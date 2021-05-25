from nonebot import on_command, CommandSession

@on_command('ys', aliases=('永山','yssb','永山傻逼'), only_to_me=False)
async def task(session: CommandSession):
    await session.send("[CQ:at,qq=445886434]yssb")
    session.finish()