import requests
import json
import urllib
import datetime
import time

strike_search_url = "https://getstrike.net/api/v2/torrents/search/?phrase="
client_url = 'http://127.0.0.1'
client_port = '8080'
timeout_for_params = 5
num_of_torrents = 8
'''
torrent_emoji = [bot.Emoji.DIGIT_ONE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_TWO_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_THREE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_FOUR_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_FIVE_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_SIX_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_SEVEN_PLUS_COMBINING_ENCLOSING_KEYCAP,
                 bot.Emoji.DIGIT_EIGHT_PLUS_COMBINING_ENCLOSING_KEYCAP]
'''

#example usage
response = requests.get('http://127.0.0.1:8080/query/torrents')
if not response.ok:
    response.raise_for_status()

for torrent in json.loads(response.content):
    if torrent['progress'] >= 0:
        print torrent['name']


def get_days_ago(date_string):
    if " " in date_string:
        parsed = time.strptime(date_string, '%b %d, %Y')
    else:
        parsed = datetime.datetime.fromtimestamp(long(date_string))

    dt = datetime.datetime.fromtimestamp(time.mktime(parsed))
    return (datetime.datetime.now() - dt).days

def parse_config_file():
    pass


def search_torrent(search_term):
    term = urllib.quote(search_term)
    response = requests.get(strike_search_url + term)
    return json.loads(response.content)['torrents'][:num_of_torrents]

def download_torrent():
    pass

def authenticate_user():
    pass

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
        #seeds = best_torrents[i]['seeds']
        #size = sizeof_fmt(int(best_torrents[i]['size']))
        #message = torrent_emoji[i] + best_torrents[i]['torrent_title'] + "\nSeeds: " + best_torrents[i]['seeds'] + ", Size: " #+ sizeof_fmt(int(best_torrents[i]['size'])) + ", "


def cmd_torrent_status():
    pass

def cmd_pause_all_torrents():
    pass

def cmd_resume_all_torrents():
    pass


def main():
    search_term = "iron man 2"
    term = urllib.quote(search_term)

    response = requests.get(strike_search_url + term)

    objects = json.loads(response.content)
    #print objects['torrents']
    '''for o in objects['torrents']:
        date = o['upload_date']
        if " " in date:
            parsed = time.strptime(date, '%b %d, %Y')
            print date, "y:", parsed.tm_year, "m:", parsed.tm_mon, "d:", parsed.tm_mday
        else:
            c = datetime.datetime.fromtimestamp(long(date))
            print "y:", c.year, "m:", c.month, "d:", c.day
        pass
'''
    days = get_days_ago(objects['torrents'][0]['upload_date'])
    print objects['torrents'][0]['upload_date']
    if days < 1:
        time_str = "Today"
    elif days == 1:
        time_str = "Yesterday"
    else:
        time_str = str(days) + " days ago"
    print time_str

    days = get_days_ago(objects['torrents'][1]['upload_date'])
    print objects['torrents'][1
    ]['upload_date']
    if days < 1:
        time_str1 = "Today"
    elif days == 1:
        time_str1 = "Yesterday"
    else:
        time_str1 = str(days) + " days ago"
    print time_str1


    #parse config
    #setup bot commands
    #activate bot
    pass

if __name__ == "__main__":
    main()
