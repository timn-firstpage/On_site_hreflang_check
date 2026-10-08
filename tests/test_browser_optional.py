"""Optional integration tests: install requirements-browser.txt and Chromium first."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import sys
import tempfile
from threading import Thread
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from inspect_homepage import Fetcher
from render_homepage import render


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'''<html lang="en"><body><p id="text">English version</p>
        <select id="language" onchange="document.documentElement.lang=this.value;document.getElementById('text').textContent=this.value==='zh'?'Chinese version':'English version'">
        <option value="en">English</option><option value="zh">Chinese</option></select>
        </body></html>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@unittest.skipUnless(importlib.util.find_spec('playwright'), 'Optional Playwright not installed')
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_same_url_language_change_is_observed(self):
        run_root = ROOT / 'runs'
        run_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=run_root) as tmp:
            f = Fetcher(['127.0.0.1'], 10)
            result = render(f'http://127.0.0.1:{self.server.server_port}/', f, '#language', 'zh', Path(tmp))
            self.assertEqual(result['state'], 'rendered', result)
            self.assertEqual(result['switch'], 'observed_change')
            self.assertFalse(result['url_changed'])
            self.assertTrue(result['lang_changed'])
            self.assertTrue(result['text_changed'])
            self.assertEqual(result['after']['html_lang'], 'zh')
            self.assertGreater(f.used, 0)
            self.assertTrue((Path(tmp) / 'rendered-after.html').exists())


if __name__ == '__main__':
    unittest.main()
