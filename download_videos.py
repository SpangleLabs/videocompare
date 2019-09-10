from telethon import TelegramClient
from tqdm import tqdm


# These example values won't work. You must get your own api_id and
# api_hash from `my.telegram.org` , under API Development.
api_id = APIID
api_hash = 'APIHASH'
client = TelegramClient('session_name', api_id, api_hash)
client.start()
print(client.get_me().stringify())

messages = client.get_messages('deergifs', limit=2000)
print(len(messages))
for msg in tqdm(messages):
    client.download_media(msg)
