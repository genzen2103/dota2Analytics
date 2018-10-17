
import urllib.request
import re
from bs4 import BeautifulSoup
import time

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






if __name__=="__main__":

	dota2_gamepedia_page_categories_url = "https://dota2.gamepedia.com/Category:Counters"
	dota2_gamepedia_page_url = "https://dota2.gamepedia.com"

	hero_name_dict = buildVocab(dota2_gamepedia_page_categories_url)

	hero_name_reverse_dict = dict( zip( hero_name_dict.values(),hero_name_dict.keys() ) )

	# print(getHeroData(dota2_gamepedia_page_url,"Ogre_Magi",hero_name_dict))

	for heroName in hero_name_dict:
		print(heroName)
		time.sleep(1)
		heroData = getHeroData(dota2_gamepedia_page_url,heroName,hero_name_dict)
		print(heroName+"->"+",".join([ hero_name_reverse_dict[i] for i in heroData['counteredBy'] ] ))














