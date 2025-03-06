# ---------------------------------------------------------------------------------
# Name: OpenRouter
# Author: otohikko
# Commands:
# .ask
# ---------------------------------------------------------------------------------
# ▄▀▀▀▀▄   ▄▀▀▀█▀▀▄  ▄▀▀▀▀▄   ▄▀▀▄ ▄▄   ▄▀▀█▀▄    ▄▀▀▄ █  ▄▀▀▄ █  ▄▀▀▀▀▄  
#█      █ █    █  ▐ █      █ █  █   ▄▀ █   █  █  █  █ ▄▀ █  █ ▄▀ █      █ 
#█      █ ▐   █     █      █ ▐  █▄▄▄█  ▐   █  ▐  ▐  █▀▄  ▐  █▀▄  █      █ 
#▀▄    ▄▀    █      ▀▄    ▄▀    █   █      █       █   █   █   █ ▀▄    ▄▀ 
#  ▀▀▀▀    ▄▀         ▀▀▀▀     ▄▀  ▄▀   ▄▀▀▀▀▀▄  ▄▀   █  ▄▀   █    ▀▀▀▀   
#         █                   █   █    █       █ █    ▐  █    ▐           
#         ▐                   ▐   ▐    ▐       ▐ ▐       ▐        
#              © Copyright 2025
#           http://otohikko.t.me/
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @otohikko
# scope: hikka_only
# scope: hikka_min 1.3.0
# requires: openai

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI
from .. import loader, utils

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@loader.tds
class OpenRouter(loader.Module):
    """Взаимодействие с различными моделями AI через OpenRouter"""

    strings = {
        "name": "DeepSeek",

        "no_args": "<emoji document_id=5854929766146118183>❌</emoji> <b>Нужно </b><code>{}{} {}</code>",
        "no_token": "<emoji document_id=5854929766146118183>❌</emoji> <b>Нету токена! Вставь его в </b><code>{}cfg deepseek</code>",

        "asking_model": "<emoji document_id=5332518162195816960>🔄</emoji> <b>Спрашиваю {}...</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "Токен OpenRouter. Получить токен: https://openrouter.ai/keys",
                validator=loader.validators.Hidden(loader.validators.String())
            ),
            loader.ConfigValue(
                "model",
                "deepseek/deepseek-chat",
                lambda: "Модель AI для использования. Пример: deepseek/deepseek-chat, openai/gpt-3.5-turbo",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "answer_text",
                """[👤](tg://emoji?id=5879770735999717115) **Вопрос:** {question}

[🤖](tg://emoji?id=5372981976804366741) **Ответ:** {answer}

<b>Модель:</b> <code>{model}</code>""",
                lambda: "Текст вывода",
            ),
        )
        self.executor = ThreadPoolExecutor()

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command()
    async def ask(self, message):
        """Задать вопрос к выбранной модели AI"""
        q = utils.get_args_raw(message)
        if not q:
            return await utils.answer(message, self.strings["no_args"].format(self.get_prefix(), "deepseek", "[вопрос]"))

        if not self.config['api_key']:
            return await utils.answer(message, self.strings["no_token"].format(self.get_prefix()))

        m = await utils.answer(message, self.strings['asking_model'].format(self.config['model']))

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.config['api_key'],
        )

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: client.chat.completions.create(
                    model=self.config['model'],
                    messages=[{"role": "user", "content": q}],
                    stream=True,  
                )
            )

            answer = ""
            last_answer = ""  
            for chunk in response:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

                    if answer != last_answer:
                        try:
                            await m.edit(self.config['answer_text'].format(
                                question=q,
                                answer=answer,
                                model=self.config['model']
                            ), parse_mode="markdown")
                            last_answer = answer  # Обновляем последний успешно отправленный ответ
                        except Exception as e:
                            logger.warning(f"Ошибка при редактировании сообщения: {e}")

        except Exception as e:
            logger.exception("Ошибка при запросе к OpenRouter API")
            answer = f"Ошибка: {e}"
            await m.edit(answer)

        if answer != last_answer:
            try:
                await m.edit(self.config['answer_text'].format(
                    question=q,
                    answer=answer,
                    model=self.config['model']
                ), parse_mode="markdown")
            except Exception as e:
                logger.warning(f"Ошибка при финальном редактировании сообщения: {e}")