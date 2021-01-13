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
to_be_classified={"ship":[],"non_ship":[]}
file=Path("nr_of_classifications.json")
max_px=36121
min_px=0
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("nr_of_classifications.json missing")
else:
	file_nr = open('nr_of_classifications.json', 'r')
	jsonstring_nr=file_nr.read()
	nr_of_classifications = json.loads(jsonstring_nr)

file=Path("classifications.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("classifications.json missing")
else:
	file_c = open('classifications.json', 'r')
	jsonstring_c=file_c.read()
	classifications = json.loads(jsonstring_c)

count=0
for cat in nr_of_classifications:
	for file in nr_of_classifications[cat]:
		count=count+nr_of_classifications[cat][file]

print("nr of classifications: {}".format(count))

sum_=0.0
for cat in classifications:
	for file in classifications[cat]:
		sum_=sum_+sum(classifications[cat][file])

print("accuracy: {}%".format((sum_/count)*100))
print("{} images in total".format(len(classifications["ship"])+len(classifications["non_ship"])))
print("{} classifications per image on average".format(float(count)/float(len(classifications["ship"])+len(classifications["non_ship"]))))

ship_as_ship=0
ship_as_non_ship=0
non_ship_as_ship=0
non_ship_as_non_ship=0
for file in classifications["ship"]:
	for entrance in classifications["ship"][file]:
		if entrance==0:
			ship_as_non_ship=ship_as_non_ship+1
		else:
			ship_as_ship=ship_as_ship+1

for file in classifications["non_ship"]:
	for entrance in classifications["non_ship"][file]:
		if entrance==0:
			non_ship_as_ship=non_ship_as_ship+1
		else:
			non_ship_as_non_ship=non_ship_as_non_ship+1

print("ship_as_ship: {}".format(ship_as_ship))
print("ship_as_non_ship: {}".format(ship_as_non_ship))
print("non_ship_as_ship: {}".format(non_ship_as_ship))
print("non_ship_as_non_ship: {}".format(non_ship_as_non_ship))


correct_classified={}

for cat in classifications.keys():
	#print(cat)
	for file in classifications[cat]:
		cnt=0
		pred=0
		#print(classifications[cat][file])
		for entrance in classifications[cat][file]:
			cnt=cnt+1
			pred=pred+entrance
		percentage=int((float(pred)/float(cnt))*100)
		#print(pred)
		#print(cnt)
		if percentage in correct_classified.keys():
			correct_classified[percentage]=correct_classified[percentage]+1
		else:
			correct_classified[percentage]=1


correct_classified={k: v for k, v in sorted(correct_classified.items(), key=lambda item: item[0])}

for p in correct_classified.keys():
	print("{} images classified with {}% accuracy".format(correct_classified[p],p))
