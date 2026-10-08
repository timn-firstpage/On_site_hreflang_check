"""Bounded homepage/alternate evidence collection; no computer-use tool required."""
import argparse
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlsplit, urldefrag
from urllib.request import Request, build_opener, HTTPRedirectHandler

LOCALES = set('en zh cn hk tw sg us gb uk de fr es pt it ja jp ko kr ar ru nl pl th vi id ms tr hi bn ta he sv da fi no cs el hu ro uk ca eu au nz canada english chinese french german japanese 中文 简体 繁體 繁体 简体中文 繁體中文 香港 日本語 한국어 français deutsch español'.split())
LOCALE_KEYS = {'lang', 'language', 'locale', 'region', 'country', 'hl'}
HINT = re.compile(r'language|locale|region|country|lang[-_ ]|语言|語言|地区|地區', re.I)
LOCALE_LABEL = re.compile(r'^(?:hong kong|taiwan|singapore|united states|united kingdom|english|中文|简体中文|繁體中文|繁体中文)(?:\s*[-（(].*)?$', re.I)


def locale_token(value):
    value = value.strip().lower()
    return value in LOCALES or (bool(re.fullmatch(r'[a-z]{2,3}(?:[-_][a-z]{2,4}){1,2}', value)) and value.split('-')[0].split('_')[0] in LOCALES)


def structure(url, home):
    """Candidate structure only; the agent must confirm that this is a locale URL."""
    parts = urlsplit(url)
    if any(k.lower() in LOCALE_KEYS for k in parse_qs(parts.query)):
        return 'parameter'
    host = (parts.hostname or '').lower()
    if host and locale_token(host.split('.')[0]) and '.' in host:
        return 'subdomain'
    if any(locale_token(p) for p in parts.path.split('/') if p):
        return 'subdirectory'
    if host and len(host.split('.')[-1]) == 2 and host.split('.')[-1] not in {'io', 'ai', 'co', 'me', 'tv', 'cc'}:
        return 'cctld_candidate'
    if host == urlsplit(home).hostname and parts.path in ('', '/') and not parts.query:
        return 'default_root'
    return 'unknown'


def web_url(base, raw):
    if not raw or raw.startswith('#'):
        return None
    result = urldefrag(urljoin(base, raw))[0]
    p = urlsplit(result)
    return result if p.scheme in {'http', 'https'} and p.hostname and not p.username and not p.password else None


class PageParser(HTMLParser):
    def __init__(self, url):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.lang = ''
        self.controls = []
        self.alternates = []
        self.active = []
        self.select = None
        self.skip = 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'base' and a.get('href'):
            self.url = web_url(self.url, a['href']) or self.url
        if tag in {'script', 'style'}:
            self.skip += 1
        if tag == 'link' and 'alternate' in a.get('rel', '').lower().split() and a.get('hreflang'):
            u = web_url(self.url, a.get('href'))
            if u:
                self.alternates.append({'url': u, 'hreflang': a['hreflang'], 'source': 'html_link'})
        if tag == 'select':
            self.select = a
        if tag in {'a', 'button', 'select', 'option'}:
            node = {'tag': tag, 'attributes': a, 'text': '', 'parent_select': self.select if tag == 'option' else None}
            self.controls.append(node)
            self.active.append(node)

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.skip = max(0, self.skip - 1)
        if tag in {'a', 'button', 'select', 'option'}:
            self.active = [n for n in self.active if n['tag'] != tag]
        if tag == 'select':
            self.select = None

    def handle_data(self, text):
        if self.skip:
            return
        self.text.append(text)
        for node in self.active:
            node['text'] += text


