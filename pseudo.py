#only pseudocode, not functional python-code
#only saved as .py-file to easily format the code and use syntax-highlighting

def parse_website():
	actors=HTMLParser.parse("https://www.imdb.com/list/ls053501318/?sort=list_order,asc&mode=grid&page=1&ref_=nmls_vw_grd")

def get_actor_id(actors):
	#parallel execution:
	actor_id=[imdb.search_person(name)[0] for name in actors]
	return actor_id

def get_actor_information(actor_id):
	#parallel execution
	actor_information=[imdb.get_person(p.ID) for p in actor_id]
	return actor_information

def get_movie(id):
	m=imdb.get_movie(id)
	return (m.title,m.year,m.rating,m.genre,id)

def load_json_information():
	movies_retrieved={}
	irrelevant_movies=[]
	if exists("movies.json"):
		movies_retrieved=deserialize("movies.json")
	if exists("irrelevant_movies.json"):
		irrelevant_movies=deserialize("irrelevant_movies.json")
	return (movies_retrieved,irrelevant_movies)

def create_dictionary(actor_information,movies_retrieved,irrelevant_movies):
	#actor_dictionary is a global variable
	for actor in actor_information:
		actor_dictionary[actor.name]={}
		#assign the bio to main
		actor_dictionary[actor.name]["main"]=actor["biography"]
		#only select awards that the actor won
		actor_dictionary[actor.name]["awards"]=[award for award in actor["awards"] if awards["result"]=="Winner"]
		#get movies
		actor_dictionary[actor.name]["movies"]=[movies_retrieved[m.ID] for m.ID in actor["movies"] if m.ID in movies_retrieved]
		#parallel execution
		actor_dictionary[actor.name]["movies"]+=[get_movie(m.ID) for m.ID in actor["movies"] if m.ID not in movies_retrieved and m.ID not in irrelevant_movies]
		actor_dictionary[actor.name]["genres"]={genre:nr_of_occurances for genre,nr_of_occurences in [(m[3],1) for m in actor_dictionary[actor.name]["movies"]].groupby(element=0).sum()}

def save_information(movies_retrieved,irrelevant_movies):
	write("movies.json",serialize(movies_retrieved))
	write("irrelevant_movies.json",serialize(irrelevant_movies))

def load_information():
	parse_website()
	movies_retrieved,irrelevant_movies=load_json_information()
	actor_id=get_actor_id(actors)
	actor_information=get_actor_information(actor_id)
	create_dictionary(actor_information,movies_retrieved,irrelevant_movies)
	save_information(movies_retrieved,irrelevant_movies)

def biography(self):
	self.text_field.insert(actor_dictionary[self.name]["main"])

def movies(self):
	actor_dictionary[self.name]["movies"].sort(key=lambda tup:tup[1],descending=False)
	title_list=["Title"]+[t[0] for t in actor_dictionary[self.name]["movies"]]
	year_list=["Year"]+[t[1] for t in actor_dictionary[self.name]["movies"]]
	rating_list=["Rating"]+[t[2] for t in actor_dictionary[self.name]["movies"]]
	self.t=table.Table(self.frame_content,None,(title_list,70),(year_list,30),(rating_list,30))


def best_movies(self):
	self.clear_content_frame()
	sorted_movies=actor_dictionary[self.name]["movies"].sort(key=lambda tup:tup[2],descending=True)[:5]
	title_list=["Title"]+[t[0] for t in sorted_movies]
	year_list=["Year"]+[t[1] for t in sorted_movies]
	rating_list=["Rating"]+[t[2] for t in sorted_movies]
	self.t=table.Table(self.frame_content,None,(title_list,70),(year_list,30),(rating_list,30))

def genre(self):
	sorted_genre=actor_dictionary[self.name]["genre"].sort(key=lambda k:k[1],descending=True)
	genres_of_actor=[gen[0] for gen in sorted_genre]
	self.t=table.Table(self.frame_content,None,(genres_of_actor,30))

def awards(self):
	self.clear_content_frame()
	sorted_awards=actor_dictionary[self.name]["awards"].sort(key=lambda elem:elem["year"],descending=False)
	year_list=["Year"],prize_list=["Prize"],award_list=["Award"],category_list=["Category"]
	for award in sorted_awards:
		year_list.append(award["Year"])
		prize_list.append(award["Prize"])
		award_list.append(award["Award"])
		category_list.append(award["Category"])
	self.t=table.Table(self.frame_content,None,(year_list,5),(prize_list,55),(award_list,55),(category_list,80))

def ratings(self):
	rating_by_year=actor_dictionary[self.name]["movies"].groupby(element=1).mean()
	rated_movies=[m[2] for m in actor_dictionary[self.name]["movies"]]
	total_average=sum(rated_movies)/float(len(rated_movies))
	year_list=["Year"]+[entrance[0] for entrance in rating_by_year]
	rating_list=["Average Rating"]+[round(entrance[1],2) for entrance in rating_by_year]
	self.t=table.Table(self.frame_content,["overall average: "+total_average],(year_list,30),(rating_list,30))

class Table():
	def __init__(self,frame,list_of_text,*lists_info_to_display):
		if list_of_text != None:
			self.extra_frame=tk.Frame(self.content_frame,bg="black")
			for text in list_of_text:
				display(text)
		i=0
		for list_,width in lists_info_to_display:
			j=0
			for element in list_:
				display(row=i,column=j,element)
				j++
			i++
