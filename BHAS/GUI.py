import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2
from datetime import datetime

HEADER_FOOTER_HEIGHT = 0.1
VIDEO_HEIGHT = 0.8
UPDATE_INTERVAL = 1000


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.title("BHAS - Berkane Horde Alert System")

        # self.root.iconbitmap(default='src/bhas.ico')

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # Compute dimensions of header, footer, and video
        self.header_height = int(self.height * HEADER_FOOTER_HEIGHT)
        self.footer_height = int(self.height * HEADER_FOOTER_HEIGHT)
        self.video_height = int(self.height * VIDEO_HEIGHT)
        self.video_width = self.width

        # Informatios
        self.varh = self.height * (1 - 0.065)
        self.varw = int(self.width * 0.21)
        self.varw1 = int(self.width * 0.41)

        # HEADER
        self.bhas_header = Image.open("src/BHAS HEADER.png")
        self.bhas_header = self.bhas_header.resize(
            (self.width, self.header_height))
        self.bhas_header = ImageTk.PhotoImage(self.bhas_header)

        self.header_label = tk.Label(self.root, image=self.bhas_header)
        self.header_label.place(x=0, y=0)

        # FOOTER
        self.bhas_footer = Image.open("src/BHAS FOOTER.png")
        self.bhas_footer = self.bhas_footer.resize(
            (self.width, self.header_height))
        self.bhas_footer = ImageTk.PhotoImage(self.bhas_footer)

        self.header_label = tk.Label(self.root, image=self.bhas_footer)
        self.header_label.place(x=0, y=self.height - self.header_height)

        # Streams
        self.video_label = tk.Label(self.root)
        self.video_label.place(x=0, y=self.header_height)

        self._set_clock()
        self._set_numDogs()
        self._set_lastOp()
        self._set_numMails()

        print("GUI object intialized....")

    # CLOCK
    def _set_clock(self):
        self.clock_var = tk.IntVar()
        clock = tk.Label(self.root, textvariable=self.clock_var, font=(
            'Montserrat', 18), bg="#29235C", fg="#F9B233")
        clock.place(x=self.width - self.varw, y=self.varh)

    # Last Operation
    def _set_lastOp(self):
        self.op_var = tk.IntVar()
        last_op = tk.Label(self.root, textvariable=self.op_var, font=(
            'Montserrat', 18), bg="#29235C", fg="#F9B233")
        last_op.place(x=self.width - self.varw1, y=self.varh)

    # Number of dogs
    def _set_numDogs(self):
        self.num_dog = tk.IntVar()
        num_of_dogs = tk.Label(self.root, textvariable=self.num_dog, font=(
            'Montserrat', 18), bg="#29235C", fg="#F9B233")
        num_of_dogs.place(x=self.varw1, y=self.varh)

    # Number of mails
    def _set_numMails(self):
        self.num_mail = tk.StringVar()
        num_of_mails = tk.Label(self.root, textvariable=self.num_mail, font=(
            'Montserrat', 18), bg="#29235C", fg="#F9B233")
        num_of_mails.place(x=self.varw, y=self.varh)

    def get_streams_grid(self, frames, grid):
        window_size = (self.video_height / grid[0], self.video_width / grid[1])
        grid_count = grid[0] * grid[1]
        frames_count = len(frames)

        frame_grid = np.zeros(
            (int(self.video_height), int(self.video_width), 3), dtype=np.uint8)
        i = 0
        while i < grid_count:
            if grid[0] == 1:
                row = 0
            else:
                row = i // grid[0]
            col = i % grid[1] 
            y = int(row*window_size[0])
            x = int(col*window_size[1])
            h = int(window_size[0])
            w = int(window_size[1])
            if i < frames_count:
                j = frames[i]
                frame = cv2.resize(j, (w-1, h-1))
            else:
                frame = np.zeros((h-1, w-1, 3), dtype=np.uint8)

            frame = cv2.copyMakeBorder(frame, 0, 1, 0, 1, cv2.BORDER_CONSTANT, None, value=(255, 255, 255))
            frame_grid[y:y+h, x:x+w] = frame

            i+=1

        # for idx, j in enumerate(frames):
        #     row = idx // grid[0]
        #     col = idx % grid[1] 
        #     y = int(row*window_size[0])
        #     x = int(col*window_size[1])
        #     h = int(window_size[0])
        #     w = int(window_size[1])
        #     frame = cv2.resize(j, (w-1, h-1))
        #     frame = cv2.copyMakeBorder(frame, 0, 1, 0, 1, cv2.BORDER_CONSTANT, None, value=(255, 255, 255))
        #     frame_grid[y:y+h, x:x+w] = frame

        return frame_grid

    def show(self, numMails, numDogs, lastOp, frame_to_show):
        self.clock_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.num_mail.set(numMails)
        self.num_dog.set(numDogs)
        self.op_var.set(lastOp)

        frame_image = Image.fromarray(
            cv2.cvtColor(frame_to_show, cv2.COLOR_BGR2RGB))
        frame_image = frame_image.resize((self.video_width, self.video_height))
        frame_image = ImageTk.PhotoImage(frame_image)

        self.video_label.config(image=frame_image)
        self.video_label.image = frame_image

        self.root.update()

        self.root.bind("<Escape>", lambda e: self.root.destroy())
