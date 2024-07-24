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
}

# help_info = '''-------- &a Welcome Message &r--------
# &7!!wm help &f- &c显示帮助消息
# &7!!wm list [index] &f- &c显示欢迎消息列表,index代表页数
# &7!!wm add <text> &f- &c添加欢迎消息
# &7!!wm del <text> &f- &c删除欢迎消息
# ------------------------------------
# '''   

def list_welcome_message(server, context):
    if 'index' in context:
        index = context['index'] - 1
    else:
        index = 0
    if index < 0:
        return server.reply(replace_code(_tr('message.page_error')))
    
    global page_size
    message_list = load_config()
    result_list = []
    index = 1
    for message in message_list['messages']:
        result_list.append(f'&r|- &f{index}: &a{message}&r')
        index += 1
    
    total = len(result_list)
    resp = replace_code(_tr('message.header'))

    if total == 0:
        resp += replace_code(_tr('message.footer_zero'))
    else:
        pages = math.ceil(total / page_size)
        if 0 <= index < pages:
            cur_page = result_list[index * page_size: (index + 1) * page_size]
        elif index == pages - 1:
            cur_page = result_list[index * page_size:]
        else:
            return server.reply(replace_code(_tr('message.page_error')))
        for message in cur_page:
            resp += message + '\n'
        resp += replace_code(_tr('message.footer'))
    return server.reply(replace_code(resp))

def add_welcome_message(server, context: PlayerCommandSource):
    if not context.has_permission_higher_than(3):
        return server.reply(replace_code(_tr('command.no_permission_add')))
    message = context['text']
    message_list = load_config()
    message_list['messages'].append(message)
    with open(config_path, 'w') as file:
        json.dump(message_list, file, indent=4)
    return server.reply(replace_code(_tr('command.add_success')))

def del_welcome_message(server, context: PlayerCommandSource):
    if not context.has_permission_higher_than(3):
        return server.reply(replace_code(_tr('command.no_permission_del')))
    index = context['index']
    message_list = load_config()
    if index < 1 or index > len(message_list['messages']):
        return server.reply(replace_code(_tr('message.message_not_found')))
    message = message_list['messages'].pop(index - 1)
    with open(config_path, 'w') as file:
        json.dump(message_list, file, indent=4)
    return server.reply(replace_code(_tr('command.del_success')))
    

def show_help_info(context: PlayerCommandSource):
    server = context.get_server()
    info = context.get_info()
    server.reply(info, "-------- §a Welcome Message §r--------")
    server.reply(info, RText("§7!!wm help§r").set_hover_text(_tr("message.hover_hint") + " §7!!wm help§r").set_click_event(RAction.suggest_command, "!!wm help") + ' ' + _tr("help.help"))
    server.reply(info, RText("§7!!wm add <text>§r").set_hover_text(_tr("message.hover_hint") + " §7!!wm add§r").set_click_event(RAction.suggest_command, "!!wm add ") + ' ' + _tr("help.add"))
    server.reply(info, RText("§7!!wm del <index>§r").set_hover_text(_tr("message.hover_hint") + " §7!!wm del§r").set_click_event(RAction.suggest_command, "!!wm delete") + ' ' + _tr("help.delete"))
    server.reply(info, RText("§7!!wm list [index]§r").set_hover_text(_tr("message.hover_hint") + " §7!!wm list§r").set_click_event(RAction.suggest_command, "!!wm list") + ' ' + _tr("help.list"))
    server.reply(info, "------------------------------------")

def send_message(server: ServerInterface, player: str):
    message_list = load_config()
    if len(message_list['messages']) == 0:
        server.tell(player, _tr('message.empty'))
    else:
        message = random.choice(message_list['messages'])
        message = message.replace('{player}', player)
        server.tell(player, message)

#=======================================================================================================================

def load_config():
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        with open(config_path, 'w') as file:
            json.dump(default_config, file, indent=4)
        return default_config 

def replace_code(msg: str) -> str:
    return msg.replace('&', '§')

def _tr(tag: str, *args):
    _str = PluginServerInterface.get_instance().tr(f'welcome_message.{tag}', *args)
    return _str

#=======================================================================================================================

def on_player_joined(server, player, info):
    send_message(server, player)

def on_load(server: PluginServerInterface, old):

    global __mcdr_
    __mcdr_ = server

    server.register_help_message('!!wm', _tr('register'))

    command_builder = SimpleCommandBuilder()
    command_builder.command('!!wm list', list_welcome_message)
    command_builder.command('!!wm list <index>', list_welcome_message)
    command_builder.command('!!wm add <text>', add_welcome_message)
    command_builder.command('!!wm del <index>', del_welcome_message)
    command_builder.command('!!wm', show_help_info)
    command_builder.command('!!wm help', show_help_info)
    command_builder.arg('text', Text)
    command_builder.arg('index', Integer)

    command_builder.register(server)




