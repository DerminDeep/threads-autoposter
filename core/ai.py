import os
from typing import Optional
from pathlib import Path
from config.settings import AI_BASE_URL, AI_API_KEY, AI_MODEL, AI_TIMEOUT, AI_PROVIDER
from utils.logger import logger


class AIProvider:
    def __init__(self):
        self.client = None
        self.persona = self._loadPersona()
        self.skills = self._loadSkills()
        self.provider = AI_PROVIDER

    def _loadPersona(self) -> str:
        personaPath = Path('config/prompts/persona.md')
        if personaPath.exists():
            try:
                content = personaPath.read_text(encoding='utf-8')
                logger.info(f'Loaded persona from {personaPath}')
                return content
            except Exception as e:
                logger.warning(f'Failed to load persona: {e}')
        return ''

    def _loadSkills(self) -> dict:
        skills = {}
        skillsDir = Path('config/skills')
        if skillsDir.exists():
            for skillFile in skillsDir.glob('*.md'):
                try:
                    content = skillFile.read_text(encoding='utf-8')
                    skillName = skillFile.stem
                    skills[skillName] = content
                    logger.info(f'Loaded skill: {skillName}')
                except Exception as e:
                    logger.warning(f'Failed to load skill {skillFile}: {e}')
        return skills

    async def generatePost(self, topic: str, style: str = 'casual', skill: str = None, webContext: str = None) -> Optional[str]:
        try:
            if self.provider == 'anthropic':
                return await self._generateAnthropic(topic, style, skill, webContext)
            else:
                return await self._generateOpenAI(topic, style, skill, webContext)

        except Exception as e:
            logger.error(f'AI provider error: {e}')
            return None

    async def _generateOpenAI(self, topic: str, style: str, skill: str, webContext: str) -> Optional[str]:
        from openai import AsyncOpenAI, APITimeoutError

        if self.client is None:
            self.client = AsyncOpenAI(
                base_url=AI_BASE_URL,
                api_key=AI_API_KEY or 'not-needed',
                max_retries=1
            )

        contextPart = webContext if webContext else ""

        systemPrompt = "You are a social media expert specializing in Threads posts. Generate engaging, authentic content that drives interaction."

        if self.persona:
            systemPrompt += f"\n\nPERSONA INSTRUCTIONS:\n{self.persona}"

        skillContent = ""
        if skill and skill in self.skills:
            skillContent = f"\n\nSKILL: {skill}\n{self.skills[skill]}"
            logger.info(f'Using skill: {skill}')

        prompt = f'''Generate an engaging Threads post about: {topic}
{contextPart}{skillContent}
Style: {style}
Requirements:
- Keep it under 500 characters
- Make it conversational and engaging
- Include a question or call to action
- Use emojis sparingly (1-2 max)
- Make it shareable and comment-worthy
- Return ONLY the post text, no explanations, no metadata, no character count, no tone description
- Do NOT add any labels like "Character count:", "Tone:", "Hook:", "CTA:" at the end

Post:'''

        logger.info(f'Sending request to {AI_BASE_URL} with model {AI_MODEL}...')

        try:
            response = await self.client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {'role': 'system', 'content': systemPrompt},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.8,
                max_tokens=300,
                timeout=float(AI_TIMEOUT)
            )

            content = response.choices[0].message.content.strip()
            content = self._cleanMetaInfo(content)
            logger.success(f'Generated post: {content[:50]}...')
            return content

        except APITimeoutError:
            logger.error(f'AI generation timeout ({AI_TIMEOUT}s)')
            return None
        except Exception as e:
            error_msg = str(e)
            if '500' in error_msg or 'Internal Server Error' in error_msg:
                logger.error(f'AI server error (500). Check that AI service is running and model {AI_MODEL} is available')
            else:
                logger.error(f'AI generation error: {e}')
            return None

    async def _generateAnthropic(self, topic: str, style: str, skill: str, webContext: str) -> Optional[str]:
        from anthropic import AsyncAnthropic, APITimeoutError

        if self.client is None:
            if AI_BASE_URL and AI_BASE_URL != 'https://api.anthropic.com':
                self.client = AsyncAnthropic(
                    base_url=AI_BASE_URL,
                    api_key=AI_API_KEY,
                    max_retries=1
                )
            else:
                self.client = AsyncAnthropic(
                    api_key=AI_API_KEY,
                    max_retries=1
                )

        contextPart = webContext if webContext else ""

        systemPrompt = "You are a social media expert specializing in Threads posts. Generate engaging, authentic content that drives interaction."

        if self.persona:
            systemPrompt += f"\n\nPERSONA INSTRUCTIONS:\n{self.persona}"

        skillContent = ""
        if skill and skill in self.skills:
            skillContent = f"\n\nSKILL: {skill}\n{self.skills[skill]}"
            logger.info(f'Using skill: {skill}')

        prompt = f'''Generate an engaging Threads post about: {topic}
{contextPart}{skillContent}
Style: {style}
Requirements:
- Keep it under 500 characters
- Make it conversational and engaging
- Include a question or call to action
- Use emojis sparingly (1-2 max)
- Make it shareable and comment-worthy
- Return ONLY the post text, no explanations, no metadata, no character count, no tone description
- Do NOT add any labels like "Character count:", "Tone:", "Hook:", "CTA:" at the end

Post:'''

        logger.info(f'Sending request to Anthropic with model {AI_MODEL}...')

        try:
            response = await self.client.messages.create(
                model=AI_MODEL,
                system=systemPrompt,
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.8,
                max_tokens=300,
                timeout=float(AI_TIMEOUT)
            )

            content = response.content[0].text.strip()
            content = self._cleanMetaInfo(content)
            logger.success(f'Generated post: {content[:50]}...')
            return content

        except APITimeoutError:
            logger.error(f'AI generation timeout ({AI_TIMEOUT}s)')
            return None
        except Exception as e:
            error_msg = str(e)
            if '500' in error_msg or 'Internal Server Error' in error_msg:
                logger.error(f'AI server error (500). Check that AI service is running')
            else:
                logger.error(f'AI generation error: {e}')
            return None

    def _cleanMetaInfo(self, content: str) -> str:
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            if any(marker in line.lower() for marker in [
                'character count:', 'tone:', 'hook:', 'cta:',
                'кол-во символов:', 'тон:', 'хук:'
            ]):
                break
            clean_lines.append(line)

        return '\n'.join(clean_lines).strip()


def getProvider() -> AIProvider:
    logger.info(f'Using AI provider: {AI_PROVIDER} / {AI_BASE_URL if AI_PROVIDER == "openai" else "anthropic"} / {AI_MODEL}')
    return AIProvider()
