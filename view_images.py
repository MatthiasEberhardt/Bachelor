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
nr_of_classifications={}
classifications={}
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



class WindowManager:

	def __init__(self):
		self.wrongly_classified=[]
		self.index=0
		self.load_paths()
		self.displayed_image=""
		self.window=Tk()
		self.window.title("wrongly classified images")
		#self.save_button=tk.Button(self.window,text="save",command=save)
		#self.save_button.grid(row=0,column=2)
		self.window.geometry("900x500")
		self.label_rgb=tk.Label(self.window,text="rgb-channels")
		self.label_rgb.grid(row=1,column=0)
		self.label_nir=tk.Label(self.window,text="nir-channel")
		self.label_nir.grid(row=1,column=1)

		self.label_cat=tk.Label(self.window,text="category: {}".format(self.wrongly_classified[0].split("/")[0]))
		self.label_cat.grid(row=0,column=0)
		self.label_count=tk.Label(self.window,text="1 of {}".format(len(self.wrongly_classified)))
		self.label_count.grid(row=0,column=1)
		self.label_name=tk.Label(self.window,text=self.wrongly_classified[0])
		self.label_name.grid(row=0,column=2)
		self.canvas_rgb = tk.Canvas(master=self.window,width=400,height=400)
		self.canvas_rgb.grid(row=2,column=0)
		#canvas_rgb.pack()
		self.canvas_nir = tk.Canvas(master=self.window,width=400,height=400)
		self.canvas_nir.grid(row=2,column=1)
		
		self.display_image()
		self.button_ship=tk.Button(self.window,text="prev",command=self.prev_image)
		self.button_ship.grid(row=3,column=0)
		self.button_non_ship=tk.Button(self.window,text="next",command=self.next_image)
		self.button_non_ship.grid(row=3,column=1)
		self.window.mainloop()

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
		for cat in classifications.keys():
			for file in classifications[cat].keys():
				pred=0
				for entrance in classifications[cat][file]:
					pred=pred+entrance
				if pred==0:
					self.wrongly_classified.append(cat+"/"+file)

	def get_path(self):
		return self.wrongly_classified[self.index]

	def display_image(self):
		global path
		img_path=self.get_path()
		total_path=path+"/"+img_path
		f=rasterio.open(total_path)
		b,g,r,n=f.read()
		channels=tuple([r,g,b,n])
		_4ch_img=np.dstack(channels)
		#scale to local max?
		_4ch_img_greyscale=(((_4ch_img-min_px).astype(np.float)/max_px)*255).astype(np.uint8)
		#print(_4ch_img_greyscale.shape)
		rgb_img=_4ch_img_greyscale[:,:,:3]#np.transpose(_4ch_img_greyscale[:3,:,:],axes=(1,2,0))
		nir_img=_4ch_img_greyscale[:,:,3]
		#print(rgb_img.shape)
		#print(nir_img.shape)
		self.tk_rgb_img=ImageTk.PhotoImage(image=Image.fromarray(rgb_img))
		self.tk_nir_img=ImageTk.PhotoImage(image=Image.fromarray(nir_img))
		#print(self.tk_rgb_img)
		self.canvas_rgb.create_image(0,0, anchor="nw", image=self.tk_rgb_img)
		self.canvas_nir.create_image(0,0, anchor="nw", image=self.tk_nir_img)
		self.displayed_image=img_path

	def classify_as_ship(self):
		self.classify("ship")

	def classify_as_non_ship(self):
		self.classify("non_ship")

	def classify(self,cat):
		print(self.displayed_image)
		split_name=self.displayed_image.split("/")
		category=split_name[0]
		file_name=split_name[1]#.split(".")[0]
		if category==cat:
			classifications[category][file_name].append(1)
		else:
			classifications[category][file_name].append(0)
		nr_of_classifications[category][file_name]=nr_of_classifications[category][file_name]+1
		self.display_image()
		to_be_classified[category].remove(file_name)
		if len(to_be_classified)==0:
			get_least_often_classified_images()

wm=WindowManager()