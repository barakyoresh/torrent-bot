import requests
import json
import urllib
import datetime
import time
import bot_framework
import xml.etree.ElementTree as ET
from dateutil.relativedelta import relativedelta

bot = None
strike_search_url = "https://getstrike.net/api/v2/torrents/search/?phrase="
CONFIG_FILE = 'config.xml'
client_url = 'http://127.0.0.1'
client_port = '8080'
timeout_for_params = 5
client_user = 'admin'
client_pass = 'password'
telegram_token = None
num_of_torrents = 8
torrent_emoji = [bot_framework.Bot.Emoji.DIGIT_ONE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_TWO_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_THREE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_FOUR_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_FIVE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_SIX_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_SEVEN_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot_framework.Bot.Emoji.DIGIT_EIGHT_PLUS_COMBINING_ENCLOSING_KEYCAP]


auth_telegram_users = []

'''
#example usage
response = requests.get('http://127.0.0.1:8080/query/torrents')
if not response.ok:
    response.raise_for_status()

for torrent in json.loads(response.content):
    if torrent['progress'] >= 0:
        print torrent['name']
'''

def eta_fmt(seconds):
    if seconds <= 0:
        return '0'
    if seconds >= 8640000:
        return 'inf' #return u'\u221e'.encode('utf-8')
    delta = relativedelta(seconds=seconds)
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    times = ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
        for attr in attrs if getattr(delta, attr)]
    return times[0] + (', ' + times[1] if len(times) > 1 else '')


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def get_days_ago(date_string):
    if " " in date_string:
        parsed = time.strptime(date_string, '%b %d, %Y')
    else:
        parsed = datetime.datetime.fromtimestamp(long(date_string))

    dt = datetime.datetime.fromtimestamp(time.mktime(parsed))
    return (datetime.datetime.now() - dt).days


def parse_config_file():
    global client_url, client_port, client_user, client_pass, telegram_token
    tree = ET.parse(CONFIG_FILE)

    #client data
    client_data = tree.find('client_data');
    client_url = client_data.find('url').text
    client_port = client_data.find('port').text
    client_user = client_data.find('user').text
    client_pass = client_data.find('pass').text

    #telegram data
    telegram_token = tree.find('telegram_token').text
    for user_id in tree.iter('telegram_user_id'):
        auth_telegram_users.append(user_id.text)



def search_torrent(search_term):
    term = urllib.quote(search_term)
    response = requests.get(strike_search_url + term)
    return json.loads(response.content)['torrents'][:num_of_torrents]

def download_torrent():
    pass

def authenticate_user(message):
    if str(message.chat.id) in auth_telegram_users:
        return True
    else:
        bot.send_message(message.chat_id, ("Unauthorized user %s %s, user id: %s. Please edit bot configuration file using an authenticated account to change this." % (message.chat.first_name,
                                          message.chat.last_name, message.chat.id)))
        return False

def cmd_search_torrent(message, params_text):
    #authenticate user
    if not authenticate_user(message):
        return

    #check if params are legal
    if not params_text:
        param_msg, params = bot.wait_for_message(message.chat_id, timeout_for_params)
        if not params:
            bot.send_message(message.chat_id, "No search parameters received - aborting operation")
            return

    best_torrents = search_torrent(params_text)
    print_torrent_options(best_torrents)

def print_torrent_options(best_torrents):
    for i in range(num_of_torrents):
        days = get_days_ago(best_torrents[i]['upload_time'])
        if days < 1:
            time_str = "Today"
        elif days == 1:
            time_str = "Yesterday"
        else:
            time_str = str(days) + " days ago"
        seeds = best_torrents[i]['seeds']
        size = sizeof_fmt(int(best_torrents[i]['size']))
        message = torrent_emoji[i] + best_torrents[i]['torrent_title'] + "\nSeeds: " + seeds + ", Size: " + size + ", Upload time: " + time_str
        


def cmd_torrent_status(message, param_text):
    if not authenticate_user(message):
        return

    include_complete = False
    list_entires = 50

    #handle secret params
    if param_text:
        # number - limit entry count
        try:
            list_entires = abs(int(param_text))
        except:
            pass

        # include complete torrents
        print param_text
        if param_text == 'complete':
            include_complete = True

    #get list
    response = requests.get(client_url + ':' + client_port + '/query/torrents')
    if not response.ok:
        response.raise_for_status()

    torrent_list = ''
    for torrent in json.loads(response.content):
        if torrent['progress'] < 1 or include_complete:
            torrent_list += '%s - %s (%s) speed:%s eta:%s status:%s\n' % (torrent['name'], str(int(torrent['progress'] * 100)) + '%',
                                (sizeof_fmt(torrent['size'] * torrent['progress']) + '/' + sizeof_fmt(torrent['size'])),
                                sizeof_fmt(torrent['dlspeed'], 'B/s'), eta_fmt(int(torrent['eta'])), torrent['state'])

    #print list to user
    bot.send_message(message.chat_id, torrent_list)



def cmd_pause_all_torrents(): #me
    pass

def cmd_resume_all_torrents(): #me
    pass


def main():
    global bot
    #parse config file
    parse_config_file()
    #setup bot commands
    bot = bot_framework.Bot(token = telegram_token)
    bot.add_command(cmd_name='/status', cmd_cb=cmd_torrent_status, cmd_description='Show a list of current torrents, use "/status <number>" to limit list size and "/status complete" to see finished torrents as well')
    #activate bot
    bot.activate()




'''
def callback(message, params):
    bot.send_message(chat_id=message.chat_id, message=bot.Emoji.DI)
    if not params:
        bot.send_message(chat_id=message.chat_id, message='wrong params %s, put in number - ' % message.chat.first_name)
        msg, params = bot.wait_for_message(chat_id=message.chat_id, timeout=10)

    if not params:
        params = 'none'
    print 'params - ', params
    bot.send_message(chat_id=message.chat_id, message='%s ? kthxbye' % params)
'''


if __name__ == "__main__":
    main()
