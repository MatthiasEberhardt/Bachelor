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
reclassifications={"non_ship":{},"ship":{}}
max_px=36121
min_px=0
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

file=Path("reclassifications.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("reclassifications.json missing")
else:
	file_c = open('reclassifications.json', 'r')
	jsonstring_c=file_c.read()
	reclassifications = json.loads(jsonstring_c)

def save():
	global reclassifications
	#global classifications
	string_re=json.dumps(reclassifications)
	#string_c=json.dumps(classifications)
	file_re = open('reclassifications.json', 'w')
	file_re.write(string_re)
	file_re.close()
	#file_c = open('classifications.json', 'w')
	#file_c.write(string_c)
	#file_c.close()


class WindowManager:

	def __init__(self):
		self.wrongly_classified=[]
		self.index=0
		self.load_paths()
		self.displayed_image=""
		self.window=Tk()
		self.window.title("reclassify wrongly classified images")
		self.save_button=tk.Button(self.window,text="save",command=save)
		self.save_button.grid(row=0,column=2)
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
		self.label_name.grid(row=1,column=2)
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
		self.button_ship=tk.Button(self.window,text="reclassify as ship",command=self.classify_as_ship)
		self.button_ship.grid(row=4,column=0)
		self.button_non_ship=tk.Button(self.window,text="reclassify as non_ship",command=self.classify_as_non_ship)
		self.button_non_ship.grid(row=4,column=1)
		self.window.mainloop()

	def set_labels(self):
		if self.wrongly_classified[self.index] in reclassifications["non_ship"]:
			self.label_cat["text"]="old cat: {}, reclassified as {}".format(self.wrongly_classified[self.index].split("/")[0],reclassifications["non_ship"][self.wrongly_classified[self.index]])
		else:
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
		for file in classifications["non_ship"].keys():
			pred=0
			for entrance in classifications["non_ship"][file]:
				pred=pred+entrance
			if pred<3:
				self.wrongly_classified.append("non_ship"+"/"+file)

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
		reclassifications[category][file_name]=cat
		self.label_cat["text"]="old cat: {}, reclassified as {}".format(self.wrongly_classified[self.index].split("/")[0],cat)

wm=WindowManager()