import tkinter as tk
from tkinter import *
import json
import rasterio
import os
from pathlib import Path
from PIL import Image, ImageTk
import numpy as np

#path to 400x400px images
path=r"D:/Bachelor/data/ImageFiles_downsized"
#path to original images
path_raw=r"D:/Bachelor/data/ImageFiles"

nr_of_classifications={}
classifications={}
to_be_classified={"ship":[],"non_ship":[]}
coordinates={}
file=Path("nr_of_classifications.json")
max_px=36121
min_px=0
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("nr_of_classifications.json missing")
	for d in os.listdir(path):
		nr_of_classifications[d]={}
		for f in os.listdir(os.path.join(path,d)):
			name=f
			nr_of_classifications[d][name]=0
else:
	file_nr = open('nr_of_classifications.json', 'r')
	jsonstring_nr=file_nr.read()
	nr_of_classifications = json.loads(jsonstring_nr)

file=Path("coordinates.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("coordinates.json missing")

else:
	file_coord = open('coordinates.json', 'r')
	jsonstring_coord=file_coord.read()
	coordinates = json.loads(jsonstring_coord)

file=Path("classifications.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("classifications.json missing")
	for d in os.listdir(path):
		classifications[d]={}
		for f in os.listdir(os.path.join(path,d)):
			name=f#.split(".")[0]
			classifications[d][name]=[]
else:
	file_c = open('classifications.json', 'r')
	jsonstring_c=file_c.read()
	classifications = json.loads(jsonstring_c)

def save():
	string_coords=json.dumps(coordinates)
	file_coords = open('coordinates.json', 'w')
	file_coords.write(string_coords)
	file_coords.close()




class WindowManager:

	def __init__(self):
		self.wrongly_classified=[]
		self.index=0
		self.allow_multiple_clips=False
		self.load_paths()
		self.displayed_image=""
		self.window=Tk()
		self.window.title("wrongly classified images")
		#self.save_button=tk.Button(self.window,text="save",command=save)
		#self.save_button.grid(row=0,column=2)
		self.save_button=tk.Button(self.window,text="save",command=save)
		self.save_button.grid(row=0,column=2)
		self.multiple_clip_button=tk.Button(self.window,text="toggle multiple clips",command=self.toggle)
		self.multiple_clip_button.grid(row=1,column=2)
		self.window.geometry("1800x1000")
		self.label_rgb=tk.Label(self.window,text="rgb-channels")
		self.label_rgb.grid(row=1,column=0)
		self.label_nir=tk.Label(self.window,text="nir-channel")
		self.label_nir.grid(row=1,column=1)

		self.label_cat=tk.Label(self.window,text="category: {}".format(self.wrongly_classified[0].split("/")[0]))
		self.label_cat.grid(row=2,column=0)
		self.label_count=tk.Label(self.window,text="1 of {}".format(len(self.wrongly_classified)))
		self.label_count.grid(row=2,column=1)
		self.label_name=tk.Label(self.window,text=self.wrongly_classified[0])
		self.label_name.grid(row=2,column=2)
		self.canvas_rgb = tk.Canvas(master=self.window,width=800,height=800)#,bg="red")
		self.canvas_rgb.grid(row=3,column=0)
		#canvas_rgb.pack()
		self.canvas_nir = tk.Canvas(master=self.window,width=800,height=800)#),bg="red")
		self.canvas_nir.grid(row=3,column=1)
		self.canvas_rgb.bind("<Button-1>", self.callback)
		self.canvas_nir.bind("<Button-1>", self.callback)
		self.display_image()
		self.button_prev=tk.Button(self.window,text="prev",command=self.prev_image)
		self.button_prev.grid(row=4,column=0)
		self.button_next=tk.Button(self.window,text="next",command=self.next_image)
		self.button_next.grid(row=4,column=1)
		self.button_undo=tk.Button(self.window,text="undo",command=self.undo)
		self.button_undo.grid(row=5,column=0)
		self.button_undo_all=tk.Button(self.window,text="undo all",command=self.undo_all)
		self.button_undo_all.grid(row=5,column=1)
		self.window.mainloop()

	def toggle(self):
		if self.allow_multiple_clips:
			self.allow_multiple_clips=False
			self.multiple_clip_button.configure(bg="white")
		else:
			self.allow_multiple_clips=True
			self.multiple_clip_button.configure(bg="green")

	def undo(self):
		if self.displayed_image.split("/")[-2] in coordinates:
			coordinates[self.displayed_image.split("/")[-2]]=coordinates[self.displayed_image.split("/")[-2]][:-1]
			self.display_image()

	def undo_all(self):
		if self.displayed_image.split("/")[-2] in coordinates:
			coordinates[self.displayed_image.split("/")[-2]]=[]
			self.display_image()

	def callback(self,event):
		global coordinates
		self.x_coord,self.y_coord=int(float(event.x)/self.scale_factor),int(float(event.y)/self.scale_factor)
		#canvas.create_rectangle(50, 0, 50, 0, fill='red')
		if self.displayed_image.split("/")[-2] not in coordinates:
			coordinates[self.displayed_image.split("/")[-2]]=[(self.x_coord,self.y_coord)]
		else:
			if self.allow_multiple_clips:
				coordinates[self.displayed_image.split("/")[-2]].append((self.x_coord,self.y_coord))
			else:
				coordinates[self.displayed_image.split("/")[-2]]=[(self.x_coord,self.y_coord)]
		print(type(self.x_coord))
		self.display_image()
		#print("clicked at {}, {}".format(int(float(event.x)/self.scale_factor),int(float(event.y)/self.scale_factor)))

	def draw_frame(self):
		#left rectangle
		self.canvas_rgb.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), int((self.x_coord-198)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), fill='red',outline="red")
		self.canvas_nir.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), int((self.x_coord-198)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), fill='red',outline="red")
		#bottom rectangle
		self.canvas_rgb.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord+198)*self.scale_factor), fill='red',outline="red")
		self.canvas_nir.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord+198)*self.scale_factor), fill='red',outline="red")
		#right rectangle
		self.canvas_rgb.create_rectangle(int((self.x_coord+198)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), fill='red',outline="red")
		self.canvas_nir.create_rectangle(int((self.x_coord+198)*self.scale_factor), int((self.y_coord+202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), fill='red',outline="red")
		#top rectangle
		self.canvas_rgb.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord-198)*self.scale_factor), fill='red',outline="red")
		self.canvas_nir.create_rectangle(int((self.x_coord-202)*self.scale_factor), int((self.y_coord-202)*self.scale_factor), int((self.x_coord+202)*self.scale_factor), int((self.y_coord-198)*self.scale_factor), fill='red',outline="red")


	def set_labels(self):
		self.label_cat["text"]=self.wrongly_classified[self.index].split("/")[0]
		self.label_count["text"]="{} of {}".format(self.index+1,len(self.wrongly_classified))
		self.label_name["text"]=self.wrongly_classified[self.index]

	def prev_image(self):
		self.prev()
		self.display_image()
		self.set_labels()

	def next_image(self):
		self.next()
		self.display_image()
		self.set_labels()

	def prev(self):
		self.index=self.index-1
		if self.index==-1:
			self.index=len(self.wrongly_classified)-1


	def next(self):
		self.index=self.index+1
		if self.index==len(self.wrongly_classified):
			self.index=0

	def load_paths(self):
		for file in classifications["ship"].keys():
			pred=0
			for entrance in classifications["ship"][file]:
				pred=pred+entrance
			#number of maximal correct classifications
			if pred<3:
				p="ships"+r"/"+file.split(".")[0]
				total_path_raw=path_raw+r"/"+p
				file_path=""
				if Path(total_path_raw).is_dir():
					for file in os.listdir(total_path_raw):
						if ".tif" in file and "udm" not in file:
							file_path=p+r"/"+file
				self.wrongly_classified.append(file_path)

	def get_path(self):
		return self.wrongly_classified[self.index]

	def display_image(self):
		global path
		self.canvas_rgb.delete("all")
		self.canvas_nir.delete("all")
		img_path=self.get_path()
		total_path=path_raw+"/"+img_path
		f=rasterio.open(total_path)
		b,g,r,n=f.read()
		channels=tuple([r,g,b,n])
		_4ch_img=np.dstack(channels)
		#scale to local max?
		_4ch_img_greyscale=(((_4ch_img-min_px).astype(np.float)/max_px)*255).astype(np.uint8)
		#print(_4ch_img_greyscale.shape)
		rgb_img=_4ch_img_greyscale[:,:,:3]#np.transpose(_4ch_img_greyscale[:3,:,:],axes=(1,2,0))
		nir_img=_4ch_img_greyscale[:,:,3]
		max_len=max(nir_img.shape)
		min_len=min(nir_img.shape)
		self.scale_factor=float(800)/float(max_len)
		#print(rgb_img.shape)
		#print(nir_img.shape)
		self.tk_rgb_img=ImageTk.PhotoImage(image=Image.fromarray(rgb_img).resize((int(nir_img.shape[0]*self.scale_factor),(int(nir_img.shape[1]*self.scale_factor)))))
		self.tk_nir_img=ImageTk.PhotoImage(image=Image.fromarray(nir_img).resize((int(nir_img.shape[0]*self.scale_factor),(int(nir_img.shape[1]*self.scale_factor)))))
		#print(self.tk_rgb_img)
		self.canvas_rgb.create_image(0,0, anchor="nw", image=self.tk_rgb_img)
		self.canvas_nir.create_image(0,0, anchor="nw", image=self.tk_nir_img)
		self.displayed_image=img_path
		if total_path.split("/")[-2] in coordinates:
			print("coordinates updated")
			print(coordinates)
			print(total_path.split("/")[-2])
			for pair in coordinates[total_path.split("/")[-2]]:
				print("pair: {}".format(pair))
				self.x_coord=pair[0]
				self.y_coord=pair[1]
				self.draw_frame()



wm=WindowManager()