# ---------------------------------------------------------------------------------
# Name: MusicDw
# Author: otohikko
# Commands:
# .mol
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

from .. import loader, utils
from telethon.tl.types import Document
import asyncio

@loader.tds
class MusicDw(loader.Module):
    """Скачивание музыки."""

    strings = {
        "name": "MusicDw",
        "args": "🚫 <b>Не указаны аргументы</b>",
        "loading": "🔍 <b>Поиск...</b>",
        "404": "🚫 <b>Трек </b><code>{}</code><b> не найден</b>",
    }

    async def _dl(self, bot: str, query: str):
        try:
            results = await self._client.inline_query(bot, query)
            if results:
                return results[0].document
        except Exception:
            return None

    async def _search_bots(self, query: str):
        bots = ["@vkm4bot", "@lybot", "@losslessrobot"]
        tasks = [self._dl(bot, query) for bot in bots]
        results = await asyncio.gather(*tasks)

        for document in results:
            if document:
                return document
        return None

    async def mdwcmd(self, message):
        """<название> - Скачать трек."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        await utils.answer(message, self.strings("loading"))

        document = await self._search_bots(args)
        if not document:
            await utils.answer(message, self.strings("404").format(args))
            return

        await self._client.send_file(
            message.peer_id,
            document,
            reply_to=getattr(message, "reply_to_msg_id", None),
        )
        if message.out:
            await message.delete()