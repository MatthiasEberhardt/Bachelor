
import tkinter as tk
from tkinter import *
import json
import rasterio
import os
from pathlib import Path
from PIL import Image, ImageTk
import numpy as np

classifications_matthias={}
file=Path("classifications.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("classifications.json missing")
else:
	file_c = open('classifications.json', 'r')
	jsonstring_c=file_c.read()
	classifications = json.loads(jsonstring_c)


classifications_elisabeth={}
file=Path("classifications_elisabeth.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("classifications_elisabeth.json missing")
else:
	file_c = open('classifications_elisabeth.json', 'r')
	jsonstring_c=file_c.read()
	classifications = json.loads(jsonstring_c)



classifications_peter={}
file=Path("classifications_peter.json")
try:
	file.resolve(strict=True)
except FileNotFoundError:
	print("classifications_peter.json missing")
else:
	file_c = open('classifications_peter.json', 'r')
	jsonstring_c=file_c.read()
	classifications = json.loads(jsonstring_c)

diff_max={"ship":{},"non_ship":{}}

for cat in classifications.keys():
	for file in classifications[cat].keys():
		diff_max[cat][file]=[float(sum(classifications[cat][file]))/len(classifications[cat][file])]

for cat in classifications_elisabeth.keys():
	for file in classifications_elisabeth[cat].keys():
		diff_max[cat][file].append(float(sum(classifications_elisabeth[cat][file]))/len(classifications_elisabeth[cat][file]))

for cat in classifications_peter.keys():
	for file in classifications_peter[cat].keys():
		diff_max[cat][file].append(float(sum(classifications_peter[cat][file]))/len(classifications_peter[cat][file]))

keys_to_delete={"ship":[],"non_ship":[]}

for cat in diff_max.keys():
	for file in diff_max[cat].keys():
		if len(diff_max[cat][file])==3:
			diff_m_e=abs(diff_max[cat][file][0]-diff_max[cat][file][1])
			diff_e_p=abs(diff_max[cat][file][1]-diff_max[cat][file][2])
			diff_m_p=abs(diff_max[cat][file][0]-diff_max[cat][file][2])
			diff_max[cat][file]=max([diff_m_e,diff_m_p,diff_e_p])
		else:
			del diff_max[cat][file]

for cat in diff_max.keys():
	diff_max[cat]={k: v for k, v in sorted(diff_max[cat].items(), key=lambda item: item[1])}

for cat in diff_max.keys():
	print(diff_max[cat])