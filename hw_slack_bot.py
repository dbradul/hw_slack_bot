import requests
import urllib
import json
import os
import time
import importlib
import hw_test_runner
import sys
import urllib
import pprint
import re
import html
import string
from slackclient import SlackClient

import hw_current_task


#-------------------------------------------------------------------------
CHECK_HW_COMMAND = "check"
HELP_HW_COMMAND  = "help"
ECHO_HW_COMMAND  = "echo"
TIMEOUT_CODE_RUN_SEC = 5

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

_users = []


#-------------------------------------------------------------------------
def print_channels():
    api_call = slack_client.api_call("channels.list")
    if api_call.get('ok'):
        channels = api_call.get('channels')
        for channel in channels:
            print("'%s':'%s'" % (channel["id"], channel["name"]))
            # print("'%s':'%s'" % (user["id"], user["name"]))
            for k, v in channel.items():
                print("\t%-20s:\t%s" %(k, v))


#-------------------------------------------------------------------------
def print_users():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            print("{'id': '%s', 'name': '%s'}," % (user["id"], user["name"]))
            # for k, v in user.items():
            #     print("\t%-20s:\t%s" %(k, v))


# -------------------------------------------------------------------------
def _fetch_users(slack_client):
    global _users
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        _users = api_call.get('members')


# -------------------------------------------------------------------------
def get_user_by_id(user_id):
    for user in _users:
        if user['id'] == user_id:
            return user
    return {}


#-------------------------------------------------------------------------
def sanitize(code):

    while "  " in code:
        code = code.replace("  ", " ")

    prohibited_modules = [
        'os',
        'sys',
        'shutil',
        'io',
        'pickle',
        'socket',
        'webbrowser',
        'html',
        'email',
        'code',
        'sysconfig',
        'urllib',
        'cgi',
        'requests',
        'threading',
        'mutliprocessing',
        'sched',
        'inspect'
    ]

    prohibited_lines  = ['from ' + module for module in prohibited_modules]
    prohibited_lines += ['import ' + module for module in prohibited_modules]

    for line in prohibited_modules:
        if line in code:
            raise Exception("Unsafe code: " + line)


#-------------------------------------------------------------------------
def handle_command(command, channel, user_id):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    #if not get_user_by_id(user_id).get('name'):
    response = "Hi, %s!\n" % get_user_by_id(user_id).get('name')#[user['name'] for user in ALLOWED_USERS if user['id'] == user_id][0]
    response += "Unfortunately, coudln't get what you meant. Please, use the *" + HELP_HW_COMMAND + \
               "* to get help."
    kwargs = {}

    if command.startswith(CHECK_HW_COMMAND):
    #if isinstance(command, dict):#.startswith(CHECK_HW_COMMAND):
        try:
            command_lst = command.split("\n")
            global hw_current_task
            hw_current_task = importlib.reload(hw_current_task)
            lst_task_code_line1 = re.split("[ (]",command_lst[2])
            task_id = int(command_lst[1])
            func_name = "%s_%d_%s" % (lst_task_code_line1[1], task_id, user_id)
            hw_current_task.code += "def " + func_name + "(" + "".join(lst_task_code_line1[2:]) + "\n"
            hw_current_task.code += html.unescape("\n".join(command_lst[3:]))
            hw_current_task.code += ("\nTASKS['%s'] = {%d : %s}" % (user_id, task_id, func_name))

            sanitize(hw_current_task.code)
            print(hw_current_task.code)

            global hw_test_runner
            hw_test_runner = importlib.reload(hw_test_runner)
            response, error = hw_test_runner.run_code(task_id, user_id)
            if error:
                response = ":x: Runtime ERROR:\n" \
                           "```\n%s\n```" % error

        except Exception as error:
            print("Unexpected error:", sys.exc_info()[0])
            response = ":x: Unexpected ERROR:\n" \
                       "```\n%s\n```" % error

        except:
            print("Unexpected error:", sys.exc_info()[0])
            response = ":x: Unexpected ERROR:\n" \
                       "```\n%s\n```" % sys.exc_info()[0]

    elif command.startswith(ECHO_HW_COMMAND):
        import string
        response = command.replace("echo", "").replace("echo:", "").strip()

    elif command == HELP_HW_COMMAND:
        response = ":information_source: HELP:```\n"\
        "echo <msg>   - prints message back to you\n" \
        "help         - prints this help\n" \
        "check \n<task_id>\n<task_code>\n" \
        "             - checks h/w <task_id>\n" \
        "```"
        kwargs['attachments'] = '[{"image_url": "http://imgur.com/tEWkcW3l.png",\
                                   "thumb_url": "http://example.com/path/to/thumb.png"},]'

        # "check hw: attach code snippet with [+] button (on the left <<<)\n" \

    kwargs['text'] = response

    slack_client.api_call("chat.postMessage", channel=channel,
                          as_user=True,
                          **kwargs)

    if hw_test_runner.STOP_PROCESS:
        print("\nExiting bot...")
        sys.exit(-1)

#-------------------------------------------------------------------------
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    #pprint.pprint(slack_rtm_output)
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:

            channel = None
            text = None
            user = None

            if 'subtype' in output and output['subtype'] == 'message_changed':
                channel = output.get('channel')
                message = output.get('message')
            else:
                message = output

            text = message.get('text')
            user = message.get('user')

            if not channel:
                channel = message.get('channel')

            if user and text and channel:
                if not get_user_by_id(user).get('is_bot'):
                    return text, channel, user

    return None, None, None


#-------------------------------------------------------------------------
if __name__ == "__main__":

    _fetch_users(slack_client)

    READ_WEBSOCKET_DELAY = 0.3  # 1 second delay between reading from firehose

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            #print(slack_client.rtm_read())
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel and user:
                print("\n'%s' from user '%s'\n" % (command, user))
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
