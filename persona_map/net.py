"""Bounded requests. Credentials never appear in reports or exception URLs."""

import ipaddress
import socket
import time
from urllib.parse import urlsplit

import requests


class BudgetExceeded(RuntimeError):
    pass


def public_url(url):
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise ValueError("Only public HTTPS URLs are supported")
    for item in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(item[4][0]).is_global:
            raise ValueError("Non-public destination blocked")
    return url


class Client:
    def __init__(self, max_requests=140, seconds=900, session=None):
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = (
            "awesome-persona-training/0.1 (+https://github.com/kavaryan/awesome-persona-training)"
        )
        self.max_requests = max_requests
        self.deadline = time.monotonic() + seconds
        self.count = 0

    def request(self, method, url, *, max_bytes=8_000_000, retries=2, **kwargs):
        public_url(url)
        for attempt in range(retries + 1):
            if self.count >= self.max_requests or time.monotonic() >= self.deadline:
                raise BudgetExceeded("Run request or time budget exhausted")
            self.count += 1
            try:
                response = self.session.request(
                    method, url, timeout=(10, 25), stream=True, allow_redirects=False, **kwargs
                )
                if response.is_redirect:
                    from urllib.parse import urljoin

                    location = urljoin(url, response.headers["Location"])
                    response.close()
                    if attempt == retries:
                        raise RuntimeError("Redirect limit reached")
                    # Never forward authorization or request bodies across hosts.
                    if urlsplit(url).netloc != urlsplit(location).netloc:
                        kwargs.pop("headers", None)
                        if method != "GET":
                            raise RuntimeError("Cross-host redirect of a write request refused")
                    public_url(location)
                    url = location
                    continue
                if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                    delay = response.headers.get("Retry-After", "")
                    response.close()
                    time.sleep(min(float(delay) if delay.isdigit() else 2**attempt, 8))
                    continue
                if not response.ok:
                    code = response.status_code
                    response.close()
                    raise RuntimeError(f"HTTP {code} from {urlsplit(url).hostname}")
                chunks, size = [], 0
                for chunk in response.iter_content(65536):
                    if time.monotonic() >= self.deadline:
                        response.close()
                        raise BudgetExceeded("Run time budget exhausted during download")
                    size += len(chunk)
                    if size > max_bytes:
                        response.close()
                        raise ValueError("Response exceeds byte limit")
                    chunks.append(chunk)
                response._content = b"".join(chunks)
                response._content_consumed = True
                response.close()
                return response
            except requests.RequestException:
                if attempt == retries:
                    raise RuntimeError(f"Network failure at {urlsplit(url).hostname}") from None
                time.sleep(2**attempt)
        raise RuntimeError("Request failed")

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def json(self, url, **kwargs):
        response = self.get(url, **kwargs)
        try:
            return response.json()
        except ValueError:
            raise ValueError(f"Non-JSON response from {urlsplit(url).hostname}") from None
