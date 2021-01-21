from nonebot import on_command, CommandSession

@on_command('萩', aliases=('萩图','hagihagi'), only_to_me=False)
async def task(session: CommandSession):
    await session.send("[CQ:image,file=plugins\CQHTTPMirai\images\hagi.jpg]ハギハギ♡ドキドキ")
    session.finish()