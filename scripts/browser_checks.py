"""Read test conditions through DevTools without page-side eval polling.

Playwright's native wait_for_function creates an eval-based polling function in
the page. A strict CSP correctly blocks that. These test-only checks keep the
production CSP enabled and read values via the browser inspector instead.
"""
import time
from playwright.sync_api import Page, Frame, TimeoutError as BrowserTimeout

def install_csp_wait():
    if getattr(Page, '_eclipse_csp_wait', False):
        return

    def wait(target, expression, *, arg=None, timeout=None, polling=None):
        limit = 30000 if timeout is None else timeout
        deadline = None if limit == 0 else time.monotonic() + limit / 1000
        interval = polling if isinstance(polling, (int, float)) else 50
        while deadline is None or time.monotonic() < deadline:
            handle = target.evaluate_handle(expression, arg)
            if target.evaluate('(value)=>Boolean(value)', handle):
                return handle
            handle.dispose()
            target.wait_for_timeout(max(5, interval))
        raise BrowserTimeout(f'Timed out waiting for inspector condition: {expression[:160]}')

    Page.wait_for_function = wait
    Frame.wait_for_function = wait
    Page._eclipse_csp_wait = True
