from nonebot import on_command, CommandSession

@on_command('cc', aliases=('ccsb','cc傻逼'), only_to_me=False)
async def task(session: CommandSession):
    await session.send("[CQ:at,qq=541183064]ccsb")
    session.finish()