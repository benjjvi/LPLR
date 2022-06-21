# LPLR (Low Power Letterbox Remover)
# Scan all files in a directory (and keep an eye out for new ones), and
# attempt to remove "letterboxing" from video files.

# Linux Edition

# todo
# finish variable assignment in the main func
# make it better

import checks
import lplrsysinfo
from substring import substring_after as substring
import listmanipulation
from elegant import ElegantExit

import platform
import sys
import os
import pathlib
import hashlib
import ffmpeg
import time


class Limited_FFmpeg:
    def __init__(self, os, nice_limit_level, cpu_limit_percentage, \
    ffmpeg_threads, video_codec="h264", audio_codec="ac3"):
        #Start init
        # save all variables to self
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        self.nice_limit_level = nice_limit_level
        self.cpu_limit_percentage = cpu_limit_percentage
        self.ffmpeg_threads = ffmpeg_threads

        print("Created Limited FFMPEG Object with following variables.")
        print(f"Video Codec: {self.video_codec}")
        print(f"Audio Codec: {self.audio_codec}")
        print(f"Nice Limit Level: {self.nice_limit_level}")
        print(f"CPU Limit Percentage: {self.cpu_limit_percentage}")
        print(f"FFmpeg Threads: {self.ffmpeg_threads}")
        # Run All checks
        checks.os_check(os)
        print("OS Check Fine")
        checks.nice_limit_level_check(nice_limit_level)
        print("Nice Limit Level Fine")
        checks.cpu_limit_percentage_check(cpu_limit_percentage)
        print("CPU Limit Percentage Fine")
        checks.ffmpeg_threads_check(ffmpeg_threads)
        print("FFmpeg Threads Fine")
        checks.video_codec_check(video_codec)
        print("Video Codec Fine")
        checks.audio_codec_check(audio_codec)
        print("Audio Codec Fine")
        
    def detect_crop_ratio(self, inputfile):
        start_frames = "00:00:20" # start scanning at first 20 seconds
        detect_frames = "00:00:02" # 2 seconds after first 20 seconds skipped. 60 frames @30fps, 120 frames @60fps

        #run command

        cmd = f'nice -n {self.nice_limit_level} cpulimit -f -l {self.cpu_limit_percentage} -- ffmpeg -y -threads {self.ffmpeg_threads} -ss {start_frames} -t {detect_frames} -i "{inputfile}" -vf cropdetect -f null - tmp.mp4 > output 2>&1'
        # note for command: some file names may contain a ' for example in the word everybody's. wrapping the command in a '' instead of a """allows us to use the "inside the code
        print(f"Running command \n{cmd}")
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
            x = substring(item, "crop=") #substring gets everything after the provided text from item
            ratios.append(x)

        reccomended_crop = listmanipulation.most_frequent(ratios)
        print(f"Most Seen Crop: {reccomended_crop}")
        
        #cleanup
        print("Starting cleanup.")
        os.system("rm tmp.mp4")
        os.system("rm output")
        print("Finished cleanup.")
        return (inputfile, reccomended_crop)

    def crop(self, inputfile, output, crop):
        #ffmpeg -i input.mp4 -vf crop=1280:720:0:0 -c:a copy output.mp4
        if self.video_codec == "copy" and self.audio_codec == "copy":
            command = f'nice -n {self.nice_limit_level} cpulimit -f -l {self.cpu_limit_percentage} -- ffmpeg -y -threads {self.ffmpeg_threads} -i "{inputfile}" -vf crop={crop} -c:a copy "{output}"'

        else:
            #command = f"nice -n {self.nice_limit_level} cpulimit -f -l {self.cpu_limit_percentage} -- ffmpeg -y -threads {self.ffmpeg_threads} -i '"inputfile}'"-vf crop={crop} -vcodec {self.video_codec} -acodec {self.audio_codec} '"output}"
            command = f'nice -n {self.nice_limit_level} cpulimit -f -l {self.cpu_limit_percentage} -- ffmpeg -y -threads {self.ffmpeg_threads} -i "{inputfile}" -vf crop={crop} -vcodec {self.video_codec} -acodec {self.audio_codec} "{output}'
        print(f"Using command \n{command}")
        os.system(command)
        
                

