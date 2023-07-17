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
        self.root.wm_attributes('-transparentcolor','white')
        self.root.title("Traffic Eye - Berkane Traffic monitoring System")

        self.root.iconbitmap(default='src/BRS logo-10.ico')

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        # Compute dimensions of header, footer, and video
        #self.header_height = int(self.height * HEADER_FOOTER_HEIGHT)
        # self.footer_height = int(self.height * HEADER_FOOTER_HEIGHT)
        self.video_height = self.height
        self.video_width = self.width
        # self.video_height = int(self.height * VIDEO_HEIGHT)
        # self.video_width = self.width       
        # Informatios
        # self.varh = self.height * (1 - 0.065)
        # self.varw = int(self.width * 0.21)
        # self.varw1 = int(self.width * 0.41)

        #HEADER
        self.bhas_header = Image.open("src/BRS logo-04.png")
        self.bhas_header = self.bhas_header.resize((170, 85))
        self.bhas_header = ImageTk.PhotoImage(self.bhas_header)


        self.graphe1 = Image.open("cars.png")
        self.graphe1 = self.graphe1.resize((430, 270))
        self.graphe1 = ImageTk.PhotoImage(self.graphe1)

        self.graphe2 = Image.open("Motos.png")
        self.graphe2 = self.graphe2.resize((430, 270))
        self.graphe2 = ImageTk.PhotoImage(self.graphe2)

        
        self.graphe3 = Image.open("Trucks.png")
        self.graphe3 = self.graphe3.resize((430,270))
        self.graphe3 = ImageTk.PhotoImage(self.graphe3)

        self.graphe4 = Image.open("Buses.png")
        self.graphe4 = self.graphe4.resize((430,270))  
        self.graphe4 = ImageTk.PhotoImage(self.graphe4)
    

        self.bhas_footer = Image.open("src/foot.png")
        self.bhas_footer = self.bhas_footer.resize(
            (self.width, self.height - 30))
        self.bhas_footer = ImageTk.PhotoImage(self.bhas_footer)

        self.logo = Image.open("src/BRS v2-12.png")
        self.logo = self.logo.resize((100,self.video_height))  
        self.logo = ImageTk.PhotoImage(self.logo)

        self.logo1 = Image.open("src/BRS icon-06.png")
        self.logo1 = self.logo1.resize((33,33))  
        self.logo1 = ImageTk.PhotoImage(self.logo1)

        self.logo2 = Image.open("src/BRS icon-07.png")
        self.logo2 = self.logo2.resize((33,33))  
        self.logo2 = ImageTk.PhotoImage(self.logo2)

        self.logo3 = Image.open("src/BRS icon-08.png")
        self.logo3 = self.logo3.resize((33,33))  
        self.logo3 = ImageTk.PhotoImage(self.logo3)

        self.logo4 = Image.open("src/BRS icon-09.png")
        self.logo4 = self.logo4.resize((33,33))  
        self.logo4 = ImageTk.PhotoImage(self.logo4)


        self.video_label = tk.Label(self.root)
        self.video_label.place(x=0, y=0)
        self.header_label = tk.Label(self.root, image=self.bhas_header)
        self.graphe1_label = tk.Label(self.root, bg="#AAAAAA", image=self.graphe1)
        self.graphe2_label = tk.Label(self.root, bg="#AAAAAA", image=self.graphe2)
        self.graphe3_label = tk.Label(self.root, bg="#AAAAAA", image=self.graphe3)
        self.graphe4_label = tk.Label(self.root, bg="#AAAAAA", image=self.graphe4)
        self.logo1_label = tk.Label(self.root, bg="#AAAAAA", image=self.logo1)
        self.logo2_label = tk.Label(self.root, bg="#AAAAAA", image=self.logo2)
        self.logo3_label = tk.Label(self.root, bg="#AAAAAA", image=self.logo3)
        self.logo4_label = tk.Label(self.root, bg="#AAAAAA", image=self.logo4)
        self.logo_label = tk.Label(self.root, bg="#03436B", image=self.logo)
        self.foot_label = tk.Label(self.root, image=self.bhas_footer)
        self.header_label.place(x=130, y=10)
        #self.foot_label.place(x=0, y=self.height - 20)
        self.logo1_label.place(x=120, y=800)
        self.logo2_label.place(x=570, y=800)
        self.logo3_label.place(x=1020, y=800)
        self.logo4_label.place(x=1470, y=800)
        self.graphe1_label.place(x=120, y=800)
        self.graphe2_label.place(x=570, y=800)
        self.graphe4_label.place(x=1020, y=800)
        self.graphe3_label.place(x=1470, y=800)
        self.logo_label.place(x=0, y=0)
        self.graph_update_interval = 5000  # milliseconds, i.e. 1.5 minutes

        self.root.after(self.graph_update_interval, self.update_graphs) 
        # # FOOTER
        # 

        # self.header_label = tk.Label(self.root, image=self.bhas_footer)
        # self.header_label.place(x=0, y=self.height - self.header_height)

        # Streams

        #self._set_Bus()
        self._set_cars()
        self._set_moto()
        self._set_Camion()
        self._set_Bus()
        self._set_Sent()
    #     print("GUI object intialized....")


    # Last Operation
    def _set_cars(self):
        self.Car = tk.IntVar()
        last_op = tk.Label(self.root, textvariable=self.Car, font=(
            'Montserrat', 28), bg="#03436B", fg="#FFB100",width = 3 , anchor = "center")
        last_op.place(x=13, y=255)

    def _set_moto(self):
        self.Moto = tk.IntVar()
        last_op = tk.Label(self.root, textvariable=self.Moto, font=(
            'Montserrat', 28), bg="#03436B", fg="#FFB100",width = 3 , anchor = "center")
        last_op.place(x=13, y=440)

    # Number of dogs
    def _set_Camion(self):
        self.Camion = tk.IntVar()
        num_of_dogs = tk.Label(self.root, textvariable=self.Camion, font=(
            'Montserrat', 28), bg="#03436B", fg="#FFB100",width = 3 , anchor = "center")
        num_of_dogs.place(x=13, y=800)

    # Number of mails
    def _set_Bus(self):
        self.Bus = tk.StringVar()
        num_of_mails = tk.Label(self.root, textvariable=self.Bus, font=(
            'Montserrat', 28), bg="#03436B", fg="#FFB100",width = 3 , anchor = "center")
        num_of_mails.place(x=13, y=615)

    def _set_Sent(self):
        self.Sent = tk.StringVar()
        num_of_mail = tk.Label(self.root, textvariable=self.Sent, font=(
            'Montserrat', 28), bg="#03436B", fg="#FFB100",width = 3 , anchor = "center")
        num_of_mail.place(x=13, y=82)

    # def get_streams_grid(self, frames, grid):
    #     window_size = (self.video_height / grid[0], self.video_width / grid[1])
    #     grid_count = grid[0] * grid[1]
    #     frames_count = len(frames)

    #     frame_grid = np.zeros(
    #         (int(self.video_height), int(self.video_width), 3), dtype=np.uint8)
    #     i = 0
    #     while i < grid_count:
    #         row = i // grid[0]
    #         col = i % grid[1] 
    #         y = int(row*window_size[0])
    #         x = int(col*window_size[1])
    #         h = int(window_size[0])
    #         w = int(window_size[1])
    #         if i < frames_count:
    #             j = frames[i]
    #             frame = cv2.resize(j, (w-1, h-1))
    #         else:
    #             frame = np.zeros((h-1, w-1, 3), dtype=np.uint8)

    #         frame = cv2.copyMakeBorder(frame, 0, 1, 0, 1, cv2.BORDER_CONSTANT, None, value=(255, 255, 255))
    #         frame_grid[y:y+h, x:x+w] = frame

    #         i+=1

        

        
        
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

        # return frame_grid
    def show(self,n, Voitures, Motos, Camion,Buses, frame_to_show):
    #def show(self, frame_to_show):
        self.Sent.set(n)
        self.Car.set(Voitures)
        self.Moto.set(Motos)
        self.Bus.set(Buses)
        self.Camion.set(Camion)

        frame_image = Image.fromarray(
            cv2.cvtColor(frame_to_show, cv2.COLOR_BGR2RGB))
        frame_image = frame_image.resize((self.video_width, self.video_height))
        frame_image = ImageTk.PhotoImage(frame_image)

        self.video_label.config(image=frame_image)
        self.video_label.image = frame_image

        self.root.update()

        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def update_graphs(self):
        # Load and update graph images here
        
        # Update the labels with the new images
        self.graphe1 = Image.open("cars.png")
        self.graphe1 = self.graphe1.resize((430, 270))
        self.graphe1 = ImageTk.PhotoImage(self.graphe1)

        self.graphe2 = Image.open("Motos.png")
        self.graphe2 = self.graphe2.resize((430, 270))
        self.graphe2 = ImageTk.PhotoImage(self.graphe2)

        self.graphe3 = Image.open("Trucks.png")
        self.graphe3 = self.graphe3.resize((430, 270))
        self.graphe3 = ImageTk.PhotoImage(self.graphe3)

        self.graphe4 = Image.open("Buses.png")
        self.graphe4 = self.graphe4.resize((430, 270))
        self.graphe4 = ImageTk.PhotoImage(self.graphe4)

        # Update the graph labels
        self.graphe1_label.config(image=self.graphe1)
        self.graphe2_label.config(image=self.graphe2)
        self.graphe3_label.config(image=self.graphe3)
        self.graphe4_label.config(image=self.graphe4)

        # Schedule the next graph update
        self.root.after(self.graph_update_interval, self.update_graphs)