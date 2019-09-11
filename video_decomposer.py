import glob
import os
import ffmpy

input_directory = "video_download"
output_directory = "video_decompose"
os.mkdir(output_directory)

video_files = glob.glob(f"{input_directory}/*.mp4")
for video_file in video_files:
    video_number = video_file.split(os.sep)[-1].split(".")[0]
    video_output_dir = f"{output_directory}/{video_number}/"
    os.mkdir(video_output_dir)
    print(f"Converting video: {video_file}")
    ff = ffmpy.FFmpeg(
        inputs={video_file: None},
        outputs={f"{output_directory}/{video_number}/out%d.png": "-vf fps=5 -vsync 0"}
    )
    ff.run()
