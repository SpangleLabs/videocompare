from telethon.sync import TelegramClient
import os
import glob
import json
import ffmpy
from PIL import Image
import imagehash

config = {
    "gif_channel": "deergifs",
    "api_id": ,
    "api_hash": ''
}
hash_store = f"{config['gif_channel']}/hashes.json"
try:
    with open(hash_store, "r") as f:
        store = json.load(f)
except FileNotFoundError:
    store = {"scanned_videos": [], "hashes": {}}

directory_video = f"{config['gif_channel']}/video_download"
directory_images = f"{config['gif_channel']}/video_decompose"

if not os.path.exists(config['gif_channel']):
    os.mkdir(config['gif_channel'])
if not os.path.exists(directory_video):
    os.mkdir(directory_video)
if not os.path.exists(directory_images):
    os.mkdir(directory_images)

# # # Download missing videos from gif channel
client = TelegramClient('duplicate_checker', config['api_id'], config['api_hash'])
client.start()
channel_username = config['gif_channel']
channel_entity = client.get_entity(channel_username)
for message in client.iter_messages(channel_entity):
    if message.file is None:
        # print(f"No file, skipping message: {message}")
        continue
    file_ext = message.file.mime_type.split("/")[-1]
    path = f"{directory_video}/{message.id.zfill(4)}.{file_ext}"
    if not os.path.exists(path):
        print("Downloading message: {}".format(message))
        client.download_media(message=message, file=path)

# # # Decompose missing
video_files = glob.glob(f"{directory_video}/*.mp4")
for video_file in video_files:
    video_number = video_file.split(os.sep)[-1].split(".")[0]
    video_output_dir = f"{directory_images}/{video_number}/"
    if not os.path.exists(video_output_dir):
        os.mkdir(video_output_dir)
        print(f"Converting video: {video_file}")
        ff = ffmpy.FFmpeg(
            inputs={video_file: None},
            outputs={f"{directory_images}/{video_number}/out%d.png": "-vf fps=5 -vsync 0"}
        )
        ff.run()

# # # Create huge hash directory
for image_directory in glob.glob(f"{directory_images}/*/"):
    post_number = image_directory.strip(os.sep).split(os.sep)[-1]
    # Skip already hashed videos, add to list otherwise
    if post_number in store['scanned_videos']:
        continue
    else:
        store['scanned_videos'].append(post_number)
    # Add new hashes
    for image_file in glob.glob(f"{image_directory}/*.png"):
        image = Image.open(image_file)
        image_hash = imagehash.average_hash(image)
        store['hashes'][image_hash] = post_number

# # # Save huge hash directory
with open(hash_store, "w+") as f:
    json.dump(store, f)

# # # Download videos in buffer chat
# # # Decompose videos from buffer chat
# # # Check for hashes which already exist