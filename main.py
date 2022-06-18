# LPLR (Low Power Letterbox Remover)
# Scan all files in a directory (and keep an eye out for new ones), and
# attempt to remove "letterboxing" from video files.

# Linux Edition

# TODO list

# limiting (https://stackoverflow.com/questions/4565567/how-can-i-limit-ffmpeg-cpu-usage)
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
import hashlib
import ffmpeg


class Limited_FFmpeg:
    def __init__(self, os, nice_limit_level, cpu_limit_percentage, \
    ffmpeg_threads, video_codec="h264", audio_codec="ac3"):
        #Start init
        # save all variables to self
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        self.nice_limit_level = nice_limit_level
        self.cpu_limit_percentage = cpu_limit_percentage
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
        probe = ffmpeg.probe(path)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]

        video_streams = video_streams[0]
        width = video_streams["coded_width"]
        height = video_streams["coded_height"]

        return (width, height)


class Runner():
    def __init__(self, ffmpeg_object, scraper_object, refresh_interval):
        self.ffmpeg_object = ffmpeg_object
        self.scraper_object = scraper_object
        self.refresh_interval = refresh_interval

    def start(self):
        # first, let's do the first scrape of the directory.
        video_files = self.scraper_object.get_all_video_files_in_directory_and_subdirectories()

        #check if we have already scanned files.
        if not os.path.exists("video_data.dict"):
            # lets detect the real and recommended ratio for these files. 
            #let's also get an MD5 sum and store that with the file geometry
            all_scanned_files = {}
            for video_file in video_files:
                #get crop ratio from ffmpeg
                inputfile, crop = self.ffmpeg_object.detect_crop_ratio(video_file)
                del inputfile #stop confusion
                crop_w = crop.split(":")[0]
                crop_h = crop.split(":")[1]
                
                #get the files real aspect w and h
                w, h = scraper_object.get_video_width_and_height(video_file)
    
                #get MD5 sum
                MD5_sum = hashlib.md5(open(video_file, "rb").read()).hexdigest()
                MD5_sum = str(MD5_sum)
                #store everything
                mini_dict = {"md5": MD5_sum, "cropped_wh": [crop_w, crop_h], "real_wh": [w, h]}
                
                all_scanned_files[video_file] = mini_dict
    
            #lets save our new dictionary to a file incase everything goes to shit here
            with open("video_data.dict", "w") as file:
                file.write(str(all_scanned_files))
        else: #if the dictionary does exist
            with open("video_data.dict", "r") as file:
                all_scanned_files = eval(file.read())
        

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

    #1. DETECTING CROP
    #inputfile, crop = ffmpeg_object.detect_crop_ratio("videos/example/tste.mp4")

    #2. CROPPING VIDEO
    #ffmpegItem.crop("videos/example/tste.mp4", "videos/example/cropped.mp4", crop)

    #3. DETECTING CROP, EXTRACTING WIDTH AND HEIGHT, AND PRINTING TO CONSOLE
    #inputfile, crop = ffmpeg_object.detect_crop_ratio("videos/example/tste.mp4")
    #w = crop.split(":")[0]
    #h = crop.split(":")[1]
    #print(w, h)

    #SCRAPER USAGE
    #1. GET ALL THE VIDEO FILES IN A DIRECTORY AND SUBDIRECTORIES BASED ON THE PATH INPUT WHEN CREATING THE SCRAPER OBJECT
    #scraper.get_all_video_files_in_directory_and_subdirectories()
        
    #2. GET WIDTH AND HEIGHT OF A VIDEO (INCLUDING LETTERBOXING)
    #w, h = scraper_object.get_video_width_and_height("videos/example/tste.mp4")
    #w = int(w)
    #h = int(h)
    #print(w, h)

    ffmpeg_object = Limited_FFmpeg(os=platform.system(), \
        nice_limit_level=10, cpu_limit_percentage=30, ffmpeg_threads=1, \
        video_codec="copy", audio_codec="copy")

    scraper_object = Scraper("./videos")

    runner = Runner(ffmpeg_object, scraper_object, 60*60) #rescan hourly
    runner.start()