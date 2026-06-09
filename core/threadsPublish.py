import asyncio
from typing import Optional
from pathlib import Path
from playwright.async_api import Page, Browser
from utils.logger import logger


class ThreadsPublishAgent:

    def __init__(self, browser: Browser):
        self.browser = browser
        self.page = None
        self._screenshotCallback = None

    def setScreenshotCallback(self, callback):
        self._screenshotCallback = callback

    async def _takeScreenshot(self, caption: str = "") -> Optional[bytes]:
        try:
            if not self.page:
                return None
            screenshot = await self.page.screenshot()
            if self._screenshotCallback:
                await self._screenshotCallback(screenshot, caption)
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    async def _getOrCreatePage(self) -> Page:
        all_pages = []
        for context in self.browser.contexts:
            for page in context.pages:
                all_pages.append(page.url)
        logger.info(f"Found {len(all_pages)} tabs: {all_pages}")

        for context in self.browser.contexts:
            for page in context.pages:
                url = page.url.lower()
                if 'threads.net' in url or 'threads' in url:
                    logger.info(f"Reusing existing Threads page: {page.url}")
                    self.page = page
                    return page

        for context in self.browser.contexts:
            for page in context.pages:
                url = page.url
                if url and url != 'about:blank' and not url.startswith('chrome://') and not url.startswith('edge://'):
                    logger.info(f"Reusing existing page: {url}")
                    self.page = page
                    return page

        logger.warning("No open tabs found, creating new page")
        context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
        self.page = await context.new_page()
        logger.info("Created new page")
        return self.page

    async def _findCreateButton(self):
        selectors = ['[aria-label="Создать"]', '[aria-label="Create"]']
        for sel in selectors:
            try:
                el = await self.page.wait_for_selector(sel, timeout=3000)
                if el and await el.is_visible():
                    logger.info(f"Create button found: {sel}")
                    return el
            except:
                continue

        try:
            btn = await self.page.evaluate_handle('''() => {
                const svgs = document.querySelectorAll('svg');
                for (const svg of svgs) {
                    const label = (svg.getAttribute('aria-label') || '').toLowerCase();
                    if (label.includes('creat') || label.includes('оздать')) {
                        const parent = svg.closest('[role="button"]') || svg.parentElement;
                        if (parent && parent.offsetParent !== null) return parent;
                    }
                }
                return null;
            }''')
            if btn and await btn.evaluate('el => el !== null && el.offsetParent !== null'):
                logger.info("Create button found via JS SVG")
                return btn
        except:
            pass

        return None

    async def _findTextareaInModal(self):
        selectors = [
            '[role="dialog"] [role="textbox"]',
            '[role="dialog"] [contenteditable="true"]',
            '[role="dialog"] div[aria-multiline="true"]',
            '[role="dialog"] textarea',
            '[role="textbox"]',
            '[contenteditable="true"]',
            'div[aria-multiline="true"]',
        ]
        for sel in selectors:
            try:
                el = await self.page.wait_for_selector(sel, timeout=2000)
                if el and await el.is_visible():
                    logger.info(f"Textarea found: {sel}")
                    return el
            except:
                continue
        return None

    async def _findPostButtonInModal(self):
        try:
            result = await self.page.evaluate_handle('''() => {
                const keywords = ['post', 'опубликовать', 'publicar', 'publier', '投稿', '게시'];

                const dialog = document.querySelector('[role="dialog"]');
                if (dialog) {
                    const btns = dialog.querySelectorAll('div[role="button"], button, [role="button"]');
                    for (const el of btns) {
                        if (el.offsetParent === null) continue;
                        const text = (el.textContent || '').trim().toLowerCase();
                        const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                        if (keywords.some(kw => text.includes(kw) || aria.includes(kw))) {
                            return el;
                        }
                    }
                }

                const textbox = document.querySelector('[role="textbox"], [contenteditable="true"]');
                if (textbox) {
                    let container = textbox.parentElement;
                    for (let i = 0; i < 15 && container; i++) {
                        const btns = container.querySelectorAll('div[role="button"], button');
                        for (const btn of btns) {
                            if (btn.offsetParent === null) continue;
                            const text = (btn.textContent || '').trim().toLowerCase();
                            const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                            const combined = text + ' ' + aria;
                            if (text.length > 0 && text.length < 20 && keywords.some(kw => combined.includes(kw))) {
                                return btn;
                            }
                        }
                        container = container.parentElement;
                    }
                }

                const allBtns = document.querySelectorAll('div[role="button"], button');
                for (const el of allBtns) {
                    if (el.offsetParent === null) continue;
                    const rect = el.getBoundingClientRect();
                    const text = (el.textContent || '').trim().toLowerCase();
                    const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                    if (text.length > 0 && text.length < 15 && rect.y < 200 && rect.x > 500) {
                        if (keywords.some(kw => text.includes(kw) || aria.includes(kw))) {
                            return el;
                        }
                    }
                }

                return null;
            }''')

            if result and await result.evaluate('el => el !== null'):
                label = await result.evaluate('el => (el.textContent || "").trim()')
                logger.info(f"Found post button in modal: '{label}'")
                return result
        except Exception as e:
            logger.warning(f"Modal button search error: {e}")

        return None

    async def _waitForModalClose(self, timeoutMs: int = 8000) -> bool:
        start = asyncio.get_event_loop().time()
        timeout = timeoutMs / 1000

        while asyncio.get_event_loop().time() - start < timeout:
            textarea = await self._findTextareaInModal()
            if textarea is None:
                logger.info("Modal closed - post likely published")
                await asyncio.sleep(1)
                return True
            await asyncio.sleep(0.5)

        logger.warning("Modal did not close within timeout")
        return False

    async def _uploadImage(self, imagePath: str) -> bool:
        if not Path(imagePath).exists():
            logger.error(f"Image file not found: {imagePath}")
            return False

        logger.info(f"Looking for image upload button for: {imagePath}")

        try:
            result = await self.page.evaluate_handle('''() => {
                const fileInputs = document.querySelectorAll('input[type="file"]');
                for (const input of fileInputs) {
                    if (input.offsetParent !== null || input.closest('[role="dialog"]')) {
                        return input;
                    }
                }

                const keywords = ['image', 'photo', 'picture', 'изображение', 'фото', 'картинка'];
                const buttons = document.querySelectorAll('[role="button"], button, [aria-label]');

                for (const el of buttons) {
                    const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                    const title = (el.getAttribute('title') || '').toLowerCase();
                    const text = (el.textContent || '').trim().toLowerCase();

                    if (keywords.some(kw => aria.includes(kw) || title.includes(kw) || text.includes(kw))) {
                        return el;
                    }
                }

                return null;
            }''')

            if result and await result.evaluate('el => el !== null'):
                element_type = await result.evaluate('el => el.tagName.toLowerCase()')

                if element_type == 'input':
                    logger.info("Found file input, uploading directly...")
                    await result.set_input_files(imagePath)
                    await asyncio.sleep(2)
                    return True
                else:
                    logger.info(f"Found upload button: {element_type}")
                    await result.click()
                    await asyncio.sleep(1)

                    file_input = await self.page.evaluate_handle('''() => {
                        const inputs = document.querySelectorAll('input[type="file"]');
                        return inputs.length > 0 ? inputs[0] : null;
                    }''')

                    if file_input and await file_input.evaluate('el => el !== null'):
                        logger.info("Found file input after button click, uploading...")
                        await file_input.set_input_files(imagePath)
                        await asyncio.sleep(2)
                        return True

        except Exception as e:
            logger.error(f"Upload strategy 1 failed: {e}")

        try:
            file_input = await self.page.query_selector('input[type="file"]')
            if file_input:
                logger.info("Found file input via query_selector")
                await file_input.set_input_files(imagePath)
                await asyncio.sleep(2)
                return True
        except Exception as e:
            logger.error(f"Upload strategy 2 failed: {e}")

        try:
            dialog = await self.page.query_selector('[role="dialog"]')
            if dialog:
                file_input = await dialog.query_selector('input[type="file"]')
                if file_input:
                    logger.info("Found file input in dialog")
                    await file_input.set_input_files(imagePath)
                    await asyncio.sleep(2)
                    return True
        except Exception as e:
            logger.error(f"Upload strategy 3 failed: {e}")

        logger.error("Could not find image upload mechanism")
        await self._takeScreenshot("Не удалось найти кнопку загрузки изображения")
        return False

    async def publish(self, content: str, imagePath: Optional[str] = None) -> bool:
        try:
            self.page = await self._getOrCreatePage()

            if 'threads.net' not in self.page.url:
                logger.info(f"Navigating to Threads: {self.page.url}")
                await self.page.goto('https://www.threads.net/', wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(1)
            else:
                logger.info(f"Already on Threads: {self.page.url}")

            if "/login" in self.page.url:
                logger.error("Not logged in")
                await self._takeScreenshot("Не авторизован в Threads")
                return False

            existingTextarea = await self._findTextareaInModal()
            if existingTextarea:
                logger.info("Modal already open, closing it first...")
                await self.page.keyboard.press("Escape")
                await asyncio.sleep(0.5)

            logger.info("Looking for create button...")
            createBtn = await self._findCreateButton()
            if not createBtn:
                logger.error("Create button not found")
                await self._takeScreenshot("Кнопка 'Создать' не найдена")
                return False

            logger.info("Clicking create button...")
            await createBtn.click()
            await asyncio.sleep(1)

            logger.info("Waiting for modal with textarea...")
            textarea = None
            for attempt in range(10):
                textarea = await self._findTextareaInModal()
                if textarea:
                    break
                await asyncio.sleep(0.3)

            if not textarea:
                logger.error("Textarea not found in modal")
                await self._takeScreenshot("Поле ввода не появилось")
                return False

            if imagePath:
                logger.info(f"Uploading image: {imagePath}")
                await self._uploadImage(imagePath)
                await asyncio.sleep(1)

            logger.info("Filling post content...")
            await textarea.click()
            try:
                await textarea.fill(content)
            except Exception as fillErr:
                logger.info(f"fill() failed ({fillErr}), trying keyboard.type")
                await self.page.keyboard.type(content, delay=5)
            await asyncio.sleep(0.5)

            logger.info("Looking for post button inside modal...")
            postBtn = await self._findPostButtonInModal()
            if not postBtn:
                logger.error("Post button not found inside modal")
                await self._takeScreenshot("Кнопка 'Опубликовать' не найдена в модалке")

                try:
                    allBtns = await self.page.evaluate('''() => {
                        const els = document.querySelectorAll('div[role="button"], button');
                        return Array.from(els)
                            .filter(e => e.offsetParent !== null)
                            .map(e => ({
                                tag: e.tagName,
                                text: (e.textContent || '').trim().substring(0, 50),
                                ariaLabel: e.getAttribute('aria-label'),
                                rect: (() => { const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; })()
                            }));
                    }''')
                    logger.info(f"ALL visible buttons: {allBtns}")
                except Exception as dbgErr:
                    logger.error(f"Debug error: {dbgErr}")
                return False

            logger.info("Clicking post button...")
            try:
                await postBtn.click()
            except Exception as clickErr:
                logger.warning(f"Click failed: {clickErr}, trying JS click")
                await postBtn.evaluate('el => el.click()')

            logger.info("Waiting for modal to close...")
            published = await self._waitForModalClose(timeoutMs=10000)

            if published:
                await self._takeScreenshot("Пост опубликован!")
                logger.success("Post published successfully")
                return True
            else:
                await self._takeScreenshot("Модальное окно не закрылось")
                logger.error("Post was not published (modal still open)")
                return False

        except Exception as e:
            logger.error(f"Publish error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await self._takeScreenshot(f"Ошибка: {e}")
            return False