def parse_page(html, url, link_header=''):
    parser = PageParser(url)
    parser.feed(html)
    candidates = []
    for node in parser.controls:
        a = node['attributes']
        label = ' '.join(node['text'].split())
        attrs_text = ' '.join(str(v or '') for v in a.values())
        parent_hint = ' '.join(str(v or '') for v in (node['parent_select'] or {}).values())
        raw = a.get('href') or a.get('data-url') or a.get('data-href')
        if not raw or raw.lower().startswith('javascript:') or raw == '#':
            # Extract a literal destination only. Never eval arbitrary website JS.
            match = re.search(r'(?:location(?:\.href)?\s*=\s*|location\.(?:assign|replace)\(\s*)[\'"]([^\'"]+)[\'"]', a.get('onclick', ''))
            raw = match[1] if match else raw
        # Option value="zh" is not a URL. Do not fabricate /zh from it.
        if not raw and node['tag'] == 'option' and re.match(r'^(?:https?://|/|\?|\./|\.\./)', a.get('value', '')):
            raw = a['value']
        u = web_url(parser.url, raw)
        kind = structure(u, url) if u else 'unknown'
        labels = [label, a.get('aria-label', ''), a.get('title', '')]
        if (a.get('hreflang') or any(locale_token(v) or LOCALE_LABEL.fullmatch(v.strip()) for v in labels) or HINT.search(attrs_text + ' ' + parent_hint)
                or kind in {'parameter', 'subdomain', 'subdirectory'}):
            candidates.append({'tag': node['tag'], 'label': label, 'url': u, 'structure': kind,
                               'attributes': a, 'visibility': 'not_tested',
                               'behavior': 'not_tested', 'source': 'html_control'})
    alternates = parser.alternates
    for m in re.finditer(r'<([^>]+)>\s*;([^,]+)', link_header):
        params = dict((k.lower(), (v1 or v2)) for k, v1, v2 in re.findall(r'([\w-]+)\s*=\s*(?:"([^"]*)"|([^;\s]+))', m[2]))
        u = web_url(url, m[1])
        if u and 'alternate' in params.get('rel', '').lower().split() and params.get('hreflang'):
            alternates.append({'url': u, 'hreflang': params['hreflang'], 'source': 'http_link_header'})
    return {'url': url, 'html_lang': parser.lang, 'text_sample': ' '.join(' '.join(parser.text).split())[:4000],
            'controls': candidates, 'alternates': alternates}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Fetcher:
    def __init__(self, hosts, budget, timeout=15, max_redirects=5, min_interval=2):
        self.hosts = set(hosts)
        self.remaining = budget
        self.used = 0
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.min_interval = float(min_interval)
        if not math.isfinite(self.min_interval) or self.min_interval < 0:
            raise ValueError('min_request_interval_seconds must be finite and nonnegative')
        self.last_request_at = None
        self.rate_limit = None
        self.opener = build_opener(NoRedirect())

    def acquire(self, url):
        """Shared pacing and stop state for HTTP pages, redirects and browser resources."""
        if self.rate_limit:
            return 'stopped_after_429'
        if not self.permitted(url):
            return 'host_out_of_scope'
        if self.remaining <= 0:
            return 'request_budget_exhausted'
        if self.last_request_at is not None:
            delay = self.min_interval - (time.monotonic() - self.last_request_at)
            if delay > 0:
                time.sleep(delay)
        self.last_request_at = time.monotonic()
        self.remaining -= 1
        self.used += 1
        return None

    def record_429(self, url, retry_after):
        now = datetime.now(timezone.utc)
        raw = str(retry_after or '').strip()
        valid = False
        seconds = 60
        try:
            if re.fullmatch(r'\d+', raw):
                seconds = int(raw)
            else:
                when = parsedate_to_datetime(raw)
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                seconds = max(0, math.ceil((when - now).total_seconds()))
            not_before = now + timedelta(seconds=seconds)
            valid = True
        except (TypeError, ValueError, OverflowError):
            seconds = 60
            not_before = now + timedelta(seconds=seconds)
        self.rate_limit = {'url': url, 'status': 429, 'observed_at': now.isoformat(),
                           'retry_after_raw': raw, 'retry_after_valid': valid,
                           'retry_not_before': not_before.isoformat(),
                           'suggested_wait_seconds': seconds,
                           'action': 'Stop this run. No automatic retry. Honor the server wait; if absent, the 60s suggestion is not a guarantee of recovery.'}

    def permitted(self, url):
        p = urlsplit(url)
        return p.scheme in {'http', 'https'} and p.hostname in self.hosts and not p.username and not p.password

    def fetch(self, url):
        original, chain = url, []
        for hop in range(self.max_redirects + 1):
            error = self.acquire(url)
            if error:
                return {'requested_url': original, 'url': url, 'error': error, 'redirects': chain}
            try:
                try:
                    response = self.opener.open(Request(url, headers={'User-Agent': 'OnsiteHreflangAudit/1.0', 'Accept': 'text/html'}), timeout=self.timeout)
                except HTTPError as exc:
                    response = exc
                with response:
                    status = response.code
                    if status == 429:
                        self.record_429(url, response.headers.get('Retry-After'))
                        return {'requested_url': original, 'url': url, 'status': 429,
                                'error': 'http_429', 'redirects': chain, 'rate_limit': self.rate_limit}
                    if status in {301, 302, 303, 307, 308}:
                        target = web_url(url, response.headers.get('Location'))
                        chain.append({'url': url, 'status': status, 'target': target})
                        if not target:
                            return {'requested_url': original, 'url': url, 'error': 'invalid_redirect', 'redirects': chain}
                        url = target
                        continue
                    body = response.read(2_000_001)
                    clipped = len(body) > 2_000_000
                    text = body[:2_000_000].decode(response.headers.get_content_charset() or 'utf-8', errors='replace')
                    return {'requested_url': original, 'url': url, 'status': status, 'redirects': chain,
                            'content_type': response.headers.get_content_type(), 'truncated': clipped,
                            'html': text, 'link_header': response.headers.get('Link', '')}
            except (URLError, OSError, ValueError, LookupError) as exc:
                return {'requested_url': original, 'url': url, 'error': str(exc), 'redirects': chain}
        return {'requested_url': original, 'url': url, 'error': 'redirect_limit', 'redirects': chain}


