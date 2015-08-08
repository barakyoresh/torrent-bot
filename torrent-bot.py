import requests
import json

client_url = 'http://127.0.0.1'
client_port = '8080'

#example usage
response = requests.get('http://127.0.0.1:8080/query/torrents')
if not response.ok:
    response.raise_for_status()

for torrent in json.loads(response.content):
    if torrent['progress'] >= 0:
        print torrent['name']


def parse_config_file():
    pass

def search_torrent():
    pass

def download_torrent():
    pass

def authenticate_user():
    pass

def cmd_search_torrent():
    pass

def cmd_torrent_status():
    pass

def cmd_pause_all_torrents():
    pass

def cmd_resume_all_torrents():
    pass


def main():
    #parse config
    #setup bot commands
    #activate bot
    pass

if __name__ == "__main__":
    main()
