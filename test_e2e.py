#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2E test สำหรับ runkksoAi — ใช้ mock OpenAI-compatible server (ไม่ต้องมี key จริง)
รัน: python3 test_e2e.py"""
import builtins
import http.server
import json
import os
import sys
import tempfile
import threading
import unittest
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ต้อง set ก่อน import: ให้เทสต์เขียน config ใน dir ชั่วคราว ไม่ทับของแท้ผู้ใช้
os.environ["RUNKKSOAI_CONFIG_DIR"] = tempfile.mkdtemp(prefix="runkksoai-test-")
import runkksoai  # noqa: E402


TOOL_CALL_RESP = {
    "choices": [{
        "message": {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call_1",
                "type": "function",
                "function": {"name": "run_bash", "arguments": json.dumps({"command": "rm TOKEN_FILE"})},
            }],
        }
    }]
}

FINAL_RESP = {"choices": [{"message": {"role": "assistant", "content": "ลบเรียบร้อยแล้วครับ ✅"}}]}


class MockAIHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):  # เงียบๆ
        pass

    def do_POST(self):
        assert self.path.endswith("/chat/completions"), self.path
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        msgs = body["messages"]
        # ถ้าผู้ใช้เพิ่งปฏิเสธ (Denied by user) → AI ลอง rm ใหม่อีกครั้ง (ทดสอบว่าถามทุกครั้ง)
        denied = msgs and msgs[-1].get("role") == "tool" and msgs[-1]["content"].startswith("Denied")
        if denied or not any(m.get("role") == "tool" for m in msgs):
            resp = dict(TOOL_CALL_RESP)
        else:
            resp = FINAL_RESP
        if os.environ.get("CUSTOM_CMD"):
            resp = json.loads(json.dumps(TOOL_CALL_RESP).replace("rm TOKEN_FILE", os.environ["CUSTOM_CMD"]))
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class PromptRecorder:
    """แทน builtins.input แล้วจด prompt ที่โปรแกรมถามจริงๆ (input ไม่ print prompt เมื่อไม่ใช่ tty)"""
    def __init__(self, answers):
        self.answers = iter(answers)
        self.prompts = []
    def __call__(self, *a, **k):
        self.prompts.append(a[0] if a else "")
        return next(self.answers)


class E2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), MockAIHandler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_classify(self):
        allowed, reason = runkksoai.classify_command("rm -f a.txt")
        self.assertTrue(allowed)
        self.assertEqual(reason, "must_confirm")
        allowed, reason = runkksoai.classify_command("ls -la")
        self.assertEqual(reason, "normal")
        allowed, reason = runkksoai.classify_command("rm -rf /")
        self.assertFalse(allowed)
        self.assertEqual(reason, "blocked")
        allowed, reason = runkksoai.classify_command("mkfs.ext4 /dev/sda1")
        self.assertFalse(allowed)
        allowed, reason = runkksoai.classify_command("find . -name '*.tmp' -delete")
        self.assertEqual(reason, "must_confirm")

    def test_run_bash(self):
        out = runkksoai.run_bash("echo hello-runkksoAi")
        self.assertIn("hello-runkksoAi", out)

    def test_delete_confirm_yes(self):
        d = tempfile.mkdtemp()
        target = os.path.join(d, "victim.txt")
        open(target, "w").write("x")
        self.assertTrue(os.path.exists(target))
        rec = PromptRecorder(["y"])
        orig_input = builtins.input
        try:
            builtins.input = rec
            call = {"function": {"name": "run_bash",
                                 "arguments": json.dumps({"command": f"rm {target}"})}}
            result = runkksoai.execute_tool_call({"lang": "th"}, "th", call)
        finally:
            builtins.input = orig_input
        self.assertFalse(os.path.exists(target))          # ลบไปจริงหลัง y
        self.assertIn("ยืนยันการลบ", rec.prompts[0])       # ถามทุกครั้งก่อนลบ
        self.assertNotIn("ERROR", result)

    def test_delete_confirm_no(self):
        d = tempfile.mkdtemp()
        target = os.path.join(d, "victim2.txt")
        open(target, "w").write("x")
        rec = PromptRecorder(["n"])
        orig_input = builtins.input
        try:
            builtins.input = rec
            call = {"function": {"name": "run_bash",
                                 "arguments": json.dumps({"command": f"rm {target}"})}}
            result = runkksoai.execute_tool_call({"lang": "en"}, "en", call)
        finally:
            builtins.input = orig_input
        self.assertTrue(os.path.exists(target))           # ปฏิเสธ → ไฟล์อยู่ครบ
        self.assertIn("confirm? (y/n)", rec.prompts[0])
        self.assertIn("Denied by user", result)

    def test_full_loop_against_mock(self):
        # config ชี้ไปที่ mock server
        cfg = {"provider": "mock", "base_url": f"http://127.0.0.1:{self.port}/v1",
               "model": "mock-model", "api_key": "sk-mock", "lang": "en"}
        d = tempfile.mkdtemp()
        target = os.path.join(d, "TOKEN_FILE")
        open(target, "w").write("x")
        rec = PromptRecorder(["n", "y"])   # 1st: ปฏิเสธ, 2nd: ยืนยัน
        orig_input = builtins.input
        try:
            builtins.input = rec
            history = [{"role": "user", "content": "delete TOKEN_FILE please"}]
            for _ in range(8):
                resp = runkksoai.api_chat(cfg, history)
                calls, content = runkksoai.get_tool_calls(resp)
                if content:
                    final = content
                    break
                history.append({"role": "assistant", "content": None, "tool_calls": calls})
                for call in calls:
                    result = runkksoai.execute_tool_call(cfg, "en", call)
                    history.append({"role": "tool", "tool_call_id": call.get("id", ""),
                                    "content": result})
        finally:
            builtins.input = orig_input
        self.assertEqual(final, "ลบเรียบร้อยแล้วครับ ✅")     # loop จบสมบูรณ์
        self.assertEqual(len(rec.prompts), 2)               # ถาม 2 ครั้ง (n แล้ว y)
        for p in rec.prompts:
            self.assertIn("confirm? (y/n)", p)              # ← ถามยืนยันทุกครั้ง

    def test_setup_wizard_saves_config(self):
        rec = PromptRecorder(["1", "", "sk-test-123"])  # provider1, model, key (ภาษามาจาก arg)
        orig_input = builtins.input
        try:
            builtins.input = rec
            cfg = runkksoai.setup_wizard("th")
        finally:
            builtins.input = orig_input
        self.assertEqual(cfg["model"], "gpt-4o-mini")
        self.assertEqual(cfg["api_key"], "sk-test-123")
        self.assertEqual(cfg["lang"], "th")
        self.assertEqual(cfg["base_url"], "https://api.openai.com/v1")
        with open(runkksoai.CONFIG_PATH) as f:
            saved = json.load(f)
        self.assertEqual(saved, cfg)
        # prompt สำหรับกรอกโมเดลต้องแสดงถึงค่าเริ่มต้นให้ผู้ใช้แก้ได้
        self.assertIn("[gpt-4o-mini]", rec.prompts[1])


if __name__ == "__main__":
    unittest.main()
