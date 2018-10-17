
import urllib.request
import re
from bs4 import BeautifulSoup
import time
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import MiniBatchKMeans 	

def buildVocab(page_url):

	request = urllib.request.Request(page_url)

	response = urllib.request.urlopen(request)

	pageSource = response.read().decode('utf-8')

	soup = BeautifulSoup(pageSource, 'html.parser')

	all_hero_names = [ l.text.replace("/Counters","").replace(" ","_") for l in soup.find_all('li') if "/Counters" in l.text ]

	return dict(zip(all_hero_names,range(1,len(all_hero_names)+1)))

def getHeroData(page_url,heroName,vocab):

	request = urllib.request.Request(page_url+'/'+heroName+'/'+'Counters')

	response = urllib.request.urlopen(request)

	pageSource = response.read().decode('utf-8')

	soup = BeautifulSoup(pageSource, 'html.parser')

	heroData = { 'counteredBy':[] , 'doesCounter':[] , 'synergy':[] }

	all_titles = ",".join([ tag.attrs['title'] for tag in soup.find_all('a') if 'title' in tag.attrs ])

	# print(all_titles)

	for name in re.search("Edit section: Bad against(.*?)Edit section",all_titles,re.IGNORECASE).group(1).split(','):
		name = name.replace(" ","_")
		if name in vocab and name!=heroName and not name in heroData['counteredBy']:
			heroData['counteredBy'].append(vocab[name])
	heroData['counteredBy'] = sorted(set(heroData['counteredBy']))

	for name in re.search("Edit section: Good against(.*?)Edit section",all_titles,re.IGNORECASE).group(1).split(','):
		name = name.replace(" ","_")
		if name in vocab and name!=heroName and not name in heroData['doesCounter']:
			heroData['doesCounter'].append(vocab[name])
	heroData['doesCounter'] = sorted(set(heroData['doesCounter']))

	for name in re.search("Edit section: Works well with(.*?)(Edit section|Special)",all_titles,re.IGNORECASE).group(1).split(','):
		name = name.replace(" ","_")
		if name in vocab and name!=heroName and not name in heroData['synergy']:
			heroData['synergy'].append(vocab[name])
	heroData['synergy'] = sorted(set(heroData['synergy']))

	return heroData

def generateCMat(pageUrl,vocab):
	temp = {}
	cmat = np.zeros((len(vocab)+1,len(vocab)+1))
	for hero in vocab:
		time.sleep(1)
		print(hero)
		heroData = getHeroData(pageUrl,hero,vocab)
		r = vocab[hero]
		for c in heroData['counteredBy']:
			cmat[r][c]+=3.0
		for c in heroData['doesCounter']:
			cmat[r][c]+=5.0
		for c in heroData['synergy']:
			cmat[r][c]+=7.0
	return cmat

def getHeroAttrTable(page_url,heroDict,typeDict, opfile="dota2HeroStats.csv"):

	request = urllib.request.Request(page_url)

	response = urllib.request.urlopen(request)

	pageSource = response.read().decode('utf-8')

	soup = BeautifulSoup(pageSource, 'html.parser')

	heroTable = soup.find('table')

	headers = [   th.find('span')['title'] for th in heroTable.find('tr').find_all('th') if th.find('span') ]

	attrTable = np.zeros((len(heroDict)+1,len(headers)))

	r,c = 0, 0
	for row in heroTable.find_all('tr'):
		if row.find('td'):
			for td in row.find_all('td'):
				if td.find('a'):
					val = td.find('a')['title'].strip().replace(" ","_")
					if( val in heroDict):
						r = heroDict[val]
						c = 0
					elif (val in typeDict):
						attrTable[r][c] = float(typeDict[val])
						c+=1
					else:
						print("ERROR:Parsing table failed")
						print(row,td)
						exit()
				else:
					attrTable[r][c] = float(td.text.strip())
					c+=1

	# print(heroDict)
	# print(typeDict)
	# for hero in heroDict:
	# 	print(hero,attrTable[heroDict[hero]])

	finalTable = attrTable[1:]

	normTable = finalTable/finalTable.max(axis=0)

	print(normTable)


	return normTable

	
		


if __name__=="__main__":

	dota2_gamepedia_page_categories_url = "https://dota2.gamepedia.com/Category:Counters"
	dota2_gamepedia_page_url = "https://dota2.gamepedia.com"
	reCompute = False
	hero_type_dict = { "Strength" : 1,"Agility" :2 , "Intelligence" : 3 }
	PCA_components = 10
	TSNE_components = 2

	hero_name_dict = buildVocab(dota2_gamepedia_page_categories_url)
	hero_name_reverse_dict = dict( zip( hero_name_dict.values(),hero_name_dict.keys() ) )

	if reCompute:
		# print(getHeroData(dota2_gamepedia_page_url,"Ogre_Magi",hero_name_dict))
		cmat = generateCMat(dota2_gamepedia_page_url,hero_name_dict)
		np.save('dota2_hero_cmat',cmat)

	#cmat = np.load('dota2_hero_cmat.npy')

	atrTable = getHeroAttrTable(dota2_gamepedia_page_url+"/Table_of_hero_attributes",hero_name_dict,hero_type_dict)

	pcaAtrTable = PCA(n_components=PCA_components).fit_transform(atrTable)

	atEmbeding = TSNE(n_components=TSNE_components,verbose=1, random_state=0, n_iter=1000).fit_transform(atrTable)

	x_coords , y_coords = atEmbeding[:,0], atEmbeding[:,1]

	plt.scatter(x_coords, y_coords)

	for label, x, y in zip(hero_name_dict.keys(), x_coords, y_coords):
		plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
	plt.xlim(x_coords.min()+0.00005, x_coords.max()+0.00005)
	plt.ylim(y_coords.min()+0.00005, y_coords.max()+0.00005)
	plt.show()


	# Clustering
	# for n in range(2,20):
	# 	clustering = MiniBatchKMeans(n_clusters=n,verbose=True).fit(atrTable)
	# 	print("Iter:"+str(n)+"\tMax Iterations for convergence:"+str(clustering.n_iter_)+"\tInertia:"+str(clustering.inertia_))

	# clustering = MiniBatchKMeans(n_clusters=5,verbose=True).fit(atEmbeding)

	# plt.scatter(x_coords, y_coords,c=clustering.labels_)

	# for label, x, y in zip(hero_name_dict.keys(), x_coords, y_coords):
	# 	plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
	# plt.xlim(x_coords.min()+0.00005, x_coords.max()+0.00005)
	# plt.ylim(y_coords.min()+0.00005, y_coords.max()+0.00005)
	# plt.show()




