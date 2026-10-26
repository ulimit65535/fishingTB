"""Regression checks for credential storage, media boundaries and verified TLS."""
from __future__ import annotations

import asyncio
import io
import os
import ssl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import aiohttp
from aiotieba.core.net import NetCore
from PIL import Image
from yarl import URL

from fishingtb import config
from fishingtb.media import images
from fishingtb.media.urls import media_url
from fishingtb.tls import verified_context
from fishingtb.transport import VerifiedClient, VerifiedNetCore


class SecurityTests(unittest.IsolatedAsyncioTestCase):
    def test_private_atomic_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.yaml'
            with patch.object(config, 'CONFIG_PATH', path):
                config.save_config({'bduss': 'dummy'})
                self.assertEqual(config.load_config()['bduss'], 'dummy')
                if os.name == 'posix':
                    self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                with patch.object(config.yaml, 'safe_dump', side_effect=OSError('disk full')):
                    with self.assertRaises(OSError):
                        config.save_config({'bduss': 'replacement'})
                self.assertEqual(config.load_config()['bduss'], 'dummy')
                self.assertEqual(len(list(Path(directory).iterdir())), 1)
                config.save_config({'recent_forums': 5})
                self.assertEqual(config.load_config()['recent_forums'], [])

    def test_media_urls(self):
        self.assertEqual(media_url('http://imgsrc.baidu.com/a.png'), 'https://imgsrc.baidu.com/a.png')
        for url in ('file:///etc/passwd', 'http://127.0.0.1/x', 'https://baidu.com.evil.test/x',
                    'https://evilbaidu.com/x', 'https://user:pw@baidu.com/x',
                    'https://imgsrc.baidu.com:8080/x', 'javascript:alert(1)'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                media_url(url)

    def test_decode_limits_and_resize(self):
        buffer = io.BytesIO()
        Image.new('RGB', (800, 400)).save(buffer, format='PNG')
        self.assertEqual(images._decode_and_resize(buffer.getvalue(), 720).size, (720, 360))
        with patch.object(images, 'MAX_IMAGE_PIXELS', 100), self.assertRaises(ValueError):
            images._decode_and_resize(buffer.getvalue(), 720)

    async def test_verified_transport(self):
        context = verified_context()
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        async with VerifiedClient() as client:
            core = client._http_core.net_core
            self.assertIsInstance(core, VerifiedNetCore)
            self.assertTrue(client._connector._ssl.check_hostname)
            request = aiohttp.ClientRequest('GET', URL('http://tiebac.baidu.com/test'), ssl=False)
            with patch.object(NetCore, 'req2res', new_callable=AsyncMock) as send:
                await core.req2res(request)
                self.assertEqual(request.url.scheme, 'https')
                self.assertEqual(request.url.port, 443)
                self.assertIs(request.ssl, True)
                send.assert_awaited_once()
            request = aiohttp.ClientRequest('GET', URL('https://example.com/test'), ssl=False)
            with self.assertRaises(ValueError):
                await core.req2res(request)

    async def test_download_limit_and_redirect_guard(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(images, 'CACHE_DIR', Path(directory)):
            response = MagicMock()
            response.status = 200
            response.content_length = images.MAX_DOWNLOAD_BYTES + 1
            response.__aenter__ = AsyncMock(return_value=response)
            response.__aexit__ = AsyncMock(return_value=False)
            session = MagicMock()
            session.get.return_value = response
            with patch.object(images, '_get_session', AsyncMock(return_value=session)):
                with self.assertRaises(ValueError):
                    await images._read_bytes('https://imgsrc.baidu.com/a')
                response.content_length = None
                async def chunks(_):
                    yield b'a' * 11
                response.content.iter_chunked = chunks
                with patch.object(images, 'MAX_DOWNLOAD_BYTES', 10), self.assertRaises(ValueError):
                    await images._read_bytes('https://imgsrc.baidu.com/a')
                response.status = 302
                response.headers = {'Location': 'http://127.0.0.1/private'}
                with self.assertRaises(ValueError):
                    await images._read_bytes('https://imgsrc.baidu.com/a')
                self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
