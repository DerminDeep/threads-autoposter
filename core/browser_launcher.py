import os
import subprocess
import asyncio
import httpx
from pathlib import Path
from utils.logger import logger
from config.settings import CLOAKBROWSER_CDP_URL

_browserProcess = None

CLOAKBROWSER_CLI = Path(r"C:\Users\user\AppData\Local\Programs\Python\Python312\Scripts\cloakbrowser.exe")
CLOAKBROWSER_INSTALL_DIR = Path.home() / ".cloakbrowser"
CLOAKBROWSER_GITHUB_URL = "https://github.com/CloakHQ/CloakBrowser/releases/latest/download/CloakBrowser.exe"

async def downloadCli() -> bool:
    logger.info(f"Скачиваю CloakBrowser CLI с GitHub...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                CLOAKBROWSER_GITHUB_URL,
                follow_redirects=True,
                timeout=60.0
            )

            if response.status_code == 200:
                CLOAKBROWSER_CLI.write_bytes(response.content)
                logger.success(f"CloakBrowser CLI скачан: {CLOAKBROWSER_CLI}")
                return True
            else:
                logger.error(f"Ошибка скачивания: HTTP {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"Ошибка при скачивании CloakBrowser CLI: {e}")
        return False

def findBrowserExecutable() -> str | None:
    if not CLOAKBROWSER_INSTALL_DIR.exists():
        logger.warning(f"Папка установки не найдена: {CLOAKBROWSER_INSTALL_DIR}")
        return None

    logger.info(f"Ищу браузер в: {CLOAKBROWSER_INSTALL_DIR}")

    for exe_name in ["chrome.exe", "chromium.exe"]:
        exe_path = CLOAKBROWSER_INSTALL_DIR / exe_name
        if exe_path.exists():
            logger.success(f"Найден браузер: {exe_path}")
            return str(exe_path)

    for exe in CLOAKBROWSER_INSTALL_DIR.rglob("*.exe"):
        if exe.name.lower() in ["chrome.exe", "chromium.exe"]:
            logger.success(f"Найден браузер: {exe}")
            return str(exe)

    return None

async def installBrowser() -> bool:
    if not CLOAKBROWSER_CLI.exists():
        logger.info(f"CloakBrowser CLI не найден, пытаюсь скачать...")
        if not await downloadCli():
            logger.error(f"Не удалось скачать CloakBrowser CLI")
            return False

    logger.info("Запускаю установку браузера через CloakBrowser...")

    try:
        process = await asyncio.create_subprocess_exec(
            str(CLOAKBROWSER_CLI),
            "install",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(CLOAKBROWSER_CLI.parent)
        )

        stdout, stderr = await process.communicate()

        if stdout:
            logger.info(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
        if stderr:
            logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")

        if process.returncode == 0:
            logger.success("Браузер успешно установлен")
            return True
        else:
            logger.error(f"Ошибка установки, код: {process.returncode}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при установке: {e}")
        return False

async def shutdownBrowser():
    global _browserProcess
    if _browserProcess and _browserProcess.returncode is None:
        try:
            logger.info("Завершаю процесс браузера...")
            _browserProcess.terminate()
            try:
                await asyncio.wait_for(_browserProcess.wait(), timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Браузер не завершился, принудительно завершаю...")
                _browserProcess.kill()
                await _browserProcess.wait()
            logger.success("Браузер завершен")
            _browserProcess = None
        except Exception as e:
            logger.error(f"Ошибка при завершении браузера: {e}")


async def launchBrowser() -> bool:
    global _browserProcess

    browserExe = findBrowserExecutable()

    if not browserExe:
        logger.info("Chrome.exe не найден, запускаю установку через CloakBrowser...")
        if not await installBrowser():
            return False

        await asyncio.sleep(3)
        browserExe = findBrowserExecutable()

        if not browserExe:
            logger.error("Не удалось найти chrome.exe после установки")
            logger.error(f"Проверьте папку: {CLOAKBROWSER_INSTALL_DIR}")
            return False

    cdpPort = CLOAKBROWSER_CDP_URL.split(":")[-1]
    logger.info(f"Запускаю браузер: {browserExe}")
    logger.info(f"Remote debugging порт: {cdpPort}")

    try:
        process = await asyncio.create_subprocess_exec(
            browserExe,
            f"--remote-debugging-port={cdpPort}",
            "--no-first-run",
            "--no-default-browser-check",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )

        _browserProcess = process
        logger.success(f"Браузер запущен (PID: {process.pid})")
        logger.info("Ожидаю 10 секунд для инициализации...")
        await asyncio.sleep(10)

        for i in range(5):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{CLOAKBROWSER_CDP_URL}/json/version", timeout=3.0)
                    if response.status_code == 200:
                        logger.success("CDP готов к работе!")
                        return True
            except:
                logger.info(f"Ожидаю CDP... попытка {i+1}/5")
                await asyncio.sleep(2)

        logger.warning("Не удалось подключиться к CDP")
        return False

    except Exception as e:
        logger.error(f"Ошибка запуска браузера: {e}")
        return False

async def isBrowserRunning() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CLOAKBROWSER_CDP_URL}/json/version", timeout=3.0)
            return response.status_code == 200
    except:
        return False
