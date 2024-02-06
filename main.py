import tkinter.filedialog
from tkinter import *
from PIL import Image, ImageTk
import cv2
from pygame import mixer
import subprocess


def rewind(num: int) -> None:
    global frames_played
    global seconds
    global minutes
    if (frames_played + num * fps >= video.get(cv2.CAP_PROP_FRAME_COUNT)):
        return
    video.set(cv2.CAP_PROP_POS_FRAMES, frames_played + num * fps)
    seconds += num
    if (seconds < 0):
        seconds = 60 + seconds
        minutes -= 1
    if (minutes < 0):
        minutes = 0
        seconds = 0
    if (seconds > 60):
        seconds -= 60
        minutes += 1
    frames_played += num * fps
    if (frames_played < 0):
        frames_played = 0
    mixer.music.play(start=(seconds + minutes * 60))
    if paused:
        mixer.music.pause()


def new_slider_val(num: str) -> None:
    global delayed
    new_var = (int(video.get(cv2.CAP_PROP_FRAME_COUNT)) * float(num)) - frames_played
    rewind(int(new_var / fps))
    delayed = True


def pause() -> None:
    global paused
    mixer.music.pause()
    if paused:
        mixer.music.unpause()
    paused = not paused
    print(paused)


def open_file() -> None:
    mixer.music.unload()
    global audio
    global paused
    global time_between_frame
    path = tkinter.filedialog.askopenfilename()
    if path == "":
        return
    last_index_dot = path.rfind('.')
    format = path[last_index_dot - len(path) + 1:]
    if format not in ["3g2", "3gp", "aaf", "asf", "avchd", "avi", "drc", "flv", "m2v", "m3u8", "m4p", "m4v", "mkv",
                      "mng", "mov", "mp2", "mp4", "mpe", "mpeg", "mpg", "mpv", "mxf", "nsv", "ogg", "ogv", "qt", "rm",
                      "rmvb", "roq", "svi", "vob", "webm", "wmv", "yuv"]:
        print("given format : " + format + " is unsupported")
        return
    print(format)
    global minutes, seconds, frames_played, frames_played_per_sec, fps, video
    minutes = seconds = frames_played = frames_played_per_sec = 0
    video = cv2.VideoCapture(path)
    convert = subprocess.Popen("ffmpeg -y -i " + '"' + path + '"' + " audio.mp3", shell=True)
    convert.wait()
    audio = "audio.mp3"
    mixer.music.load(audio)
    mixer.music.play()
    fps = video.get(cv2.CAP_PROP_FPS)
    if video.get(cv2.CAP_PROP_FPS) != 0:
        length_in_time = int((video.get(cv2.CAP_PROP_FRAME_COUNT)) / video.get(cv2.CAP_PROP_FPS))
        if length_in_time % 60 < 10:
            length_max.config(text=str(int(length_in_time / 60)) + ":" + str(length_in_time % 60) + "0")
        else:
            length_max.config(text=str(int(length_in_time / 60)) + ":" + str(length_in_time % 60))
    time_between_frame = int(1000 / fps)
    paused = False


def video_stream() -> None:
    global frames_played_per_sec
    global frames_played
    if paused or delayed:
        label.after(time_between_frame, video_stream)
        return
    if frames_played >= video.get(cv2.CAP_PROP_FRAME_COUNT):
        label.after(time_between_frame, video_stream)
        return
    _, frame = video.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(img)
    img = img.resize((frame_arr[0].winfo_width(), frame_arr[0].winfo_height()), Image.NEAREST)
    img = ImageTk.PhotoImage(image=img)
    label.img = img
    label.config(image=img)
    fps_label.config(text=str(int(fps)) + " frames per second")
    slider.var = DoubleVar()
    slider.var.set(frames_played / video.get(cv2.CAP_PROP_FRAME_COUNT))
    slider.config(variable=slider.var)
    frames_played += 1
    frames_played_per_sec += 1
    label.after(time_between_frame, video_stream)
    length_current.config(text=str(minutes) + ":" + str(seconds))


def timer() -> None:
    global delayed
    root.after(1000, timer)
    if paused:
        return
    delayed = False
    global seconds
    global minutes
    global time_between_frame
    global frames_played_per_sec
    global frames_played
    seconds += 1
    if (seconds >= 60):
        seconds = 0
        minutes += 1
    if (frames_played_per_sec < fps):
        time_between_frame -= 1
        if ((fps - frames_played_per_sec) > 5):
            time_between_frame -= 5
    if (frames_played_per_sec > fps):
        time_between_frame += 1
        if ((frames_played_per_sec - fps) > 5):
            time_between_frame += 5
    if (time_between_frame < 1):
        # if time beween frame is too slow(<1ms)
        time_between_frame = 1
        video.set(cv2.CAP_PROP_POS_FRAMES, (seconds + minutes * 60) * fps)
        frames_played = (seconds + minutes * 60) * fps
    frames_played_per_sec = 0

def initialize_ui() -> None:
    global label
    global fps_label
    global length_max
    global length_current
    global slider
    global root
    root = Tk()
    mixer.init()
    root.geometry("1200x600")
    frame_arr.append(Frame(root, background="grey", padx=0, pady=0))
    frame_arr.append(Frame(root, padx=20, pady=0, bd=0))
    frame_arr.append(Frame(root, padx=20, pady=0, bd=2))
    frame_arr.append(Frame(root, padx=0, pady=0, bd=1))
    Button(frame_arr[1], text=">>", command=lambda: rewind(10)).pack(side='right', anchor='e')
    Button(frame_arr[1], text="||", command=pause).pack(side='right', anchor='w')
    Button(frame_arr[1], text="<<", command=lambda: rewind(-10)).pack(side='left')
    Button(frame_arr[3], text="open video", command=open_file).pack(side='left')

    slider = Scale(frame_arr[2], orient=HORIZONTAL, showvalue=False, from_=0.0, to=1.0, resolution=0.0005,
                   command=new_slider_val)

    label = Label(frame_arr[0])
    fps_label = Label(frame_arr[2], text="text")
    length_max = Label(frame_arr[2], text="0:00")
    slider.pack(side='top', fill=X)
    length_current = Label(frame_arr[2], text="#")
    length_max.pack(side="right")
    length_current.pack(side="left")
    fps_label.pack()
    label.pack(side="left")
    frame_arr[3].pack(side="top", fill=X)
    frame_arr[1].pack(side="bottom", pady=(10, 50))
    frame_arr[2].pack(side="bottom", fill=X)
    frame_arr[0].pack(side="top", fill='both', expand=1)
    root.title("")
    video_stream()
    timer()
    root.mainloop()

if __name__ == "__main__":
    frame_arr = []
    seconds = 0
    minutes = 0
    length_in_time = 0
    frames_played_per_sec = 0
    frames_played = 0
    video = cv2.VideoCapture()
    audio = None
    fps = 0
    paused = True
    delayed = False
    time_between_frame = 999
    initialize_ui()






