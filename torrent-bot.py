import requests
import json
import xml.etree.ElementTree as ET
from dateutil.relativedelta import relativedelta

bot = None

CONFIG_FILE = 'config.xml'
client_url = 'http://127.0.0.1'
client_port = '8080'
client_user = 'admin'
client_pass = 'password'

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


def parse_config_file():
    global client_url, client_port, client_user, client_pass
    tree = ET.parse(CONFIG_FILE)

    #client data
    client_data = tree.find('client_data');
    client_url = client_data.find('url').text
    client_port = client_data.find('port').text
    client_user = client_data.find('user').text
    client_pass = client_data.find('pass').text

    #telegram data
    for user_id in tree.iter('telegram_user_id'):
        auth_telegram_users.append(user_id.text)



def search_torrent():
    pass

def download_torrent():
    pass

def authenticate_user(message):
    if message.chat.id in auth_telegram_users:
        return True
    else:
        bot.send_message(message.chat_id, "Unauthorized user %s %s, user id: %s. Please edit bot configuration file "
                                          "using an authenticated account to change this." % message.chat.first_name,
                                          message.chat.last_name, message.chat.id)
        return False

def cmd_search_torrent():
    pass

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
    #parse config file
    parse_config_file()
    #setup bot commands
    #activate bot


if __name__ == "__main__":
    main()
