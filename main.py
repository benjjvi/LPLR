# LPLR (Low Power Letterbox Remover)
# Scan all files in a directory (and keep an eye out for new ones), and
# attempt to remove "letterboxing" from video files.

# Linux Edition

# TODO list

# ffmpeg -i input.mp4 -vf crop=1280:720:0:0 -c:a copy output.mp4
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

    def crop(self, input, output, crop):
        #ffmpeg -i input.mp4 -vf crop=1280:720:0:0 -c:a copy output.mp4
        if self.video_codec == "copy" and self.audio_codec == "copy":
            command = f"ffmpeg -y -i {inputfile} -vf crop={crop} -c:a copy {output}"
        else:
            command = f"ffmpeg -y -i {inputfile} -vf crop={crop} -vcodec {self.video_codec} -acodec {self.audio_codec} {output}"

        os.system(command)
        
                

        


ffmpegItem = Limited_FFmpeg(os=platform.system(), nice_limit_level=10, cpu_limit_percentage=30, ffmpeg_threads=1, video_codec="copy", audio_codec="copy")

inputfile, crop = ffmpegItem.detect_crop_ratio("videos/example/tste.mp4")
print(crop)

ffmpegItem.crop("videos/example/tste.mp4", "videos/example/cropped.mp4", crop)