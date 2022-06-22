# LPLR: Low Powered Letterbox Remover

[View LPLR on replit.com](https://replit.com/@bildsben/LPLR)

[View a demonstration of LPLR on Replit](https://youtu.be/pz9v0jDWZGM)


## Who?
Built by me (bildsben).

## What?
Low Powered Letterbox Remover (abbreviated to LPLR) is a standalone program designed to run in the background of a **LINUX** server 24/7 and analyse all the video files in a certain directory and all subdirectories, and detect the recommendedcrop for each of these videos.
### Side Note- What is the Letterbox effect on a video?
The letterbox effect occurs when a video is filmed in an aspect ratio such as 16:9, but the video contents are actually in a different aspect ratio (e.g 4:3). This often occurs when videos have been downloaded from the internet where the owner of the video expects a specific aspect ratio. This causes black bars on the top and bottom, sides, or both top bottom and sides of videos. An example is shown below.

![A screenshot of a video with the letterboxing effect at the top and bottom of the screen.](https://pbblogassets.s3.amazonaws.com/uploads/2016/05/Free-Letterbox-Templates.jpg)
## Where?
This program is designed to work on LINUX systems only. This MAY work on Windows and Linux if you are able to install your systems version of [UNIX's nice](https://en.wikipedia.org/wiki/Nice_%28Unix%29) and [cpulimit](https://github.com/opsengine/cpulimit).
## When?
This program was made in 3 days, hence the absolute spaghetti code.
## Why?
Many people such as me have [a Plex Media Server](https://www.plex.tv/en-gb/media-server-downloads/?langr=1) running on their linux machines. Some people use software to rip videos from DVDs to put on these servers, but sometimes, these programs can letterbox videos, either on purpouse or an accidental code design. Other times, people may download videos from archive websites such as [archive.org](https://archive.org/), which may sometimes have poorly cropped videos.

## Note
It is important to note that, while it works for my machine in the way the program comes, you may need to tweak the ```main.py``` file. It is highly reccomended to only modify this if you have been told to, or if you know what you are doing.

If you encounter any errors when trying to run the file, please do not hesitate to reach out to me. You can email me at [ben {at} bildsben {dot} com](mailto:ben@bildsben.com). I will try my best to help you with any issues. In addition, you could [open a new issue](https://github.com/bildsben/LPLR/issues), and I can try my best to help you out with whatever problems you are facing.

