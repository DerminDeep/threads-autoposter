from core.ai import getProvider
from core.mcp_client import mcpClient
from database.models import addPost, getTopics
from utils.logger import logger
from typing import Optional
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        self.provider = getProvider()

    async def generateAndQueue(
        self,
        topic: str,
        count: int = 1,
        scheduledTime: Optional[datetime] = None,
        style: str = 'casual'
    ) -> list[int]:
        postIds = []

        for i in range(count):
            logger.info(f'Generating post {i+1}/{count} for topic: {topic}')
            content = await self.generateNow(topic, style)

            if content:
                postId = await addPost(content, topic, scheduledTime)
                postIds.append(postId)
                logger.success(f'Post added to queue: ID {postId}')
            else:
                logger.error(f'Failed to generate post {i+1}')

        return postIds

    async def generateNow(self, topic: str, style: str = 'casual') -> Optional[str]:
        web_context = None


        try:
            search_results = await mcpClient.search(topic, max_results=3)

            if search_results:
                web_context = f"\nДоступный контекст из интернета (используй если релевантно):\n{search_results}"
                logger.info("Получен контекст из интернета")
        except Exception as e:
            logger.debug(f"MCP unavailable: {e}")

        return await self.provider.generatePost(topic, style, web_context)
