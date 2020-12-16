from nonebot import on_command, CommandSession

@on_command('tz', aliases=('团子','tzsb','团子傻逼'), only_to_me=False)
async def task(session: CommandSession):
    await session.send("[CQ:at,qq=1503123256]tzsb")
    session.finish()