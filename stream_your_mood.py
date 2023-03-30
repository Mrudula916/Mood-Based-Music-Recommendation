# Importing Required Modules & libraries
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import pygame
import os
from db import *
import time
try:
    import pyglet
except:
    os.system("pip install pyglet")
    import pyglet
pyglet.font.add_file('assets/fonts/GothamLight.ttf')
from threading import Thread
from contextlib import contextmanager
from globalSettings import *
import uuid
import cv2
from sys import exit
import sqlite3
import random
from tkinter import *
global_pid = os.getpid()
import signal

try:
    import pygame
except:
    os.system('pip install pygame')
    import pygame

def createFolderIfnotExists(path):
    if not os.path.exists(path):
        os.makedirs(path, mode=0o777)

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

default_font = "Gotham" #"times new roman"

grey = "#888" #"grey"
white = "#ffffff" #"white"
black = "#000"
gold = "gold"
default_bg = black
default_fg = "#00d7df"

# Creating TK Container
root = Tk()
root.configure(background=default_bg)

print("\n<============= LOADING LIBRARIES =============>\n")

#with suppress_stdout():
from FacialEmotionRecognition import facial
from AudioClassification import audio

print("\n<============= LIBRARIES LOADED =============>\n")

def load_window_defaults(root):
    root.title("SYM - Stream Your Mood!")
    root.configure(background=default_bg)

def play_music(root, detected_emotion):
    conn = create_connection(DBPath)
    c=conn.cursor()
    if detected_emotion in emotion_genre_mappings.keys():
        genre_to_play = emotion_genre_mappings[detected_emotion]
        genre_to_play = random.choice(genre_to_play)
    else:
        raise NameError("unknown genre")
    
    print("Genre Detected : {}\n".format(genre_to_play))
    query = "select path,song from songs where genre='" + str(genre_to_play) + "'"
    c.execute(query)
    song_paths = []
    i = 0
    for col in c:
        path = col[0]
        song = col[1]
        if os.path.isfile(path):
            song_paths.append(path)
            i=1
            
    if i==0:
        messagebox.showerror("showerror", "Couldn't find any appropriate songs. Playing a random song.")
        query = "select path, song from songs order by prediction desc"
        c.execute(query)
        for col in c:
            path = col[0]
            song = col[1]
            if os.path.isfile(path):
                i=1
                song_paths.append(path)
    conn.close()
    if i==0 and not song_paths:
        messagebox.showerror("showerror", "No songs in the DB.")
    else:
        path = random.choice(song_paths)
        print("PLAYING {}. PLEASE ENJOY!".format(path))
        mp = MusicPlayer(root, song_paths)
        mp.playsong(path)

def analyze_music(root, flag, music_folder_dir, files, detected_emotion):
    root.title("Analyzing music...")
    conn = create_connection(DBPath)
    c=conn.cursor()
    existing_paths = []
    existing_songs = []
    query="select path,song from songs"
    c.execute(query)
    for col in c:
        existing_paths.append(col[0])
        existing_songs.append(col[1])

    if flag:
        for file in files:
            song = os.path.join(music_folder_dir,file)

            if song not in existing_paths and file not in existing_songs:
                sys.stdout.write("Analyzing song ... %s%%\r" % (file))
                sys.stdout.flush()

                results = audio.classify_audio(song)
                i = 0
                print("results : ", results)
                for genre, val in results:
                    if val > 0.5 or i==0:
                        c.execute("insert into songs(path, genre, prediction, song) values(?,?,?, ?)",[song, genre, val, file])
                        conn.commit()
                    else:
                        break
                    i+=1
    
    conn.close()
    play_music(root, detected_emotion)

def analyze_facial_emotion(root,flag, music_folder_dir, files):
    root.title("Analyzing your mood...")
    attempt = 0
    while True:
        attempt+=1
        if use_webcam:
            video_capture = cv2.VideoCapture(0)
            frame = video_capture.read()[1]
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY )
        else:
            image = cv2.imread("happy.png",0)
            frame = image

        if save_images:
            createFolderIfnotExists('saved_images')
            name = os.path.join('saved_images', str(uuid.uuid4()) + '.png')
            cv2.imwrite(name, frame)
        
        detected_emotion = facial.detect_emotion(image)
        if detected_emotion is None:
            if attempt > 3:
                print("Failed to detect face in {} attempts. Exiting...".format(attempt))
                exit()
            messagebox.showerror("showerror", "Emotion couldn't be recognized.\nRetrying in 3s")
            time.sleep(3)
        else:
            break
        
    print("\nEmotion detected : ", detected_emotion)
    analyze_music(root, flag, music_folder_dir, files, detected_emotion)

