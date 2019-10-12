import urllib2
import simplejson
from bs4 import BeautifulSoup
import pandas as pd 

#opening the patent
claimNum="1"
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
#print "Assignee: ",patentAssignee
#fetching the claims
claimTag=soup.find("div", { "class" : "claim-text"}).text
claimTag2=soup.find("div",{"num" :claimNum}).text
#print "Claim:",claimTag2
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
	#print "Inventors:",inventorName
	return inventorName
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
	bibList["Claim"]=claimTag
	bibList["Inventors"]=getInventorNames()
	bibList["Assignee"]=patentAssignee
	#print bibList.items()
mainBibData()
#print bibList.items()
df=pd.DataFrame(bibList,index=[0])
print df.head()

df.to_csv('PythonExport.csv', sep=',')

from mailmerge import MailMerge
from datetime import date

df=pd.read_csv('PythonExport.csv')
print(df.iloc[0,1])
template = "123.docx"
document = MailMerge(template)
print(document.get_merge_fields())
di={"Name":"Sherni"}
document.merge(
    status='Gold',
    city='Springfield',
    phone_number=df.iloc[0,2],
    Business=df.iloc[0,1],
    zip=df.iloc[0,3],
    purchases=df.iloc[0,4],
    shipping_limit=df.iloc[0,5],
    state=df.iloc[0,6],
    address='1234 Main Street',
    date='{:%d-%b-%Y}'.format(date.today()),
    discount='5%',
    recipient="sdfs")

document.write('test-outpufinalt2.docx')
# plan  to dump data in a file