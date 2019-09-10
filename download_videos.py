from telethon.sync import TelegramClient


directory = "video_download"
# These example values won't work. You must get your own api_id and
# api_hash from `my.telegram.org` , under API Development.
api_id = APIID
api_hash = 'APIHASH'
client = TelegramClient('deer_gifs_downloader', api_id, api_hash)
client.start()
# print(client.get_me())

channel_username = 'deergifs'
channel_entity = client.get_entity(channel_username)
for message in client.iter_messages(channel_entity):
    print("Downloading message: {}".format(message))
    file_ext = message.file.mime_type.split("/")[-1]
    path = f"{directory}/{message.id}.{file_ext}"
    client.download_media(message=message, file=path)
