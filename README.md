# kancolletaskrecord

kancolle task record based on nonebot

## INSTALL

    pip install nonebot "nonebot[scheduler]" ujson

## RUN

首先重命名config_template.py为config.py并修改文件中的各项内容，匹配cqhttp设置

然后打开bot.py即可

## USAGE

机器人能响应私聊或者群聊，目前默认不需要艾特机器人或者喊机器人的昵称即可响应命令

命令开头需添加'/', '!', '／', '！', '#'中的任意一个字符

记录命令为

/task(任务,任务记录,记录) tasknumber 完成(complete)(stage1 status1 [stage 2 status2 ...])

“task”或“任务”等为命令名

tasknumber为任务编号，目前仅支持战斗任务，即B开头的任务。任务编号请在poi插件或[舰娘百科任务页面](https://zh.kcwiki.cn/wiki/%E4%BB%BB%E5%8A%A1)查看。仅需一次即可完成的任务，以及可以在几个不同地图任意挑选完成的任务不包含在内。或者说，本记录只会对真正需要记录的任务进行记录

“完成”或“complete”代表整个任务完成，此时无需输入地图和状态参数

stage为任务地图，status为任务完成状态，支持“+1”，“+2”，“-1”，“1”，“2”，“完成”，“complete”等参数，参数意义同字面意思一致。并且，多个stage和status可以连续输入。任意一个stage或status输入有误，整个语句将不会生效，本次不会进行任何记录

查询命令为

/check(查询,任务查询,查询,查询记录,查询任务) tasknumber

“check”或“查询”等为命令名

tasknumber为任务编号，与记录命令中的相同

也可访问网页进行查看和修改（待做）

## TODO

- [x] 月常远征提醒

- [x] 任务记录到时自动清零

- [x] init.json录入

- [x] task.csv录入

- [ ] 网页查询和修改
