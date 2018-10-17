
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






if __name__=="__main__":

	dota2_gamepedia_page_categories_url = "https://dota2.gamepedia.com/Category:Counters"
	dota2_gamepedia_page_url = "https://dota2.gamepedia.com"
	reCompute = False
	PCA_components = 30
	TSNE_components = 2

	hero_name_dict = buildVocab(dota2_gamepedia_page_categories_url)
	hero_name_reverse_dict = dict( zip( hero_name_dict.values(),hero_name_dict.keys() ) )

	if reCompute:
		# print(getHeroData(dota2_gamepedia_page_url,"Ogre_Magi",hero_name_dict))
		cmat = generateCMat(dota2_gamepedia_page_url,hero_name_dict)
		np.save('dota2_hero_cmat',cmat)

	cmat = np.load('dota2_hero_cmat.npy')
	print(",".join( ["Hero"]+list(hero_name_dict.keys()) ))
	for hero in hero_name_dict:
		print(hero+",".join( map( str,cmat[hero_name_dict[hero]] ) )
			.replace("12.0","GOOD_VERSES_WORKS_WITH")
			.replace("10.0","BAD_VERSES_WORKS_WITH")
			.replace("8.0","CONFUSED")
			.replace("7.0","WORKS_WITH")
			.replace("5.0","GOOD_VERSES")
			.replace("3.0","BAD_VERSES")
			.replace("0.0","")													
			)




	# ### Visualize data using TSNE

	# pcaCmat = PCA(n_components=PCA_components).fit_transform(cmat)

	# cmatEmbeding = TSNE(n_components=TSNE_components,verbose=1, random_state=0, n_iter=1000).fit_transform(pcaCmat)

	# x_coords , y_coords = cmatEmbeding[:,0], cmatEmbeding[:,1]

	# plt.scatter(x_coords, y_coords)

	# for label, x, y in zip(hero_name_dict.keys(), x_coords, y_coords):
	# 	plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
	# plt.xlim(x_coords.min()+0.00005, x_coords.max()+0.00005)
	# plt.ylim(y_coords.min()+0.00005, y_coords.max()+0.00005)
	# plt.show()


	## Clustering
	# for n in range(2,100):
	# 	clustering = KMeans(n_clusters=3,verbose=False).fit(pcaCmat)
	# 	print("Iter:"+str(n)+"\tMax Iterations for convergence:"+str(clustering.n_iter_)+"\tInertia:"+str(clustering.inertia_))

	# clustering = MiniBatchKMeans(n_clusters=7,verbose=True).fit(cmat)

	# plt.scatter(x_coords, y_coords,c=clustering.labels_)

	# for label, x, y in zip(hero_name_dict.keys(), x_coords, y_coords):
	# 	plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
	# plt.xlim(x_coords.min()+0.00005, x_coords.max()+0.00005)
	# plt.ylim(y_coords.min()+0.00005, y_coords.max()+0.00005)
	# plt.show()












