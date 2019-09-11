from PIL import Image
import imagehash
import glob

images_directory = "video_decompose"
all_hashes = {}

for image_directory in glob.glob(f"{images_directory}/*/"):
    print(image_directory)
    video_hashes = {}
    # Build map of image hashes for that directory
    for image_file in glob.glob(f"{image_directory}/*.png"):
        # print(f"File: {image_file}")
        image = Image.open(image_file)
        image_hash = imagehash.average_hash(image)
        # print(image_hash)
        video_hashes[image_hash] = image_directory
    # Merge that into all hashes, checking for duplicates
    for image_hash in video_hashes:
        if image_hash in all_hashes:
            print(f"DUPLICATE POTENTIALLY FOUND? "
                  f"does {all_hashes[image_hash]} match {video_hashes[image_hash]}?")
        all_hashes[image_hash] = video_hashes[image_hash]




"""
Run through directory recursively, hashing all images.
Build structure like:
{hash: video number}
Build for all images in a hash first, allow overlap. Then copy to big structure
If hash already exists in big structure, warn about collision
"""
