from nonebot import session
from config import ERR_STR
from nonebot import on_command, CommandSession
import ujson
import re
import os
import shutil
from datetime import datetime
import nonebot
import zoneinfo

stage_list = ['1-1', '1-2', '1-3', '1-4', '1-5', '1-6', '2-1', '2-2', '2-3', '2-4', '2-5', '3-1', '3-2', '3-3', '3-4', '3-5',
              '7-1', '7-2', '7-2P1', '7-2P2', '7-3', '7-3P1', '7-3P2', '4-1', '4-2', '4-3', '4-4', '4-5', '5-1', '5-2', '5-3', '5-4', '5-5', '6-1', '6-2', '6-3', '6-4', '6-5']

status_list = ['+1', '-1', '完成', 'complete',
               '0', '+2', '-2', '+3', '-3', '1', '2', '3']


# task record

@on_command('task', aliases=('任务', '任务记录', '记录'), only_to_me=False)
async def task(session: CommandSession):
    arg = session.get('arg')
    userid = session.event.user_id  # QQ号
    nickname = session.event.sender['nickname']  # 昵称，注意转义
    tasknumber = await record(arg, userid, session)
    if tasknumber == '-1':
        await arg_err(session)
    elif tasknumber == "-2":
        session.finish()
    else:
        await session.send(str(userid)+' 任务 '+tasknumber+' 记录成功')
        session.finish()


@task.args_parser
async def _(session: CommandSession):
    """args parser"""
    stripped_arg = session.current_arg_text.strip()
    if not stripped_arg:
        await arg_err(session)
    else:
        session.state['arg'] = stripped_arg


async def arg_err(session):
    """input wrong arg"""
    await session.send(ERR_STR)
    session.finish()