def loading_window(root,flag, music_folder_dir, files):
    for widgets in root.winfo_children():
        widgets.destroy()
    frameCnt = 12
    frames = [PhotoImage(file='assets/images/loading.gif',format = 'gif -index %i' %(i)) for i in range(frameCnt)]

    def update(ind):
        frame = frames[ind]
        ind += 1
        if ind == frameCnt:
            ind = 0
        root.configure(background=white)
        label.configure(image=frame,background=white,text="Analyzing Mood")
        root.after(100, update, ind)
    label = Label(root)
    label.pack()
    root.after(0, update, 0)
    # analyze_facial_emotion(root,flag, music_folder_dir, files)
    x = Thread(target=analyze_facial_emotion,args=(root,flag, music_folder_dir, files,))
    x.start()

def submit(root, flag, music_folder_dir, existing_paths, name_var):
    name_var.set("")
    conn = create_connection(DBPath)
    c=conn.cursor()
    files = []
    if flag:
        if os.path.isdir(music_folder_dir):
            files = [f for f in os.listdir(music_folder_dir) if f.endswith('.mp3') or f.endswith('.wav')]
            if not files:
                messagebox.showerror("showerror","The folder doesn't contain any audio files")
            else:
                if os.path.normpath(music_folder_dir) not in list(os.path.normpath(p) for p in existing_paths):
                    c.execute("insert into folder_paths(path) values(?)",[music_folder_dir])
                    conn.commit()
                conn.close()
                loading_window(root, flag, music_folder_dir, files)
            
        else:
            #print("\nPlease enter a valid folder!\n")
            messagebox.showerror("showerror", "Please enter a valid folder!")
    else:
        conn.close()
        loading_window(root, flag, music_folder_dir, files)
        
class FolderPath:
    def __init__(self,root):
        conn = create_connection(DBPath)
        c=conn.cursor()
        for widgets in root.winfo_children():
            widgets.destroy()
        root.configure(background=default_bg)
        self.root = root
        # Title of the window
        self.root.title("Stream Your Mood!")
        root.geometry("750x300")
        name_var=tk.StringVar()

        # creating a label for
        # name using widget Label
        
        name_label = tk.Label(root, text = 'Enter the full path of music directory: ', font=(default_font,15, 'bold'),bg=default_bg,fg=default_fg)
        
        # creating a entry for input
        # name using widget Entry
        name_entry = tk.Entry(root,textvariable = name_var, font=(default_font,15,'normal'),bg=default_bg,fg=default_fg,insertbackground='white')
                
        existingPaths = []
        query="select id,path from folder_paths"
        c.execute(query)
        conn.commit()
        btnState="disabled"
        existing_count=False
        for col in c:
            btnState,existing_count="normal",True
            existingPaths.append(col[1])

        # creating a button using the widget
        # Button that will call the submit function
        sub_btn=tk.Button(root,text = 'Submit', command=lambda: submit(self.root, True,name_var.get(),existingPaths,name_var), font=(default_font,15, 'bold'), bg=default_bg,fg=default_fg,state="normal")
        
        existing_btn=tk.Button(root,text = 'Use existing', command=lambda:submit(self.root,False,name_var.get(),existingPaths,name_var), font=(default_font,15, 'bold'), bg=default_bg,fg=default_fg,state=btnState)
        
        # placing the label and entry in
        # the required position using grid
        # method
        name_label.grid(row=0,column=0,padx=10,pady=5)
        name_entry.grid(row=0,column=1,columnspan=2,padx=10,pady=5)
        sub_btn.grid(row=1,column=1,padx=10,pady=5)
        existing_btn.grid(row=1,column=2,padx=10,pady=5)

        songsframe = LabelFrame(root,text="Existing Paths",font=(default_font,15,"bold"),bg=default_bg,fg=default_fg,bd=5,relief=SUNKEN )
        songsframe.place(x=0,y=100,width=750,height=200)
        # Inserting scrollbar
        scrol_y = Scrollbar(songsframe,orient=VERTICAL)
        # Inserting Playlist listbox
        self.playlist = Listbox(songsframe,yscrollcommand=scrol_y.set,selectbackground=default_bg,selectmode=SINGLE,font=(default_font,12,"bold"),bg=default_bg,fg=default_fg,bd=5,relief=SUNKEN )
        # Applying Scrollbar to listbox
        scrol_y.pack(side=RIGHT,fill=Y)
        scrol_y.config(command=self.playlist.yview,background=default_bg)
        self.playlist.pack(fill=BOTH)
        # # Changing Directory for fetching Songs
        #os.chdir("D:\\Desktop\\the best of rock")
        # Fetching Songs
        songtracks = os.listdir("D:\\Desktop\\the best of rock")
        #songtracks = []
        # # Inserting Songs into Playlist
        if existing_count:
            i=1
            for track in existingPaths:
                track = str(i) + ' => ' + track
                self.playlist.insert(END,track)
                i+=1
        else:
            self.playlist.insert(END,"NONE")

