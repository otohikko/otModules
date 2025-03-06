# ---------------------------------------------------------------------------------
# Name: TimeInName
# Author: otohikko
# Commands:
# .timein
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

from hikka import loader, utils
from datetime import datetime
import pytz
import asyncio
from telethon.tl.functions.account import UpdateProfileRequest

@loader.tds
class TimeInNameMod(loader.Module):
    """Модуль для обновления имени в формате 'имя|время'"""
    strings = {"name": "TimeInName"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "TIMEZONE", "Europe/Kyiv", lambda: "Часовой пояс (например, Europe/Kyiv)",
            "NICKNAME", "User", lambda: "Твой ник (например, otohikko)"
        )
        self.running = False
        self.last_time = None

    async def watcher(self, message):
        """Обновляет имя, только если время изменилось"""
        if not self.running:
            return

        timezone = pytz.timezone(self.config["TIMEZONE"])
        current_time = datetime.now(timezone).strftime('%H:%M')

        if current_time == self.last_time:
            await asyncio.sleep(1)
            return

        nickname = str(self.config["NICKNAME"])
        await self.client(UpdateProfileRequest(
            first_name=f"{nickname}|{current_time}"
        ))

        self.last_time = current_time

    async def timeincmd(self, message):
        """Включить/выключить обновление имени"""
        self.running = not self.running
        status = "включено" if self.running else "выключено"
        await utils.answer(message, f"Обновление имени {status}.")