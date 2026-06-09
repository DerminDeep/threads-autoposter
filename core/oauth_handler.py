import httpx
import webbrowser
from urllib.parse import urlencode, parse_qs
from config.settings import META_APP_ID, META_APP_SECRET, THREADS_REDIRECT_URI
from utils.logger import logger


class OAuthHandler:
    AUTH_URL = "https://threads.net/oauth/authorize"
    TOKEN_URL = "https://graph.threads.net/oauth/access_token"
    LONG_LIVED_TOKEN_URL = "https://graph.threads.net/access_token"
    ME_URL = "https://graph.threads.net/v1.0/me"

    def __init__(self):
        self.app_id = META_APP_ID
        self.app_secret = META_APP_SECRET
        self.redirect_uri = THREADS_REDIRECT_URI

    def get_auth_url(self) -> str:
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "threads_basic,threads_content_publish,threads_manage_replies",
            "response_type": "code"
        }
        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        logger.info(f"Generated OAuth URL: {auth_url}")
        return auth_url

    def open_auth_browser(self):
        auth_url = self.get_auth_url()
        logger.info("Opening browser for OAuth authorization")
        webbrowser.open(auth_url)
        return auth_url

    async def exchange_code_for_token(self, code: str) -> str | None:
        logger.info(f"Exchanging authorization code for short-lived token")

        data = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.TOKEN_URL, data=data)
                response.raise_for_status()
                result = response.json()

                access_token = result.get("access_token")
                user_id = result.get("user_id")

                logger.success(f"Received short-lived token for user {user_id}")
                return access_token

        except httpx.HTTPError as e:
            logger.error(f"HTTP error exchanging code for token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None

    async def exchange_for_long_lived_token(self, short_lived_token: str) -> str | None:
        logger.info("Exchanging short-lived token for long-lived token")

        params = {
            "grant_type": "th_exchange_token",
            "client_secret": self.app_secret,
            "access_token": short_lived_token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.LONG_LIVED_TOKEN_URL, params=params)
                response.raise_for_status()
                result = response.json()

                access_token = result.get("access_token")
                expires_in = result.get("expires_in")

                logger.success(f"Received long-lived token (expires in {expires_in} seconds)")
                return access_token

        except httpx.HTTPError as e:
            logger.error(f"HTTP error exchanging for long-lived token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error exchanging for long-lived token: {e}")
            return None

    async def validate_token(self, access_token: str) -> bool:
        logger.info("Validating access token")

        params = {
            "access_token": access_token,
            "fields": "id,username"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ME_URL, params=params)
                response.raise_for_status()
                logger.success("Token is valid")
                return True

        except httpx.HTTPError as e:
            logger.warning(f"Token validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False

    async def get_user_id(self, access_token: str) -> str | None:
        logger.info("Fetching Threads User ID")

        params = {
            "access_token": access_token,
            "fields": "id,username"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.ME_URL, params=params)
                response.raise_for_status()
                result = response.json()

                user_id = result.get("id")
                username = result.get("username")

                logger.success(f"Retrieved User ID: {user_id}, Username: {username}")
                return user_id

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching user ID: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user ID: {e}")
            return None