def collect(home, fetcher, max_targets=6, html=None, archive=None):
    source = fetcher.fetch(home) if html is None else {'url': home, 'html': html, 'source': 'saved_html'}
    result = {'homepage_response': {k: v for k, v in source.items() if k != 'html'}, 'targets': [], 'limitations': []}
    if 'html' not in source or source.get('content_type', 'text/html') not in {'text/html', 'application/xhtml+xml'}:
        result['limitations'].append('Homepage HTML unavailable; this does not prove a broken language switch.')
        return result
    page = parse_page(source['html'], source['url'], source.get('link_header', ''))
    if archive:
        (archive / 'homepage.html').write_text(source['html'], encoding='utf-8')
    result['homepage'] = page
    if source.get('status', 200) != 200 or source.get('truncated'):
        result['limitations'].append('Homepage response is non-200 or truncated; do not infer absent controls.')
    unique = list(dict.fromkeys([n['url'] for n in page['controls'] + page['alternates'] if n.get('url') and n['url'] != source['url']]))
    result['candidate_target_count'] = len(unique)
    result['unchecked_targets'] = unique[max_targets:] if html is None else unique
    if html is None:
        for index, target in enumerate(unique[:max_targets], 1):
            response = fetcher.fetch(target)
            entry = {k: v for k, v in response.items() if k != 'html'}
            entry['structure'] = structure(target, home)
            if 'html' in response and response.get('content_type') in {'text/html', 'application/xhtml+xml'}:
                entry['page'] = parse_page(response['html'], response['url'], response.get('link_header', ''))
                if archive:
                    filename = f'target-{index}.html'
                    (archive / filename).write_text(response['html'], encoding='utf-8')
                    entry['archive'] = filename
            result['targets'].append(entry)
    result['limitations'].append('Static route checks do not prove control visibility or JS click behavior. URL structure can be reviewed independently of a successful click.')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--html', type=Path, help='Saved homepage HTML; offline mode, no HTTP or rendering')
    ap.add_argument('--remaining-requests', type=int, default=0, help='Explicit allocation from remaining shared live budget')
    ap.add_argument('--max-targets', type=int, default=6)
    ap.add_argument('--render', action='store_true')
    ap.add_argument('--selector', help='One inspected language/region control CSS selector; never arbitrary page buttons')
    ap.add_argument('--option-value', help='For a known language select element')
    args = ap.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding='utf-8-sig'))
        if config.get('checks', {}).get('hreflang') is False:
            raise ValueError('checks.hreflang=false; this flow is disabled')
        home = config.get('site', {}).get('start_url')
        if not isinstance(home, str) or not web_url(home, home):
            raise ValueError('site.start_url must be an HTTP(S) URL')
        if not args.html and not config.get('checks', {}).get('live_checks', True):
            raise ValueError('Live checks disabled; supply --html for offline parsing')
        if args.html and (args.render or args.selector):
            raise ValueError('Offline mode cannot render or click')
        if args.selector and not args.render:
            raise ValueError('--selector requires --render')
        if args.option_value and not args.selector:
            raise ValueError('--option-value requires --selector')
        budget = config.get('budget', {})
        allocation = min(args.remaining_requests, budget.get('max_live_requests', 200))
        if allocation < 0 or args.max_targets < 0:
            raise ValueError('Request allocation and max-targets must be nonnegative')
        if not args.html and allocation == 0:
            raise ValueError('Live mode requires --remaining-requests from the shared remaining budget')
        hosts = config.get('site', {}).get('allowed_hosts') or [urlsplit(home).hostname]
        fetcher = Fetcher(hosts, allocation, budget.get('timeout_seconds', 15), budget.get('max_redirect_hops', 5),
                          budget.get('min_request_interval_seconds', 2))
        args.output_dir.mkdir(parents=True, exist_ok=False)
        html = args.html.read_text(encoding='utf-8-sig') if args.html else None
        result = collect(home, fetcher, args.max_targets, html, args.output_dir)
        if args.render:
            from render_homepage import render
            result['render'] = render(home, fetcher, args.selector, args.option_value, args.output_dir)
        result.update(created_at=datetime.now(timezone.utc).isoformat(), requests_used=fetcher.used,
                      allocation_remaining=fetcher.remaining, config_path=str(args.config.resolve()),
                      min_request_interval_seconds=fetcher.min_interval, rate_limit=fetcher.rate_limit)
        path = args.output_dir / 'homepage-evidence.json'
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(path)
    except (OSError, ValueError) as exc:
        ap.exit(1, f'Homepage inspection failed: {exc}\n')


if __name__ == '__main__':
    main()
