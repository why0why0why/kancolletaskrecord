import os
import ujson
import pytz
import nonebot
from nonebot import on_command, CommandSession
import subprocess


@nonebot.scheduler.scheduled_job('cron', hour="8")
async def _():
    """update ftumm"""
    subprocess.Popen(r"powershell .\data\update.bat")


@on_command('updateftumm', aliases=('更新ftumm','更新FTUMM'), only_to_me=False)
async def updateftumm(session: CommandSession):
    subprocess.Popen(r"powershell .\data\update.bat")
    await session.send('FTUMM更新完成')
    session.finish()