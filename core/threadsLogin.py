import asyncio
import base64
from typing import Optional
from playwright.async_api import Page
from utils.logger import logger


class ThreadsLoginAgent:

    THREADS_LOGIN_URL = "https://www.threads.net/login"
    THREADS_HOME_URL = "https://www.threads.net/"

    USERNAME_SELECTORS = [
        'input[name="username"]',
        'input[aria-label*="username" i]',
        'input[aria-label*="логин" i]',
        'input[placeholder*="username" i]',
        'input[type="text"]',
    ]

    PASSWORD_SELECTORS = [
        'input[name="password"]',
        'input[aria-label*="password" i]',
        'input[aria-label*="пароль" i]',
        'input[type="password"]',
    ]

    SUBMIT_SELECTORS = [
        'button[type="submit"]',
        'div[role="button"]:has-text("Log in")',
        'div[role="button"]:has-text("Войти")',
        'button:has-text("Log in")',
        'button:has-text("Войти")',
    ]

    TWOFa_SELECTORS = [
        'input[name="security_code"]',
        'input[aria-label*="security" i]',
        'input[aria-label*="код" i]',
        'input[placeholder*="code" i]',
        'input[inputmode="numeric"]',
    ]

    def __init__(self, page: Page):
        self.page = page
        self._screenshotCallback = None

    def setScreenshotCallback(self, callback):
        self._screenshotCallback = callback

    async def _takeScreenshot(self, caption: str = "") -> Optional[bytes]:
        try:
            screenshot = await self.page.screenshot()
            if self._screenshotCallback:
                await self._screenshotCallback(screenshot, caption)
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    async def _findElement(self, selectors: list, timeout: int = 3000) -> Optional[object]:
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=timeout)
                if element and await element.is_visible():
                    logger.info(f"Found element: {selector}")
                    return element
            except:
                continue
        return None

    async def _fillField(self, selector: str, text: str) -> bool:
        try:
            element = await self.page.wait_for_selector(selector, timeout=3000)
            if element:
                await element.fill(text)
                return True
        except Exception as e:
            logger.error(f"Fill error for {selector}: {e}")
        return False

    async def _clickSubmit(self) -> bool:
        for selector in self.SUBMIT_SELECTORS:
            try:
                button = await self.page.wait_for_selector(selector, timeout=2000)
                if button and await button.is_visible():
                    await button.click()
                    logger.info(f"Clicked submit: {selector}")
                    return True
            except:
                continue

        try:
            await self.page.keyboard.press("Enter")
            logger.info("Pressed Enter as fallback")
            return True
        except:
            return False

    async def _checkLoginStatus(self) -> str:
        try:
            await asyncio.sleep(0.5)
            currentUrl = self.page.url

            errorElements = await self.page.query_selector_all('[role="alert"]')
            for elem in errorElements:
                text = await elem.text_content()
                if text and len(text) > 5:
                    return f"error:{text.strip()}"

            if "checkpoint" in currentUrl or "challenge" in currentUrl:
                return "challenge"

            twoFAElement = await self._findElement(self.TWOFa_SELECTORS, timeout=1000)
            if twoFAElement:
                return "needs_2fa"

            loginSelectors = [
                'a[href*="login"]',
                'button:has-text("Log in")',
                'button:has-text("Войти")',
                'a:has-text("Log in")',
                'a:has-text("Войти")',
                'input[name="username"]',
                'input[name="password"]',
            ]

            for selector in loginSelectors:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"Found login element: {selector}")
                    return "not_logged_in"

            loggedIndicators = [
                '[aria-label="Create"]',
                '[aria-label="Создать"]',
                '[aria-label*="Profile" i]',
                '[aria-label*="профиль" i]',
                'a[href*="/@"]',
                'div[data-visualcompletion="ignore"]',
            ]

            for selector in loggedIndicators:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"Found logged-in indicator: {selector}")
                    return "logged_in"

            if "threads.net" in currentUrl and "/login" not in currentUrl:
                logger.info("On Threads main page without login form, assuming logged in")
                return "logged_in"

            return "unknown"

        except Exception as e:
            logger.error(f"Login status check error: {e}")
            return "unknown"

    async def navigateToLogin(self) -> bool:
        try:
            logger.info(f"Navigating to {self.THREADS_LOGIN_URL}")
            await self.page.goto(self.THREADS_LOGIN_URL, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(1.5)
            await self._takeScreenshot("Страница входа Threads")
            return True
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False

    async def isLoggedIn(self) -> bool:
        try:
            await self.page.goto(self.THREADS_HOME_URL, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(1.5)

            status = await self._checkLoginStatus()
            if status == "logged_in":
                await self._takeScreenshot("Уже авторизован в Threads")
                return True
            return False
        except:
            return False

    async def fillUsername(self, username: str) -> bool:
        for selector in self.USERNAME_SELECTORS:
            try:
                if await self._fillField(selector, username):
                    logger.info(f"Username filled: {username[:3]}***")
                    return True
            except:
                continue

        logger.error("Could not find username field")
        return False

    async def fillPassword(self, password: str) -> bool:
        for selector in self.PASSWORD_SELECTORS:
            try:
                if await self._fillField(selector, password):
                    logger.info("Password filled")
                    return True
            except:
                continue

        logger.error("Could not find password field")
        return False

    async def submitLogin(self) -> str:
        if not await self._clickSubmit():
            await self._takeScreenshot("Ошибка: не удалось нажать кнопку входа")
            return "submit_failed"

        logger.info("Waiting for login response...")

        for i in range(20):
            await asyncio.sleep(0.2)
            status = await self._checkLoginStatus()

            if status in ["logged_in", "needs_2fa", "challenge"]:
                await self._takeScreenshot(f"Статус после входа: {status}")
                return status

            if status.startswith("error:"):
                await self._takeScreenshot(f"Ошибка: {status}")
                return status

        status = await self._checkLoginStatus()
        await self._takeScreenshot(f"Статус после входа: {status}")
        return status

    async def needs2FA(self) -> bool:
        element = await self._findElement(self.TWOFa_SELECTORS, timeout=2000)
        return element is not None

    async def fill2FA(self, code: str) -> str:
        for selector in self.TWOFa_SELECTORS:
            try:
                if await self._fillField(selector, code):
                    logger.info("2FA code filled")
                    await asyncio.sleep(0.3)
                    await self._clickSubmit()

                    for i in range(15):
                        await asyncio.sleep(0.2)
                        status = await self._checkLoginStatus()
                        if status in ["logged_in", "challenge"]:
                            await self._takeScreenshot(f"Статус после 2FA: {status}")
                            return status
                        if status.startswith("error:"):
                            await self._takeScreenshot(f"Ошибка 2FA: {status}")
                            return status

                    status = await self._checkLoginStatus()
                    await self._takeScreenshot(f"Статус после 2FA: {status}")
                    return status
            except:
                continue

        return "2fa_failed"

    async def fullLogin(self, username: str, password: str, onStatus: callable = None) -> dict:
        result = {"success": False, "status": "", "needs2FA": False}

        async def report(msg):
            if onStatus:
                await onStatus(msg)

        try:
            await report("Проверяю текущий статус...")
            if await self.isLoggedIn():
                result["success"] = True
                result["status"] = "already_logged_in"
                return result

            await report("Открываю страницу входа...")
            if not await self.navigateToLogin():
                result["status"] = "navigation_failed"
                return result

            await report("Ввожу имя пользователя...")
            if not await self.fillUsername(username):
                result["status"] = "username_field_not_found"
                return result

            await report("Ввожу пароль...")
            if not await self.fillPassword(password):
                result["status"] = "password_field_not_found"
                return result

            await report("Отправляю форму входа...")
            status = await self.submitLogin()

            if status == "needs_2fa" or await self.needs2FA():
                result["needs2FA"] = True
                result["status"] = "needs_2fa"
                await report("Требуется код двухфакторной аутентификации!")
                return result

            if status.startswith("error:"):
                result["status"] = status
                await report(f"Ошибка входа: {status}")
                return result

            if status == "logged_in":
                result["success"] = True
                result["status"] = "logged_in"
                await report("Успешная авторизация!")
                return result

            result["status"] = status
            return result

        except Exception as e:
            logger.error(f"Full login error: {e}")
            result["status"] = f"error:{e}"
            return result
