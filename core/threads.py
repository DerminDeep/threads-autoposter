import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from config.settings import (
    THREADS_API_BASE, CLOAKBROWSER_CDP_URL
)
from utils.logger import logger

class ThreadsPublisher(ABC):
    @abstractmethod
    async def publish(self, content: str, imagePath: Optional[str] = None) -> Optional[str]:
        pass

class APIPublisher(ThreadsPublisher):
    def __init__(self):
        self.userId = None
        self.accessToken = None
        self.baseUrl = THREADS_API_BASE

    async def publish(self, content: str, imagePath: Optional[str] = None) -> Optional[str]:
        if not self.userId or not self.accessToken:
            from database.models import getSetting
            self.userId = await getSetting('threads_user_id')
            self.accessToken = await getSetting('threads_access_token')

            if not self.userId or not self.accessToken:
                logger.error('OAuth tokens not found. Use /login to authorize via OAuth first')
                return None

        try:
            async with httpx.AsyncClient() as client:
                containerResponse = await client.post(
                    f'{self.baseUrl}/{self.userId}/threads',
                    data={
                        'media_type': 'TEXT',
                        'text': content,
                        'access_token': self.accessToken
                    },
                    timeout=30.0
                )

                if containerResponse.status_code != 200:
                    logger.error(f'Failed to create container: {containerResponse.text}')
                    return None

                containerId = containerResponse.json().get('id')
                if not containerId:
                    logger.error('No container ID received')
                    return None

                publishResponse = await client.post(
                    f'{self.baseUrl}/{self.userId}/threads_publish',
                    data={
                        'creation_id': containerId,
                        'access_token': self.accessToken
                    },
                    timeout=30.0
                )

                if publishResponse.status_code != 200:
                    logger.error(f'Failed to publish: {publishResponse.text}')
                    return None

                postId = publishResponse.json().get('id')
                logger.success(f'Post published via API: {postId}')
                return postId

        except Exception as e:
            logger.error(f'Error publishing via API: {e}')
            return None

class BrowserPublisher(ThreadsPublisher):
    async def publish(self, content: str, imagePath: Optional[str] = None) -> Optional[str]:
        try:
            from playwright.async_api import async_playwright
            from core.browser_launcher import isBrowserRunning, launchBrowser
            from core.threadsPublish import ThreadsPublishAgent

            if not await isBrowserRunning():
                logger.info('CloakBrowser не запущен, запускаю автоматически...')
                if not await launchBrowser():
                    logger.error('Не удалось запустить CloakBrowser')
                    return None
                await asyncio.sleep(3)

            logger.info(f'Connecting to CloakBrowser: {CLOAKBROWSER_CDP_URL}')

            async with async_playwright() as p:
                try:
                    browser = await p.chromium.connect_over_cdp(CLOAKBROWSER_CDP_URL, timeout=10000)
                    logger.success('Connected to CloakBrowser')
                except Exception as e:
                    logger.error(f'Cannot connect to CloakBrowser at {CLOAKBROWSER_CDP_URL}: {e}')
                    return None

                if not browser.contexts:
                    logger.error('No browser contexts found in CloakBrowser')
                    return None

                agent = ThreadsPublishAgent(browser)
                success = await agent.publish(content, imagePath)

                if success:
                    logger.success('Post published via CloakBrowser AI agent')
                    return 'browser_post_id'
                else:
                    logger.error('AI agent failed to publish post')
                    return None

        except ImportError:
            logger.error('playwright не установлен. Выполните: pip install playwright')
            return None
        except Exception as e:
            logger.error(f'Ошибка подключения к CloakBrowser: {e}')
            import traceback
            logger.error(traceback.format_exc())
            return None

def getPublisher() -> ThreadsPublisher:
    from config.settings import PUBLISH_METHOD

    if PUBLISH_METHOD == 'browser':
        logger.info('Using BrowserPublisher (CloakBrowser)')
        return BrowserPublisher()
    else:
        logger.info('Using APIPublisher (Official API)')
        return APIPublisher()
