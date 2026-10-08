"""Optional programmatic Chromium evidence. No model vision/desktop control."""
from inspect_homepage import parse_page


def render(url, fetcher, selector, option_value, output_dir):
    result = {'state': 'unavailable', 'blocked': [], 'switch': 'not_tested'}
    if fetcher.rate_limit:
        result.update(state='skipped_after_429', rate_limit=fetcher.rate_limit)
        return result
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        result['reason'] = 'Playwright is not installed; use static evidence or install requirements-browser.txt and Chromium.'
        return result
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, timeout=fetcher.timeout * 1000)
            try:
                context = browser.new_context(service_workers='block', accept_downloads=False)
                def route_request(route):
                    request = route.request
                    previous, hops = request.redirected_from, 0
                    while previous:
                        hops += 1
                        previous = previous.redirected_from
                    error = 'method_or_redirect_limit' if request.method != 'GET' or hops > fetcher.max_redirects else fetcher.acquire(request.url)
                    if error:
                        result['blocked'].append({'url': request.url, 'method': request.method, 'reason': error})
                        route.abort()
                        return
                    try:
                        # Disable automatic redirect following here; browser redirect hops get routed again.
                        response = route.fetch(max_redirects=0, timeout=fetcher.timeout * 1000)
                        if response.status == 429:
                            fetcher.record_429(request.url, response.headers.get('retry-after'))
                        route.fulfill(response=response)
                    except Exception as exc:
                        result['blocked'].append({'url': request.url, 'reason': str(exc)})
                        route.abort()
                context.route('**/*', route_request)
                page = context.new_page()
                page.set_default_timeout(fetcher.timeout * 1000)
                response = page.goto(url, wait_until='domcontentloaded')
                page.wait_for_timeout(1000)
                if fetcher.rate_limit:
                    result.update(state='rate_limited', rate_limit=fetcher.rate_limit)
                    return result
                before_html = page.content()
                before = parse_page(before_html, page.url)
                (output_dir / 'rendered-before.html').write_text(before_html, encoding='utf-8')
                result.update(state='rendered', response_status=response.status if response else None, before=before)
                if selector:
                    control = page.locator(selector)
                    if control.count() != 1:
                        raise ValueError('Selector must identify exactly one inspected language/region control')
                    result['control'] = {'selector': selector, 'text': control.inner_text(), 'visible': control.is_visible()}
                    # Caller must choose a language/region control from actual evidence.
                    if option_value is not None:
                        control.select_option(value=option_value)
                    else:
                        control.click()
                    page.wait_for_timeout(1500)
                    if fetcher.rate_limit:
                        result.update(state='rate_limited', rate_limit=fetcher.rate_limit, switch='not_verified_due_to_429')
                        return result
                    after_html = page.content()
                    after = parse_page(after_html, page.url)
                    (output_dir / 'rendered-after.html').write_text(after_html, encoding='utf-8')
                    result.update(after=after, switch='observed_change' if before != after else 'no_observed_change',
                                  url_changed=before['url'] != after['url'],
                                  lang_changed=before['html_lang'] != after['html_lang'],
                                  text_changed=before['text_sample'] != after['text_sample'])
                    result['interpretation'] = 'Review actual locale content. Change alone is not success; no change in this bounded wait is not proof of failure. Popups, menu-only clicks or blocked resources require a precise limitation.'
            finally:
                browser.close()
    except Exception as exc:
        result.update(state='incomplete', reason=str(exc))
        if fetcher.rate_limit:
            result.update(state='rate_limited', rate_limit=fetcher.rate_limit)
    return result
