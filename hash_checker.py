import os
from PIL import Image
import imagehash
import glob

images_directory = "video_decompose"
channel_name = "deergifs"

all_hashes = {}
duplicates = []


def url_from_post_number(post_id):
    return f"https://t.me/s/{channel_name}/{post_id}"


for image_directory in glob.glob(f"{images_directory}/*/"):
    print(image_directory)
    post_number = image_directory.strip(os.sep).split(os.sep)[-1]
    video_hashes = {}
    # Build map of image hashes for that directory
    for image_file in glob.glob(f"{image_directory}/*.png"):
        # print(f"File: {image_file}")
        image = Image.open(image_file)
        image_hash = imagehash.average_hash(image)
        # print(image_hash)
        video_hashes[image_hash] = post_number
    # Merge that into all hashes, checking for duplicates
    duplicate_counts = {}
    for image_hash in video_hashes:
        if image_hash in all_hashes:
            print(f"DUPLICATE POTENTIALLY FOUND? "
                  f"does {all_hashes[image_hash]} match {video_hashes[image_hash]}?")
            if all_hashes[image_hash] not in duplicate_counts:
                duplicate_counts[all_hashes[image_hash]] = 0
            duplicate_counts[all_hashes[image_hash]] += 1
        all_hashes[image_hash] = video_hashes[image_hash]
    # Check out the duplicate counts
    for other_image in duplicate_counts:
        if duplicate_counts[other_image] >= 3:
            duplicates.append((post_number, other_image))
# Output all duplicates.
print("----")
print(f"Found these duplicates:")
for duplicate in duplicates:
    print(f"{url_from_post_number(duplicate[0])} - {url_from_post_number(duplicate[1])}")


"""
Run through directory recursively, hashing all images.
Build structure like:
{hash: video number}
Build for all images in a hash first, allow overlap. Then copy to big structure
If hash already exists in big structure, warn about collision
"""
