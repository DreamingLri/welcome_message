from datetime import datetime
import random
import json
from mcdreforged.api.all import *
import math
import random

__mcdr_ : PluginServerInterface
page_size = 10

config_path = 'config/welcome_message.json'
default_config = {
    "messages": [
        "欢迎 {player} 加入服务器喵~",
        "欢迎 {player} 喵~"
        ],
    "datetime": "1988-01-01",
    "error_message": "出错了喵，请联系服主喵~"
}

help_info = '''-------- &a Player Last Play &r--------
&7!!mv help &f- &c显示帮助消息
&7!!mv list [index] &f- &c显示欢迎消息列表,index代表页数
&7!!mv add <text> &f- &c添加欢迎消息
&7!!mv del <text> &f- &c删除欢迎消息
-----------------------------------
'''

def load_config():
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        with open(config_path, 'w') as file:
            json.dump(default_config, file, indent=4)
        return default_config
    
def get_player_last_join(server, context):
    player = context['player']
    online_players = server.get_online_players()
    resp: str
    if player in online_players:
        resp = f'玩家&a{player}&r当前&a在线喵~'
    elif player in server.get_offline_players():
        resp = f'玩家&a{player}&r最后一次登录时间为{server.get_player_last_join(player)}'
    else:
        resp = f'玩家&a{player}&r还没有登陆过喵·w·'
    return server.reply(replace_code(resp))

    

def get_welcome_message_list(server, context):
    if 'index' in context:
        index = context['index'] - 1
    else:
        index = 0
    if index < 0:
        return server.reply("查询页数不能小于1")
    
    global page_size
    message_list = load_config()
    result_list = []
    for message in message_list['messages']:
        result_list.append(f'&r|- &a{message}&r')
    
    total = len(result_list)
    resp = '------ &a消息列表 &r------\n'

    if total == 0:
        resp += f'&r>>>>>> 第0页/共0页 <<<<<<'
    else:
        pages = math.ceil(total / page_size)
        if 0 <= index < pages:
            cur_page = result_list[index * page_size: (index + 1) * page_size]
        elif index == pages - 1:
            cur_page = result_list[index * page_size:]
        else:
            return server.reply("查询页数超出范围")
        for message in cur_page:
            resp += message + '\n'
        resp += f'&r>>>>>> 第{index + 1}页/共{pages}页 <<<<<<'
    return server.reply(replace_code(resp))

def add_welcome_message(server, context):
    if __mcdr_.get_permission_level(context['player']) < 3:
        return server.reply(replace_code(f'&c你没有权限添加消息喵~'))
    message = context['text']
    message_list = load_config()
    message_list['messages'].append(message)
    with open(config_path, 'w') as file:
        json.dump(message_list, file, indent=4)
    return server.reply(replace_code(f'添加消息&a{message}&r成功喵~'))

def del_welcome_message(server, context):
    if __mcdr_.get_permission_level(context['player']) < 3:
        return server.reply(replace_code(f'&c你没有权限删除消息喵~'))
    message = context['text']
    message_list = load_config()
    if message in message_list['messages']:
        message_list['messages'].remove(message)
        with open(config_path, 'w') as file:
            json.dump(message_list, file, indent=4)
        return server.reply(replace_code(f'删除消息&a{message}&r成功喵~'))
    else:
        return server.reply(replace_code(f'消息&a{message}&r不存在喵~'))
    
def show_help_info(server):
    for line in help_info.splitlines():
        server.reply(replace_code(line))

#=======================================================================================================================

def replace_code(msg: str) -> str:
    return msg.replace('&', '§')

#=======================================================================================================================

def on_player_joined(server, player):
    message_list = load_config()
    message = random.choice(message_list['messages'])
    message = message.replace('{player}', player)
    server.execute('tellraw @a [{"text":"%s"}]' % replace_code(message))

def on_load(server: PluginServerInterface, old):
    pass
    global __mcdr_
    __mcdr_ = server

    server.register_help_message('!!wm', '欢迎消息插件')

    command_builder = SimpleCommandBuilder()
    command_builder.command('!!wm list', get_welcome_message_list)
    command_builder.command('!!wm list <index>', get_welcome_message_list)
    command_builder.command('!!wm add <text>', add_welcome_message)
    command_builder.command('!!wm del <text>', del_welcome_message)
    command_builder.command('!!wm', show_help_info)
    command_builder.command('!!wm help', show_help_info)
    command_builder.arg('text', Text)
    command_builder.arg('index', Integer)

    command_builder.register(server)




