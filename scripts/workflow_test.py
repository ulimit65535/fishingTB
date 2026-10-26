"""Exercise search, forum, post and image screens without account credentials."""
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from PIL import Image
from rich.cells import cell_len
from textual.widgets import Button, Static
from fishingtb import config
from fishingtb.models import ThreadItem, PostItem, CommentItem
from fishingtb.ui.app import FishingApp
from fishingtb.ui.screens.forum import ForumScreen
from fishingtb.ui.screens.thread_list import ThreadListScreen
from fishingtb.ui.screens.thread_detail import ThreadDetailScreen
from fishingtb.ui.screens.image_preview import ImagePreviewScreen
from fishingtb.ui.widgets import ToolBar


def assert_toolbar_hitboxes(app):
    for toolbar in app.screen.query(ToolBar):
        for button in toolbar.query(Button):
            assert app.screen.region.contains_region(button.region), button.id
            assert toolbar.content_region.contains_region(button.region), button.id
            assert button.content_size.width >= cell_len(button.label.plain), button.id
            x, y = button.region.center
            assert app.get_widget_at(x, y)[0] is button, button.id


async def click_action(app, pilot, selector):
    button = app.screen.query_one(selector, Button)
    x, y = button.region.center
    assert app.get_widget_at(x, y)[0] is button, selector
    assert await pilot.click(offset=(x, y)), selector
    await pilot.pause()


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
            # Match a narrow side terminal, then resize without restarting.
            for width, height in ((24, 24), (120, 40), (38, 46)):
                await pilot.resize_terminal(width, height)
                await pilot.pause()
                assert_toolbar_hitboxes(app)
            await click_action(app, pilot, '#btn-next')
            assert app.screen.page == 2
            await click_action(app, pilot, '#btn-prev')
            assert app.screen.page == 1
            await click_action(app, pilot, '#btn-refresh')
            old_sort = app.screen.sort
            await click_action(app, pilot, '#btn-sort')
            assert app.screen.page == 1
            assert app.screen.sort != old_sort
            app.screen.query_one('#thread-list').index = 0
            await click_action(app, pilot, '#btn-open')
            assert isinstance(app.screen, ThreadDetailScreen), type(app.screen)
            assert len(app.screen.posts) == 1
            assert_toolbar_hitboxes(app)
            await click_action(app, pilot, '#btn-next')
            assert app.screen.page == 2
            await click_action(app, pilot, '#btn-prev')
            assert app.screen.page == 1
            await click_action(app, pilot, '#btn-refresh')
            await click_action(app, pilot, '#btn-all-imgs')
            assert isinstance(app.screen, ImagePreviewScreen)
            await pilot.pause(0.3)
            assert_toolbar_hitboxes(app)
            assert '已加载' in str(app.screen.query_one('#status', Static).content)
            await click_action(app, pilot, '#btn-close')
            assert isinstance(app.screen, ThreadDetailScreen)
            await click_action(app, pilot, '#btn-back')
            assert isinstance(app.screen, ThreadListScreen)
            await pilot.pause(0.3)
            await click_action(app, pilot, '#btn-back')
            assert isinstance(app.screen, ForumScreen)
            assert_toolbar_hitboxes(app)
    print('workflow ok: responsive toolbars at 24/38/120 columns, coordinate clicks, paging/sort/open/back, image preview')


if __name__ == '__main__':
    asyncio.run(main())
