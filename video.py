import datetime
from tkinter import ttk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo


class VideoPlayer:
    def __init__(self, frame: ttk.Frame, path, width, height):
        """ init player on a frame """
        vid_frame = ttk.Frame(frame, width=width, height=height - 65)
        self.vid_player = TkinterVideo(vid_frame, keep_aspect=True)
        self.vid_player.place(relx=0, rely=0, relwidth=1, relheight=1)
        vid_frame.pack()

        self.play_pause_btn = ttk.Button(frame, text="Play", command=self.play_pause)
        self.play_pause_btn.pack()

        self.skip_plus_5sec = ttk.Button(frame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_plus_5sec.pack(side="left")

        self.start_time = ttk.Label(frame, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_slider = ttk.Scale(frame, from_=0, to=0, orient="horizontal")
        self.progress_slider.bind("<ButtonRelease-1>", self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = ttk.Label(frame, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended )

        self.skip_plus_5sec = ttk.Button(frame, text="Skip +5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        self.load_video(path)
        self.play_pause()

    def update_duration(self, event):
        """ updates the duration after finding the duration """
        duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.progress_slider["to"] = duration


    def update_scale(self, event):
        """ updates the scale value """
        self.progress_slider.set(self.vid_player.current_duration())


    def load_video(self, file_path):
        """ loads the video """
        if file_path:
            self.vid_player.load(file_path)

            self.progress_slider.config(to=0, from_=0)
            self.play_pause_btn["text"] = "Play"
            self.progress_slider.set(0)


    def seek(self, event=None):
        """ used to seek a specific timeframe """
        self.vid_player.seek(int(self.progress_slider.get()))


    def skip(self, value: int):
        """ skip seconds """
        self.vid_player.seek(int(self.progress_slider.get())+value)
        self.progress_slider.set(self.progress_slider.get() + value)


    def play_pause(self):
        """ pauses and plays """
        if self.vid_player.is_paused():
            self.vid_player.play()
            self.play_pause_btn["text"] = "Pause"
        else:
            self.vid_player.pause()
            self.play_pause_btn["text"] = "Play"


    def video_ended(self, event):
        """ handle video ended """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)
        self.play_pause()