"""Only open media on the HTTPS hosts used by Baidu/Tieba."""

from urllib.parse import urlsplit, urlunsplit


def media_url(url: str) -> str:
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    domains = ("baidu.com", "bdimg.com", "bcebos.com")
    if (
        parts.scheme not in ("http", "https")
        or parts.username is not None
        or parts.password is not None
        or parts.port not in (None, 443)
        or not any(host == domain or host.endswith("." + domain) for domain in domains)
    ):
        raise ValueError("仅允许百度图片域名的 HTTPS 链接")
    return urlunsplit(("https", parts.netloc, parts.path, parts.query, ""))