async def record(arg: str, userid, session: CommandSession):
    arg_list = arg.split(' ')
    length = len(arg_list)
    # if there is not a userdata file, copy one from init.json
    if not os.path.exists('./userdata/' + str(userid) + '.json'):
        shutil.copy2(r'./data/init.json', './userdata/' +
                     str(userid) + '.json')
        # add userid
        with open('./userdata/' + str(userid) + '.json', 'r+', encoding="utf-8-sig") as file_json:
            file_dict: dict = ujson.load(file_json)
            file_dict["userid"] = userid
            file_json.seek(0, 0)
            file_json.truncate()
            ujson.dump(file_dict, file_json, indent=4)
    else:
        # check if there is a new verson of init.json
        file_json_init = open('./data/init.json', 'r', encoding="utf_8_sig")
        file_json_user = open('./userdata/' + str(userid) +
                              '.json', 'r+', encoding="utf-8-sig")
        file_dict_init = ujson.load(file_json_init)
        file_dict_user = ujson.load(file_json_user)
        if not file_dict_init["version"] == file_dict_user["version"]:
            file_dict_init["userid"] = file_dict_user["userid"]
            for tasktype in ['once', 'weekly', 'monthly', 'quarterly', 'yearly']:
                for index, taskrecord in enumerate(file_dict_user["record"][tasktype]):
                    file_dict_init["record"][tasktype][index] = taskrecord
            file_dict_user = file_dict_init
            file_json_user.seek(0, 0)
            file_json_user.truncate()
            ujson.dump(file_dict_user, file_json_user)
        file_json_init.close()
        file_json_user.close()
    tasknumber = arg_list[0].capitalize()
    tasknumber = await searchtasknumber(tasknumber)
    if tasknumber == '-1':
        return '-1'
    tasktype = await checktasktype(tasknumber)
    # if complete this whole task
    if arg_list[1] == '完成' or arg_list[1] == "complete":
        if length != 2:
            return '-1'
        with open('./userdata/' + str(userid) + '.json', 'r+', encoding="utf-8-sig") as file_json:
            file_dict: dict = ujson.load(file_json)
            for taskrecord in file_dict["record"][tasktype]:
                if taskrecord["tasknumber"] == tasknumber:
                    taskrecord["iscomplete"] = 1
                    for stagerecord in taskrecord["stage"]:
                        stagerecord["time"] = stagerecord["requiretime"]
                        stagerecord["iscomplete"] = 1
                    break
            file_json.seek(0, 0)
            file_json.truncate()
            ujson.dump(file_dict, file_json, indent=4)
        return tasknumber
    if length % 2 == 0:
        return '-1'
    # record
    with open('./userdata/' + str(userid) + '.json', 'r+', encoding="utf-8-sig") as file_json:
        file_bak = file_json.read()
        file_json.seek(0, 0)
        file_dict: dict = ujson.load(file_json)
        file_json.seek(0, 0)
        file_json.truncate()
        thistaskrecord = {}
        for taskrecord in file_dict["record"][tasktype]:
            if taskrecord["tasknumber"] == tasknumber:
                thistaskrecord = taskrecord
                break
        # check stage and status
        for i in range(length//2):
            stage = arg_list[2 * i + 1].upper()
            status = arg_list[2 * i + 2]
            if stage not in stage_list:
                return '-1'
            if status not in status_list:
                return '-1'
        # search
        for i in range(length//2):
            stage = arg_list[2 * i + 1]
            status = arg_list[2 * i + 2]
            flag = 0
            for stagerecord in thistaskrecord["stage"]:
                if stage == stagerecord["stage"]:
                    flag = 1
                    # 是不是应该改成基于类型的啊，这也太长了
                    if status == '-1':
                        if stagerecord["time"]-1 < 0:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图,记录次数为"+str(stagerecord["time"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] -= 1
                        thistaskrecord["iscomplete"] = 0
                        stagerecord["iscomplete"] = 0
                    elif status == '-2':
                        if stagerecord["time"]-2 < 0:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，记录次数为"+str(stagerecord["time"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] -= 2
                        thistaskrecord["iscomplete"] = 0
                        stagerecord["iscomplete"] = 0
                    elif status == '-3':
                        if stagerecord["time"]-3 < 0:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，记录次数为"+str(stagerecord["time"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] -= 3
                        thistaskrecord["iscomplete"] = 0
                        stagerecord["iscomplete"] = 0
                    elif status == '+1':
                        if stagerecord["time"]+1 > stagerecord["requiretime"]:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，记录次数为"+str(stagerecord["time"])+"次，任务要求为"+str(stagerecord["requiretime"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] += 1
                        if stagerecord["time"] == stagerecord["requiretime"]:
                            stagerecord["iscomplete"] = 1
                    elif status == '+2':
                        if stagerecord["time"]+2 > stagerecord["requiretime"]:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，记录次数为"+str(stagerecord["time"])+"次，任务要求为"+str(stagerecord["requiretime"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] += 2
                        if stagerecord["time"] == stagerecord["requiretime"]:
                            stagerecord["iscomplete"] = 1
                    elif status == '+3':
                        if stagerecord["time"]+3 > stagerecord["requiretime"]:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，记录次数为"+str(stagerecord["time"])+"次，任务要求为"+str(stagerecord["requiretime"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] += 3
                        if stagerecord["time"] == stagerecord["requiretime"]:
                            stagerecord["iscomplete"] = 1
                    elif status == '完成' or status == 'complete':
                        stagerecord["time"] = stagerecord["requiretime"]
                        stagerecord["iscomplete"] = 1
                    elif status == '0':
                        stagerecord["time"] = 0
                        stagerecord["iscomplete"] = 0
                        thistaskrecord["iscomplete"] = 0
                    elif status == '1':
                        stagerecord["time"] = 1
                        if stagerecord["requiretime"] == 1:
                            stagerecord["iscomplete"] = 1
                        else:
                            stagerecord["iscomplete"] = 0
                            thistaskrecord["iscomplete"] = 0
                    elif status == '2':
                        if stagerecord["requiretime"] < 2:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，任务要求为"+str(stagerecord["requiretime"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] = 2
                        if stagerecord["requiretime"] == 2:
                            stagerecord["iscomplete"] = 1
                        else:
                            stagerecord["iscomplete"] = 0
                            thistaskrecord["iscomplete"] = 0
                    elif status == '3':
                        if stagerecord["requiretime"] < 3:
                            await session.send("参数错误，任务"+tasknumber+"中的"+stage+"图，任务要求为"+str(stagerecord["requiretime"])+"次")
                            file_json.write(file_bak)
                            return '-2'
                        stagerecord["time"] = 3
                        if stagerecord["requiretime"] == 3:
                            stagerecord["iscomplete"] = 1
                        else:
                            stagerecord["iscomplete"] = 0
                            thistaskrecord["iscomplete"] = 0
                    break
            if flag == 0:
                await session.send("任务"+tasknumber+"中不包含"+stage+"，请重新输入")
                file_json.write(file_bak)
                return '-2'
            flag = 1
            for stagerecord in thistaskrecord["stage"]:
                if stagerecord["iscomplete"] == 0:
                    flag = 0
            if flag == 1:
                thistaskrecord["iscomplete"] = 1
        ujson.dump(file_dict, file_json, indent=4)

    return tasknumber


async def searchtasknumber(tasknumber: str) -> str:
    """search tasknumber"""
    if tasknumber[1] == '0':
        tasknumber = tasknumber[0]+tasknumber[2:]
    #if tasknumber[2] == '0':
    #    tasknumber = tasknumber[0]+tasknumber[1]+tasknumber[3:]
    with open("./data/task.csv", 'r', encoding="utf-8-sig") as csvfile:
        csv = csvfile.read()
        flag = 0
        for line in csv.split("\n")[1:]:
            row = line.split(",")
            for col in row:
                if tasknumber == col:
                    tasknumber = row[0]
                    flag = 1
                    break
            if flag == 1:
                break
        if flag == 0:
            return '-1'
    return tasknumber


async def checktasktype(tasknumber: str) -> str:
    """check the type of task"""
    """if tasknumber[1] == 'd':
        tasktype = 'daily'"""
    if tasknumber[1] == 'w':
        tasktype = 'weekly'
    elif tasknumber[1] == 'm':
        tasktype = "monthly"
    elif tasknumber[1] == 'q':
        tasktype = "quarterly"
    elif tasknumber[1] == 'y':
        tasktype = "yearly"
    else:
        tasktype = 'once'
    return tasktype

# check task record


@on_command('check', aliases=('任务查询', '查询', '查询记录', '查询任务'), only_to_me=False)
async def check(session: CommandSession):
    arg = session.get('arg')
    userid = session.event.user_id  # QQ号
    nickname = session.event.sender['nickname']  # 昵称，注意转义
    tasknumber = await checkrecord(arg, userid, session)
    session.finish()


@check.args_parser
async def _(session: CommandSession):
    """args parser"""
    stripped_arg = session.current_arg_text.strip()
    if not stripped_arg:
        await arg_err(session)
    else:
        session.state['arg'] = stripped_arg


async def checkrecord(arg: str, userid, session: CommandSession):
    if not os.path.exists('./userdata/' + str(userid) + '.json'):
        await session.send(str(userid)+' 不存在记录')
        return '-1'
    tasknumber = arg.capitalize()
    tasknumber = await searchtasknumber(tasknumber)
    if tasknumber == '-1':
        await session.send('任务名输入错误')
        return '-1'
    tasktype = await checktasktype(tasknumber)
    with open('./userdata/' + str(userid) + '.json', 'r', encoding="utf-8-sig") as file_json:
        file_dict: dict = ujson.load(file_json)
        thistaskrecord = {}
        for taskrecord in file_dict["record"][tasktype]:
            if taskrecord["tasknumber"] == tasknumber:
                thistaskrecord = taskrecord
                break
        # if the whole task is complete
        if thistaskrecord["iscomplete"] == 1:
            await session.send(str(userid)+" 任务 "+tasknumber+" 已完成")
            return tasknumber
        # check how many times left
        sessionstr = str(userid)+" 任务 "+tasknumber
        for stage in thistaskrecord["stage"]:
            if stage["iscomplete"] == 1:
                continue
            sessionstr += " " + \
                stage["stage"]+"记录"+str(stage["time"])+"次 还差" + \
                str(stage["requiretime"]-stage["time"])+"次"
        await session.send(sessionstr)
        return tasknumber


# auto initialize task record


@nonebot.scheduler.scheduled_job('cron', hour=4)
async def _():
    """clear task record when 4:00am GMT+8"""
    bot = nonebot.get_bot()
    now = datetime.now(zoneinfo.ZoneInfo('Asia/Shanghai'))
    # await init("daily")
    if now.weekday == 0:
        await init("weekly")
    if now.day == 1:
        await init("monthly")
        if now.month == 3 or now.month == 6 or now.month == 9 or now.month == 12:
            await init("quarterly")
        await init_yearly(now.month)


async def init(tasktype: str):
    """clear task record"""
    for root, dirs, files in os.walk(r'./userdata'):
        for jsonfile in files:
            with open(os.path.join(root, jsonfile), 'r+', encoding="utf-8-sig") as file_json:
                file_dict = ujson.load(file_json)
                for taskrecord in file_dict["record"][tasktype]:
                    taskrecord["iscomplete"] = 0
                    for stage in taskrecord["stage"]:
                        stage["time"] = 0
                        stage["iscomplete"] = 0
                file_json.seek(0, 0)
                file_json.truncate()
                ujson.dump(file_dict, file_json, indent=4)
    return


async def init_yearly(month: int):
    """clear yearly task record"""
    for root, dirs, files in os.walk(r'./userdata'):
        for jsonfile in files:
            with open(os.path.join(root, jsonfile), 'r+', encoding="utf-8-sig") as file_json:
                file_dict = ujson.load(file_json)
                for taskrecord in file_dict["record"]["yearly"]:
                    if taskrecord["month"] == month:
                        taskrecord["iscomplete"] = 0
                        for stage in taskrecord["stage"]:
                            stage["time"] = 0
                            stage["iscomplete"] = 0
                file_json.seek(0, 0)
                file_json.truncate()
                ujson.dump(file_dict, file_json, indent=4)
    return