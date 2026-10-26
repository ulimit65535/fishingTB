"""Exercise search, forum, post and image screens without account credentials."""
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from PIL import Image
from textual.widgets import Static
from fishingtb import config
from fishingtb.models import ThreadItem, PostItem, CommentItem
from fishingtb.ui.app import FishingApp
from fishingtb.ui.screens.forum import ForumScreen
from fishingtb.ui.screens.thread_list import ThreadListScreen
from fishingtb.ui.screens.thread_detail import ThreadDetailScreen
from fishingtb.ui.screens.image_preview import ImagePreviewScreen


async def main():
    thread = ThreadItem(1, '[red]中文帖子[/red]', '', 3, 5, 1700000000, '作者', 'python')
    post = PostItem(1, 1, '作者', '中文内容 [red]应原样显示[/red]', image_urls=['https://imgsrc.baidu.com/test.png'],
                    comments=[CommentItem('访客', '测试评论', author_tags=['楼主'])])
    with (
        tempfile.TemporaryDirectory() as directory,
        patch.object(config, 'CONFIG_PATH', Path(directory) / 'config.yaml'),
        patch('fishingtb.ui.screens.forum.get_followed_forums', AsyncMock(return_value=[])),
        patch('fishingtb.ui.screens.forum.get_follow_feed', AsyncMock(return_value=[])),
        patch('fishingtb.ui.screens.thread_list.get_forum_threads', AsyncMock(return_value=([thread], True))),
        patch('fishingtb.ui.screens.thread_detail.get_thread_posts', AsyncMock(return_value=([post], True, thread.title))),
        patch('fishingtb.ui.screens.thread_detail.warm_image_bytes', AsyncMock()),
        patch('fishingtb.ui.screens.image_preview.fetch_image', AsyncMock(return_value=Image.new('RGB', (80, 80), 'white'))),
        patch('fishingtb.ui.screens.image_preview.warm_image_bytes', AsyncMock()),
    ):
        app = FishingApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await app.push_screen(ForumScreen())
            await pilot.pause()
            await pilot.click('#tab-search')
            await pilot.pause()
            await pilot.click('#forum-input')
            await pilot.press('q')
            assert app.screen.query_one('#forum-input').value == 'q', 'q must be typeable in search'
            app.screen.query_one('#forum-input').value = 'python'
            await pilot.press('enter')
            await pilot.pause()
            assert isinstance(app.screen, ThreadListScreen)
            await pilot.click('#btn-next')
            await pilot.pause()
            assert app.screen.page == 2
            await pilot.click('#btn-sort')
            await pilot.pause()
            assert app.screen.page == 1
            await pilot.click('#thread-list ListItem')
            await pilot.pause()
            assert isinstance(app.screen, ThreadDetailScreen), type(app.screen)
            assert len(app.screen.posts) == 1
            await pilot.click('#btn-all-imgs')
            await pilot.pause()
            assert isinstance(app.screen, ImagePreviewScreen)
            await pilot.pause(0.3)
            assert '已加载' in str(app.screen.query_one('#status', Static).content)
            await pilot.press('escape')
            await pilot.pause()
            assert isinstance(app.screen, ThreadDetailScreen)
    print('workflow ok: search q, forum paging/sort, posts/comments, image preview')


if __name__ == '__main__':
    asyncio.run(main())
