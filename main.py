# LPLR (Low Power Letterbox Remover)
# Scan all files in a directory (and keep an eye out for new ones), and
# attempt to remove "letterboxing" from video files.

# Linux Edition

# TODO list

# limiting
# file grabbing (reuse dikkie fiets code)
# scheduling


import checks
import lplrsysinfo
from substring import substring_after as substring
import listmanipulation

import platform
import sys
import os
import pathlib
import cv2
    

class Limited_FFmpeg:
    def __init__(self, os, nice_limit_level, cpu_limit_percentage, \
    ffmpeg_threads, video_codec="h264", audio_codec="ac3"):
        #Start init
        # save all variables to self
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        # Run All checks
        checks.os_check(os)
        checks.nice_limit_level_check(nice_limit_level)
        checks.cpu_limit_percentage_check(cpu_limit_percentage)
        checks.ffmpeg_threads_check(ffmpeg_threads)
        checks.video_codec_check(video_codec)
        checks.audio_codec_check(audio_codec)
        
    def detect_crop_ratio(self, inputfile):
        start_frames = "00:00:20" # start scanning at first 20 seconds
        detect_frames = "00:00:02" # 2 seconds after first 20 seconds skipped. 60 frames @30fps, 120 frames @60fps

        #run command

        cmd = f"ffmpeg -y -ss {start_frames} -t {detect_frames} -i {inputfile} -vf cropdetect -f null - tmp.mp4 > output 2>&1"
        os.system(cmd)

        #analyse output
        o = open("output", "r")
        output = o.read()
        o.close()
        print(output)
        output = output.split("\n")
        
        cropDetectOutput = []
        for line in output:
            if "cropdetect" in line:
                cropDetectOutput.append(line)
        
        ratios = []
        for item in cropDetectOutput:
            x = substring(item, "crop=")
            ratios.append(x)

        reccomended_crop = listmanipulation.most_frequent(ratios)
        print(f"Reccomending use of crop {reccomended_crop}")

        #cleanup
        os.system("rm tmp.mp4")
        os.system("rm output")
        return (inputfile, reccomended_crop)

    def crop(self, inputfile, output, crop):
        #ffmpeg -i input.mp4 -vf crop=1280:720:0:0 -c:a copy output.mp4
        if self.video_codec == "copy" and self.audio_codec == "copy":
            command = f"ffmpeg -y -i {inputfile} -vf crop={crop} -c:a copy {output}"
        else:
            command = f"ffmpeg -y -i {inputfile} -vf crop={crop} -vcodec {self.video_codec} -acodec {self.audio_codec} {output}"

        os.system(command)
        
                

class Scraper():
    def __init__(self, media_folder):
        self.media_folder = media_folder

    def get_all_video_files_in_directory_and_subdirectories(self):
        all_extentions = ["mp4", "mkv"]
        all_files = []
        for extention in all_extentions:
            x = list(pathlib.Path(f"{self.media_folder}").rglob(f"*.{extention}"))
            for item in x:
                all_files.append(str(item)) #turn PosixPath or WindowsPath to string
        return all_files

    def get_video_width_and_height(self, path):
        vid = cv2.VideoCapture(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

        return (height, width)


class Runner():
    def __init__(self, ffmpeg_object, scraper_object, refresh_interval):
        self.ffmpeg_object = ffmpeg_object
        self.scraper_object = scraper_object
        self.refresh_interval = refresh_interval

    def start(self):
        # first, let's do the first scrape of the directory.
        video_files = self.scraper_object.get_all_video_files_in_directory_and_subdirectories()

        # now, let's try and detect the crop ration for all of these files and transcode them if the crop is different to the original video aspect ratio.
        all_scanned_files = {}
        for video_file in video_files:
            #get crop ration
            inputfile, crop = self.ffmpeg_object.detect_crop_ratio(video_file)
            #minidict = {inputfile, rec_crop, real_crop}

if __name__ == "__main__":
    # Pre-load checks:
    # 1. Help Menu Requested?
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""LPLR - Low Power Letterbox Remover""")
        exit(0)
    
    # 2. SysInfo Requested
    if "--dump" in sys.argv or "-d" in sys.argv:
        print("LPLR prining VERBOSE information now.")
        lplrsysinfo.print_all_sysinfo()
        exit(0)
        
    
    #FFMPEG USAGE
    #inputfile, crop = ffmpeg_object.detect_crop_ratio("videos/example/tste.mp4")
    #print(crop)
    #ffmpegItem.crop("videos/example/tste.mp4", "videos/example/cropped.mp4", crop)

    #SCRAPER USAGE
    #scraper.get_all_video_files_in_directory_and_subdirectories()

    ffmpeg_object = Limited_FFmpeg(os=platform.system(), \
        nice_limit_level=10, cpu_limit_percentage=30, ffmpeg_threads=1, \
        video_codec="copy", audio_codec="copy")

    scraper_object = Scraper("./videos")
    
    inputfile, crop = ffmpeg_object.detect_crop_ratio("videos/example/tste.mp4")
    print(crop)

    scraper_object.get_video_width_and_height()

    

    #runner = Runner(ffmpeg_object, scraper_object, 60*60) #hourly
    #runner.start()