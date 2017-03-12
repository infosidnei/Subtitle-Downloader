import requests
import re
import zipfile
import os
from bs4 import BeautifulSoup

movieFolder = "E:\Movies"

def ToWords(num):
	map={"1":"first","2":"second","3":"third","4":"fourth","5":"fifth","6":"sixth","7":"seventh"
			,"8":"eight","9":"ninth","10":"tenth","11":"eleventh","12":"twelfth"}

	return map[num]

def findpath(name,*args):

	s1=args[0]
	s=args[1]

	for path, directories, _, in os.walk(movieFolder):
		
		for directory in directories:

			if(re.sub('[^a-zA-Z0-9 \n]',' ',directory)[:len(name)].lower().strip() == name.lower().strip()):

				if(s1 == s):
					return os.path.join(path,directory)
				else:
					for subpath, subdirs, _, in os.walk(os.path.join(path,directory)):
						break
					for subdir in subdirs:
						if("season "+s1[len(s1)-1] in re.sub('[^a-zA-Z0-9 \n]',' ',subdir).lower().strip()):
							return os.path.join(subpath,subdir)

					return os.path.join(path,directory)

def changeExtension(path):

	commonext=[".mp4",".mkv",".mpeg",".avi",".mpg",".srt",".zip"]
	filenames = os.listdir(path)

	for filename in filenames:
		ext = os.path.splitext(os.path.join(path,filename))[1]
		if(ext not in commonext):
			os.rename(os.path.join(path,filename),os.path.join(path,filename.replace(ext,".srt")))


def download_subs(page,s1,path):

	
	print "Downloading Subtitles"
	print ""

	try:
		play=open(os.path.join(path,s1+".zip"),"wb")
	except:
		if( not os.path.exists( os.path.join(movieFolder,"Subtitles") ) ):
			os.makedirs( os.path.join(movieFolder,"Subtitles") )

			
	path = os.path.join(movieFolder, "Subtitles")
	play=open(os.path.join(path,s1+".zip"),"wb")
	
	for chunk in page.iter_content(200000):
		play.write(chunk)
	
	play.close()

	print "extracting subtitles"
	print ""
	
	play = zipfile.ZipFile(os.path.join(path,s1+".zip"),'r')
	play.extractall(path)
	play.close()

	print "subtiles extracted in ", path

	changeExtension(path)

def subscene_subtitle_downloader(s):
		url="https://subscene.com"
		#print "enter movie name"
		#s = raw_input()
		print "enter episode name if any"
		e = raw_input()


		#adjusting names
		
		if(e != ""):
			e = int(e)
			if(e / 10 == 0):
				e="0"+str(e)
		else:
			eregex=re.compile("E\d\d",re.IGNORECASE)

		name=s[:s.lower().find('season')]
		s1=s

		if(re.search(name+'Season '+'[0-9]+',s,re.IGNORECASE)):
			s=name+""+ToWords(s[len(s)-1])+" season"
		else:
			name=s

		print s

		page=requests.get(url+"/subtitles/title?q="+s.replace(' ','+')+"&l=")
		soup=BeautifulSoup(page.text,"html.parser")

		links=soup.find_all("div",class_="search-result")[0].find_all("a",href=True)
		present=False

		for link in links:
			#print link.string
			if(link.string[:link.string.find("(")].replace('-','').replace(' ','').lower() == s.replace(' ','').lower()):
				present=True
				break

		if(not present):

			print s+" subtitle not present in https://subscene.com checking in yify"
			yify_subtitle_downloader(s)
		else:

			print link['href']
			page=requests.get(url+link['href'])
			soup=BeautifulSoup(page.text,"html.parser")

			i=0
			string=""
			subs=[]
			links = soup.find_all("tbody")[0].find_all("td",class_="a1")

			print "Preparing List"
			print ""

			for link in links:

				if(link.find("span").string.strip() == "English" ):

					string = link.find("span").find_next_sibling("span").string.strip()
					
					if(e != "" and "E"+str(e)in string ):
						subs.append(link.find("a",href=True)['href'])
						print i,")"
						print string
						print " "
						i=i+1
					elif(e == "" and eregex.search(string) == None):
						subs.append(link.find("a",href=True)['href'])
						print i,")"
						try:
							print string
						except UnicodeEncodeError:
							print ""
						print " "
						i=i+1
			try:			
				print "enter the index to be downloaded"
				i = int(raw_input())
			except ValueError:
				print " "
			else:
				page = requests.get(url + subs[i])
				soup = BeautifulSoup(page.text,"html.parser")
				page=requests.get(url + soup.find_all("div",class_="download")[0].find("a",href=True)['href'])

				download_subs(page,s1,findpath(name,s1,s))

def yify_subtitle_downloader(s):

	site="http://www.yifysubtitles.com"
	page = requests.get(site+"/search?q="+s)
	soup=BeautifulSoup(page.text,"html.parser")

	#find the correct movie from the list of movies

	movies = soup.find_all("h3",class_="media-heading")

	try:
		for movie in movies:
			if(movie.string.lower() == s.lower()):
				break

		url = movie.find_parent("a").find_parent("div").find("a",href=True)['href']

	except NameError:
		print s+" subtitle is not present in "+site

	else:
		page = requests.get(site+url)
		soup = BeautifulSoup(page.text,"html.parser")

		# listing of all the english subtitles

		movies = soup.find_all("span",class_="sub-lang")
		subs=[] #list of all subtitles
		ratings=[]# list of ratings of english subtitles

		for movie in movies:
			if(movie.string == "English"):
				subs.append(movie.find_next("a",href=True)['href'])
				ratings.append(movie.find_parent("td").find_previous_sibling("td").find("span").string)

		for i in xrange(len(subs)):
			print i,")"
			print "rating = " ,ratings[i]
			print "subtitle :"
			print subs[i][11:]

		try:
			print "enter the index of subtitle to download"
			index = int(raw_input())
		except ValueError:
			print " "
		else:	

			page=requests.get(site+"/subtitle"+subs[index][10:]+".zip")

			download_subs(page,s,findpath(s))

def main():
	print "enter movie name"
	s = str(raw_input())
	subscene_subtitle_downloader(s)

if __name__ == "__main__":main()