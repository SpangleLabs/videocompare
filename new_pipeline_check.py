from telethon.sync import TelegramClient
import os
import glob
import json
import ffmpy
from PIL import Image
import imagehash

config = {
    "gif_channel": "deergifs",
    "buffer_group": -366227945,
    "api_id": ,
    "api_hash": ''
}
hash_store = f"{config['gif_channel']}/hashes.json"
try:
    with open(hash_store, "r") as f:
        store = json.load(f)
except FileNotFoundError:
    store = {"scanned_videos": [], "hashes": {}}

dir_video = f"{config['gif_channel']}/video_download"
dir_images = f"{config['gif_channel']}/video_decompose"
dir_buffer = f"{config['gif_channel']}/buffer"
dir_buffer_video = f"{dir_buffer}/video_download"
dir_buffer_images = f"{dir_buffer}/video_decompose"

for path in [config['gif_channel'], dir_video, dir_images, dir_buffer, dir_buffer_video, dir_buffer_images]:
    if not os.path.exists(path):
        os.mkdir(path)

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
    path = f"{dir_video}/{message.id.zfill(4)}.{file_ext}"
    if not os.path.exists(path):
        print("Downloading message: {}".format(message))
        client.download_media(message=message, file=path)

# # # Decompose missing
video_files = glob.glob(f"{dir_video}/*.mp4")
for video_file in video_files:
    video_number = video_file.split(os.sep)[-1].split(".")[0]
    video_output_dir = f"{dir_images}/{video_number}/"
    if not os.path.exists(video_output_dir):
        os.mkdir(video_output_dir)
        print(f"Converting video: {video_file}")
        ff = ffmpy.FFmpeg(
            inputs={video_file: None},
            outputs={f"{dir_images}/{video_number}/out%d.png": "-vf fps=5 -vsync 0"}
        )
        ff.run()

# # # Create huge hash directory
for image_directory in glob.glob(f"{dir_images}/*/"):
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
buffer_entity = client.get_entity(config['buffer_group'])
for message in client.iter_messages(buffer_entity):
    if message.file is None:
        # print(f"No file, skipping message: {message}")
        continue
    file_ext = message.file.mime_type.split("/")[-1]
    path = f"{dir_buffer_video}/{message.id.zfill(4)}.{file_ext}"
    if not os.path.exists(path):
        print("Downloading message from buffer: {}".format(message))
        client.download_media(message=message, file=path)

# # # Decompose videos from buffer chat
video_files = glob.glob(f"{dir_buffer_video}/*.mp4")
for video_file in video_files:
    video_number = video_file.split(os.sep)[-1].split(".")[0]
    video_output_dir = f"{dir_buffer_images}/{video_number}/"
    if not os.path.exists(video_output_dir):
        os.mkdir(video_output_dir)
        print(f"Converting buffer video: {video_file}")
        ff = ffmpy.FFmpeg(
            inputs={video_file: None},
            outputs={f"{dir_buffer_images}/{video_number}/out%d.png": "-vf fps=5 -vsync 0"}
        )
        ff.run()

# # # Check for hashes which already exist
duplicates = []

for image_directory in glob.glob(f"{dir_buffer_images}/*/"):
    post_number = image_directory.strip(os.sep).split(os.sep)[-1]
    video_hashes = {}
    # Build map of image hashes for that directory
    for image_file in glob.glob(f"{image_directory}/*.png"):
        image = Image.open(image_file)
        image_hash = imagehash.average_hash(image)
        video_hashes[image_hash] = post_number
    # Merge that into all hashes, checking for duplicates
    duplicate_counts = {}
    for image_hash in video_hashes:
        if image_hash in store['hashes']:
            if store['hashes'] not in duplicate_counts:
                duplicate_counts[store['hashes']] = 0
            duplicate_counts[store['hashes']] += 1
        store['hashes'] = f"buffer-{video_hashes[image_hash]}"
    # Check out the duplicate counts
    for other_image in duplicate_counts:
        if duplicate_counts[other_image] >= 3:
            duplicates.append((post_number, other_image))
# Output all duplicates.


def url_from_post_number(post_id):
    return f"https://t.me/{config['gif_channel']}/{post_id}"


print("----")
print(f"Found these duplicates:")
for duplicate in duplicates:
    print(f"Post ID {duplicate[0]} in buffer - {url_from_post_number(duplicate[1])}")
