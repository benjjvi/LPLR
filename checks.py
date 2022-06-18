import psutil
from elegant import ElegantExit

def os_check(os):
    if os != "Linux":
        ElegantExit(101)

def nice_limit_level_check(nice_limit_level):
    if nice_limit_level < -20 or nice_limit_level > 19:
        ElegantExit(102)

def cpu_limit_percentage_check(cpu_limit_percentage):
    if cpu_limit_percentage < 5 or cpu_limit_percentage > 100:
        ElegantExit(102)

def ffmpeg_threads_check(ffmpeg_threads):
    if ffmpeg_threads > psutil.cpu_count():
        ElegantExit(103)

def video_codec_check(video_codec):
    video_codecs = ["h261", "h263", "h263i", "h264p", "h264", "hevc", "mpeg1video", "mpeg2video", "mpeg4", "vp8", "vp9", "wmv3", "copy"]
    if video_codec not in video_codecs:
        ElegantExit(104)
    
def audio_codec_check(audio_codec):
    audio_codecs = ["aac", "ac3", "alac", "mp1", "mp2", "mp3", "mp4als", "opus", "vorbis", "wmalossless", "wmapro", "wmav1", "wmav2", "copy"]
    if audio_codec not in audio_codecs:
        ElegantExit(104)