import urllib2
import simplejson
from bs4 import BeautifulSoup
#opening the patent
URL = 'https://www.google.co.in/patents/US5606609'
req = urllib2.Request(URL, headers={'User-Agent' : "python"})
_file = urllib2.urlopen(req)
patent_html = _file.read()
soup = BeautifulSoup(patent_html, 'html.parser')
bibKeys=("Publication number","Publication type","Application number","Publication Date","Filing Date","Priority Date","Fee status")
bibList={}
#fetching the patent number
patentNumber = soup.find("span", { "class" : "patent-number" }).text
#fetching the assignee
assigneeMetaTag = soup.find("meta", { "scheme" : "assignee"})
patentAssignee = assigneeMetaTag.attrs["content"]
print "Assignee: ",patentAssignee
#fetching the claims
claimTag=soup.find("div", { "class" : "claim-text"}).text
#fetching all the inventors
def getInventorNames():
	inventor=soup.find_all("meta", { "scheme" : "inventor",})
	i=1
	dist=len(inventor)
	inventorName=""
	for tag in inventor:
		inventorName=inventorName+tag['content']
		if i<dist:
			inventorName=inventorName+", "
		i=i+1
		#print tag['content']
	print "Inventors:",inventorName
#another way to fetch filing and publication , although priority can't be scraped using this	
filingDate=soup.find("meta", { "scheme" : "dateSubmitted"})
publicationDate=soup.find("meta", { "scheme" : "issued"})
#mainBibData
def mainBibData():
	i=0
	bibData=soup.find_all("td",{ "class":"single-patent-bibdata"})
	for ptag in bibData:
		bibList[bibKeys[i]]=ptag.text
		i=i+1
		print ptag.text
	print bibList.items()
mainBibData()
getInventorNames()
#print bibList['Publication number']