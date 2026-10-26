"""Verified HTTPS transport for the pinned aiotieba version.

aiotieba 4.8.2 disables certificate verification in both its connector and
individual requests. Keep this adaptation local to this application's client.
"""

import aiohttp
import aiotieba
from aiotieba.core.net import NetCore
from fishingtb.tls import verified_context


class VerifiedNetCore(NetCore):
    async def req2res(self, request, read_until_eof=True):
        host = request.url.host or ""
        if request.url.scheme not in ("http", "https") or not (
            host == "baidu.com" or host.endswith(".baidu.com")
        ):
            raise ValueError("Refusing credentials outside Baidu HTTPS endpoints")
        if request.url.port not in (80, 443):
            raise ValueError("Refusing nonstandard Baidu API port")
        if request.url.scheme == "http":
            request.url = request.url.with_scheme("https").with_port(None)
            request.original_url = request.url
        # Requests are constructed by aiotieba with ssl=False. aiohttp consults
        # this field when choosing the connector's certificate-verifying context.
        request._ssl = True
        return await super().req2res(request, read_until_eof)


class VerifiedClient(aiotieba.Client):
    async def __aenter__(self):
        await super().__aenter__()
        await self._connector.close()
        self._connector = aiohttp.TCPConnector(
            ssl=verified_context(), limit=12, ttl_dns_cache=300
        )
        self._http_core.net_core = VerifiedNetCore(
            self._connector, self._proxy, self._timeout
        )
        return self
