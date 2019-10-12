import urllib2
import simplejson
from bs4 import BeautifulSoup

URL = 'https://www.google.co.in/patents/US5606609'
req = urllib2.Request(URL, headers={'User-Agent' : "python"})
_file = urllib2.urlopen(req)
patent_html = _file.read()
soup = BeautifulSoup(patent_html, 'html.parser')
patentNumber = soup.find("span", { "class" : "patent-number" }).text
assigneeMetaTag = soup.find("meta", { "scheme" : "assignee"})
patentAssignee = assigneeMetaTag.attrs["content"]
claimTag=soup.find("div", { "class" : "claim-text"}).text
claimTag2=soup.find("div",{"num" :"2"}).text
print "patent no.: ", patentNumber
print "assignee: ", patentAssignee
print claimTag2
