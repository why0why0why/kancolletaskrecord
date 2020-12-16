import os
import ujson
import zoneinfo
import nonebot
from datetime import datetime
from config import REMIND_GROUP


@nonebot.scheduler.scheduled_job('cron', hour="1,13")
async def _():
    """drill remind"""
    bot = nonebot.get_bot()
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Shanghai'))
    for group in REMIND_GROUP:
        await bot.send_group_msg(group_id=group, message='演习还有一小时刷新')


@nonebot.scheduler.scheduled_job('cron', hour=22, day='last')
async def _():
    """EO remind"""
    bot = nonebot.get_bot()
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Shanghai'))
    for group in REMIND_GROUP:
        await bot.send_group_msg(group_id=group, message='EO还有一小时刷新')


@nonebot.scheduler.scheduled_job('cron', hour=10, day="11,12,13")
async def _():
    """expedition remind"""
    bot = nonebot.get_bot()
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Shanghai'))
    for group in REMIND_GROUP:
        await bot.send_group_msg(group_id=group, message='月常远征将于15日刷新')
