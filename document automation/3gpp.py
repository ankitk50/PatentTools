import urllib
from bs4 import BeautifulSoup
import pandas as pd 


def export_to_excel(frame):
	frame.to_excel("output.xlsx")
	print ("***Excel downloaded!***")

def push_to_mainframe(frame,data,col):
	f1= pd.DataFrame(data, index=[0], columns=col) #make a data frame from dict
	return frame.append(f1,ignore_index = True)

def make_url(input_n):
	if input_n//10==0: #adding a leading zero
		input_n="0"+str(input_n)

	ref_n=str(input_n).replace(".","")
	url ="https://www.3gpp.org/DynaReport/"+ref_n+".htm"
	return url

#opening the URL
def get_all_data(url):
	URL = url
	_file = urllib.request.urlopen(URL)
	patent_html = _file.read()
	soup = BeautifulSoup(patent_html, 'html.parser')
	#print(soup.prettify()) # view the html

	#intializing bilbliographic data
	data = dict()
	
	twog_val=0
	threeg_val=0
	lte_val=0
	fiveg_val=0

	#fetching data
	ref = soup.find("span", { "id" : "referenceVal" }).text
	title = soup.find("span", { "id" : "titleVal" }).text
	tstype = soup.find("span", { "id" : "typeVal" }).text
	ipr = soup.find("span", { "id" : "initialPlannedReleaseVal" }).text

	if soup.find(id="radioTechnologyVals_0", checked="checked"):
		twog_val= 1

	elif soup.find(id="radioTechnologyVals_1", checked="checked"):
		threeg_val= 1

	elif soup.find(id="radioTechnologyVals_2", checked="checked"):
		lte_val= 1

	elif soup.find(id="radioTechnologyVals_3", checked="checked"):
		fiveg_val= 1

	data[col[0]]= ref
	data[col[1]]= title
	data[col[2]]= tstype
	data[col[3]]= ipr
	data[col[4]]= twog_val
	data[col[5]]= threeg_val
	data[col[6]]= lte_val
	data[col[7]]= fiveg_val

	return data

#data=get_all_data()
#print (data)
#input execel

excel_file='input.xlsx'
df_input=pd.read_excel(excel_file)
df_input=df_input.dropna()

#output dataframe init
col=["Reference","Title","Type","Initial Planned Release","2G","3G","LTE","5G"]
df_output=pd.DataFrame()



for i in range(df_input.shape[0]):
	        iref=df_input.iloc(0)[i][0]
	        URL=make_url(iref)
	        data=get_all_data(URL)
	        print(URL)
	        print(data)
	        df_output=push_to_mainframe(df_output,data,col)

export_to_excel(df_output)