class Scraper():
    def __init__(self, media_folder):
        self.media_folder = media_folder
        print(f"Assigning media folder to {self.media_folder}")

    def get_all_video_files_in_directory_and_subdirectories(self):
        all_extentions = ["mp4", "mkv"]
        all_files = []
        for extention in all_extentions:
            x = list(pathlib.Path(f"{self.media_folder}").rglob(f"*.{extention}"))
            for item in x:
                all_files.append(str(item)) #turn PosixPath or WindowsPath to string
        print(f"Found a total of {len(all_files)} files in {self.media_folder}.")
        return all_files

    def get_video_width_and_height(self, path):
        probe = ffmpeg.probe(path)
        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]

        video_streams = video_streams[0]
        width = video_streams["coded_width"]
        height = video_streams["coded_height"]

        print(f"Got width and height of {width} x {height} for video {path}.")

        return (width, height)


class Runner():
    def __init__(self, ffmpeg_object, scraper_object, refresh_interval):
        self.ffmpeg_object = ffmpeg_object
        self.scraper_object = scraper_object
        self.refresh_interval = refresh_interval * 60 #min -> sec
        print(f"Refreshing library every {self.refresh_interval} minute(s).")

    def generate_dictionary(self):
        # first, let's do the first scrape of the directory.
        video_files = self.scraper_object.get_all_video_files_in_directory_and_subdirectories()

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
            mini_dict = {"md5": MD5_sum, "cropped_wh": [int(crop_w), int(crop_h)], "real_wh": [int(w), int(h)], "cropdetect": crop}

            print(f"Information for {video_file}")
            print(f"MD5: {MD5_sum}")
            print(f"Cropdetect Crop: {crop_w} x {crop_h}")
            print(f"Real Crop: {w} x {h}")
            print(f"Raw Crop Value: {crop}")
            
            all_scanned_files[video_file] = mini_dict
        return all_scanned_files

    def crop_from_scan(self, all_scanned_files):
        # now, lets go through all the files and try and encode all that need encoding for improper
        #aspect ratios
        for item in all_scanned_files:
            currentdict = all_scanned_files[item]

            if currentdict["cropped_wh"] != currentdict["real_wh"]:
                print(f"{item} does not fit its reccomended aspect ratio.")
                print(f"Attempting to crop {item}.")
                outfilename = item.split("/")
                filename = outfilename[-1]
                del outfilename[-1]
                splitfilename = filename.split(".")
                format = "."+ splitfilename[-1]
                splitfilename.remove(splitfilename[-1])
                splitfilename.append("-CROPPED")
                splitfilename.append(format)

                filename = ""
                for x in outfilename:
                    filename = filename + x + "/"
                for x in splitfilename:
                    filename = filename + x
                print(f"Old File Name: {item}")
                print(f"New File Name: {filename}")
                self.ffmpeg_object.crop(item, filename, currentdict["cropdetect"])

                #once the video is cropped, lets delete the old video and rename the cropped video to the old filename

                print(f"Finished cropping {item}")
                os.remove(item)
                os.system(f"mv '{filename}' '{item}'")
                print(f"Replaced {item} with its cropped version.")

    
    def start(self):
        print("Getting our fresh dictionary.")
        all_scanned_files = self.generate_dictionary()
        print("Submitting all files for crop.")
        self.crop_from_scan(all_scanned_files)

        #now, we can start our timer system.
        running = True
        while running:
            time.sleep(self.refresh_interval)
            print("Getting our fresh dictionary.")
            all_scanned_files = self.generate_dictionary()
            print("Submitting all files for crop.")
            self.crop_from_scan(all_scanned_files)   


############################
###                      ###
###  START MAIN PROGRAM  ###
###                      ###
############################

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

    nll = input("Enter a limit level to use with NICE to set priority.\n-20 is the highest priority, and 19 is the lowest priority.")

    try:
        nll = int(nll)
    except Exception:
        ElegantExit(104)

    if nll < -20 or nll > 19:
        ElegantExit(104)

    

    ffmpeg_object = Limited_FFmpeg(os=platform.system(), \
        nice_limit_level=nll, cpu_limit_percentage=20, ffmpeg_threads=2, \
        video_codec="copy", audio_codec="copy")

    scraper_object = Scraper("./videos")

    runner = Runner(ffmpeg_object, scraper_object, 1) #rescan every x minutes
    try:
        runner.start()
    except Exception:
        print("Exitting.")
        os.system("rm output")
        os.system("rm tmp.mp4")