# Defining MusicPlayer Class
class MusicPlayer:

  # Defining Constructor
  def __init__(self,root, path):
    self.root = root
    # Title of the window
    self.root.title("Stream Your Mood!")
    # Window Geometry
    self.root.geometry("1100x200")
    # Initiating Pygame
    pygame.init()
    # Initiating Pygame Mixer
    pygame.mixer.init()
    # Declaring track Variable
    self.track = StringVar()
    # Declaring Status Variable
    self.status = StringVar()
    # for i in path:
    # Creating Track Frame for Song label & status label
    trackframe = LabelFrame(self.root,text="Song Track",font=("Gotham",15,"bold"),bg=default_bg,fg="white",bd=5,relief=GROOVE)
    trackframe.place(x=0,y=0,width=700,height=100)
    # Inserting Song Track Label
    songtrack = Label(trackframe,textvariable=self.track,width=20,font=("Gotham",24,"bold"),bg=default_bg,fg=default_fg).grid(row=0,column=0,padx=10,pady=5)
    # Inserting Status Label
    trackstatus = Label(trackframe,textvariable=self.status,width=8,font=(default_font,24,"bold"),bg=default_bg,fg=default_fg).grid(row=0,column=1,padx=10,pady=5)

    # Creating Button Frame
    buttonframe = LabelFrame(self.root,text="Control Panel",font=(default_font,15,"bold"),bg=default_bg,fg="white",bd=5,relief=GROOVE)
    buttonframe.place(x=0,y=100,width=700,height=100)
    # Inserting Play Button
    playbtn = Button(buttonframe,text="RESTART",command=self.restart,width=10,height=1,font=(default_font,16,"bold"),fg=default_fg,bg=default_bg).grid(row=0,column=0,padx=10,pady=5)
    # Inserting Pause Button
    playbtn = Button(buttonframe,text="PAUSE",command=self.pausesong,width=8,height=1,font=(default_font,16,"bold"),fg=default_fg,bg=default_bg).grid(row=0,column=1,padx=10,pady=5)
    # Inserting Unpause Button
    playbtn = Button(buttonframe,text="UNPAUSE",command=self.unpausesong,width=10,height=1,font=(default_font,16,"bold"),fg=default_fg,bg=default_bg).grid(row=0,column=2,padx=10,pady=5)
    # Inserting Stop Button
    playbtn = Button(buttonframe,text="CLOSE",command=self.stopsong,width=6,height=1,font=(default_font,16,"bold"),fg=default_fg,bg=default_bg).grid(row=0,column=3,padx=10,pady=5)

    # Creating Playlist Frame
    songsframe = LabelFrame(self.root,text="Song Playlist",font=(default_font,15,"bold"),bg=default_bg,fg="white",bd=5,relief=GROOVE)
    songsframe.place(x=700,y=0,width=400,height=200)
    # Inserting scrollbar
    scrol_y = Scrollbar(songsframe,orient=VERTICAL)
    # Inserting Playlist listbox
    self.playlist = Listbox(songsframe,yscrollcommand=scrol_y.set,selectbackground=default_bg,selectmode=SINGLE,font=(default_font,12,"bold"),bg=default_bg,fg=default_fg,bd=5,relief=GROOVE)
    # Applying Scrollbar to listbox
    scrol_y.pack(side=RIGHT,fill=Y)
    scrol_y.config(command=self.playlist.yview)
    self.playlist.pack(fill=BOTH)

    i=0
    playlist_mappings = {}
    for track in path:
        playlist_mappings[i] = track
        i+=1
        track = os.path.basename(track)
        self.playlist.insert(END,track)
            

        def go(event):
            cs = self.playlist.curselection()
            text=self.playlist.get(cs)
            print(playlist_mappings[cs[0]])
            song_path = playlist_mappings[cs[0]]
            if os.path.isfile(song_path):
                self.playsong(song_path)
            else:
                messagebox.showerror("showerror", "Invalid song!")

        self.playlist.bind('<Double-1>', go)

  # Defining Play Song Function
  def playsong(self, path):
    self.status.set("-Stopped")
    # Stopped Song
    pygame.mixer.music.stop()
    # Displaying Selected Song title
    #self.track.set(self.playlist.get(ACTIVE))
    self.track.set(str(os.path.basename(path)))
    # Displaying Status
    self.status.set("-Playing")
    # Loading Selected Song
    #pygame.mixer.music.load(self.playlist.get(ACTIVE))
    pygame.mixer.music.load(path)
    # Playing Selected Song
    pygame.mixer.music.play()

  def restart(self):
    self.stopsong()
    load_window_defaults(root)
    fp = FolderPath(root)

  def stopsong(self):
    # Displaying Status
    self.status.set("-Stopped")
    # Stopped Song
    pygame.mixer.music.stop()
    self.root.destroy()
    try:
        os.kill(global_pid, signal.CTRL_BREAK_EVENT)
    except:
        pass

  def pausesong(self):
    # Displaying Status
    self.status.set("-Paused")
    # Paused Song
    pygame.mixer.music.pause()

  def unpausesong(self):
    # Displaying Status
    self.status.set("-Playing")
    # Playing back Song
    pygame.mixer.music.unpause()

fp = FolderPath(root)
# Passing Root to MusicPlayer Class
#mp = MusicPlayer(root)
# Root Window Looping
root.mainloop()
#mp.playsong("music.mp3")