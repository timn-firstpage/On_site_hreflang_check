from email.message import Message
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_homepage import Fetcher, collect, parse_page, structure

ROOT = Path(__file__).resolve().parents[1]


class Response(BytesIO):
    def __init__(self, status, body='', **headers):
        super().__init__(body.encode())
        self.code = status
        self.headers = Message()
        self.headers['Content-Type'] = 'text/html; charset=utf-8'
        for key, value in headers.items():
            self.headers[key] = value


class Opener:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def open(self, request, timeout):
        self.calls.append(request.full_url)
        return next(self.responses)


class HomepageTests(unittest.TestCase):
    def test_nested_link_and_header_alternates(self):
        page = parse_page('<html lang="en"><a href="/zh/"><span>中文</span></a><link rel="alternate" hreflang="zh" href="/zh/"></html>', 'https://example.com/', '<https://example.com/en/>; rel="alternate"; hreflang="en"')
        self.assertEqual(page['controls'][0]['url'], 'https://example.com/zh/')
        self.assertEqual(len(page['alternates']), 2)
        self.assertEqual(page['controls'][0]['behavior'], 'not_tested')

    def test_select_codes_are_not_fabricated_urls(self):
        p = parse_page('<select name="language"><option value="zh">中文</option><option value="/en/">English</option></select>', 'https://example.com/')
        options = [c for c in p['controls'] if c['tag'] == 'option']
        self.assertIsNone(options[0]['url'])
        self.assertEqual(options[1]['url'], 'https://example.com/en/')

    def test_region_label_and_accessibility_label(self):
        p = parse_page('<a href="https://example.com.hk/">Hong Kong</a><button aria-label="中文"></button>', 'https://example.com/')
        self.assertEqual(len(p['controls']), 2)
        self.assertEqual(p['controls'][0]['url'], 'https://example.com.hk/')

    def test_literal_js_destination_and_no_js_execution(self):
        p = parse_page('<button onclick="location.href=\'/zh/\'">中文</button><script>window.locale="fr"</script>', 'https://example.com/')
        self.assertEqual(len(p['controls']), 1)
        self.assertEqual(p['controls'][0]['url'], 'https://example.com/zh/')
        self.assertNotIn('window.locale', p['text_sample'])

    def test_only_lang_is_not_multilingual_evidence(self):
        p = parse_page('<html lang="en"><p>Welcome</p></html>', 'https://example.com/')
        self.assertEqual(p['controls'], [])
        self.assertEqual(p['alternates'], [])

    def test_structure_works_without_clicking(self):
        home = 'https://example.com/'
        for url, expected in [('https://example.com/?lang=en', 'parameter'),
                              ('https://example.com/en/?utm_source=x', 'subdirectory'),
                              ('https://zh.example.com/', 'subdomain'),
                              ('https://example.com/?utm_source=en', 'unknown'),
                              ('https://example.com/', 'default_root')]:
            self.assertEqual(structure(url, home), expected)

    def test_offline_does_not_fetch(self):
        f = Fetcher(['example.com'], 0)
        p = collect('https://example.com/', f, html='<a href="/zh/">中文</a>')
        self.assertEqual(f.used, 0)
        self.assertEqual(p['unchecked_targets'], ['https://example.com/zh/'])

    def test_redirect_scope_and_budget(self):
        f = Fetcher(['example.com'], 2)
        f.opener = Opener([Response(302, Location='https://other.example/zh/')])
        self.assertEqual(f.fetch('https://example.com/')['error'], 'host_out_of_scope')
        self.assertEqual(f.used, 1)
        f = Fetcher(['example.com'], 1)
        f.opener = Opener([Response(302, Location='/zh/')])
        self.assertEqual(f.fetch('https://example.com/')['error'], 'request_budget_exhausted')
        self.assertEqual(len(f.opener.calls), 1)

    def test_target_response_and_limit(self):
        f = Fetcher(['example.com'], 4)
        f.opener = Opener([Response(200, '<a href="/zh/">中文</a><a href="/en/">English</a>'), Response(404, 'Not found')])
        result = collect('https://example.com/', f, max_targets=1)
        self.assertEqual(result['targets'][0]['status'], 404)
        self.assertEqual(result['unchecked_targets'], ['https://example.com/en/'])
        self.assertEqual(f.used, 2)

    def test_offline_cli_and_live_disabled(self):
        run_root = ROOT / 'runs'
        run_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=run_root) as tmp:
            tmp = Path(tmp)
            config = tmp / 'config.json'
            config.write_text(json.dumps({'site': {'start_url': 'https://example.com/'}, 'checks': {'live_checks': False}}))
            html = tmp / 'home.html'
            html.write_text('<a href="/en/">English</a>')
            cmd = [sys.executable, str(ROOT / 'scripts/inspect_homepage.py'), '--config', str(config), '--output-dir', str(tmp / 'out')]
            run = subprocess.run(cmd + ['--html', str(html)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((tmp / 'out/homepage-evidence.json').read_text(encoding='utf-8'))
            self.assertEqual(data['requests_used'], 0)
            run = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('Live checks disabled', run.stderr)


if __name__ == '__main__':
    unittest.main()
