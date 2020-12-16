import nonebot

bot = nonebot.get_bot()

@bot.server_app.route('/')
async def checkonweb():
    return '暂未制作，敬请期待'