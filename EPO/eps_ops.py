import epo_ops
from lxml import etree as ET
from datetime import date
from mailmerge import MailMerge
from report_ui import *
import pandas as pd
import time


NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}
#US5606609A, EP1417800B1 
#patent_list=['EP1417800B1']

def read_patent_from_excel(path):
	df=path #to be developed

def save_to_xmlfile(xml):
	with open('data_family.xml', 'w') as f: #get xml response
		f.write(xml)

def get_kind_code(patent):
	# assumes country code is of two characters
	patent=(str(patent)).strip().replace(" ","") #sanitization, remove spaces
	kind=""
	number= patent[2:]
	country= patent[:2]
	lastchar=patent[-1]
	secondlastchar=patent[-2]

	if (ord(lastchar)>64 and ord(lastchar)<91) or (ord(secondlastchar)>96 and ord(secondlastchar)<123) : #if last char is alphabet
		kind =lastchar 	#last character is the kind code
		number=patent[2:-1]

	if ord(lastchar)>48 and ord(lastchar)<58: #check if integer
		if (ord(secondlastchar)>64 and ord(secondlastchar)<91) or (ord(secondlastchar)>96 and ord(secondlastchar)<123):
			kind= secondlastchar+lastchar #last two characters are kind code
			number=patent[2:-2]
		else:
			print "Kind code absent or some alein characters in the patent number", patent
			#raise exeception, do not process the patent

#make US applications Espacenet compatible
	if country=='US':
		if len(number)> 10:
			if number[4]=='0':
				number=number[:4]+number[5:]

	return country, number, kind




def get_the_dates(bib_data):

	priority_list=[]
	#gives publication and application dates
	pub_date=bib_data.find("./epo:publication-reference/epo:document-id[@document-id-type='epodoc']/epo:date", NS).text
	i=1
	while(1):
		prior_date=bib_data.find('./epo:priority-claims/epo:priority-claim[@sequence="'+str(i)+'"]/epo:document-id[@document-id-type="epodoc"]/epo:date', NS)
		if prior_date!= None:
			priority_list.append(int(prior_date.text))
			i=i+1
		else:
			break
	return pub_date, priority_list


def get_bibdata(tree, NS):
	documents = tree.findall("./epo:exchange-documents/epo:exchange-document", NS)
	for document in documents:
            data = dict()

            #scraping

            data["Family Id"] = document.attrib["family-id"]
            bib_data = document.find("./epo:bibliographic-data", NS)
            #Dates
            app_date=get_application_date(bib_data)
            pub, prior=get_the_dates(bib_data)

            try:
            	title=get_title(bib_data) #title
            except AttributeError:
            	title=" "
            	pass

            try:
            	assignee=get_assignee(bib_data)#assignee/applicant
            except AttributeError:
            	assignee=" "
            	pass

            try:	
            	inventors=get_inventor_data(bib_data)
            except AttributeError:
            	inventors=" "
            	pass
            #data logging

            data["Title"]= title
            data["Publication date"]= pub
            data['Earliest priority']= str(min(prior)) #
            data['Assignee']=assignee
            data['Application Date']=app_date
            data['Inventors']=inventors[:-2]

	return data
    
def get_assignee(bib_data):
	assignee =	bib_data.find('./epo:parties/epo:applicants/epo:applicant/[@data-format="original"]/epo:applicant-name/epo:name', NS).text #many has data-format="original"
	return assignee

def get_application_date(bib_data):
	app_date =	bib_data.find("./epo:application-reference/epo:document-id[@document-id-type='epodoc']/epo:date", NS).text #many has data-format="original"
	return app_date

def get_title(bib_data):

	title = bib_data.find("./epo:invention-title[@lang='en']", NS).text
	if title is None: #when title in not present in english
		title = bib_data.find("./epo:invention-title", NS)
	return title

def XMLparser(response):
	xml=response.text
	tree = ET.fromstring(xml.encode("utf-8"))  
	return tree


def get_family_data(tree):
	doc_db_list = list()
	
	for el in tree.findall("./ops:patent-family/ops:family-member", NS):
		pub_ref = el.find('./epo:publication-reference/epo:document-id[@document-id-type="docdb"]',NS)
		if pub_ref is not None:

			a=get_complete_patent_num(pub_ref)

			doc_db_list.append(a) #can return from here, no need to execute further for published ones
			

		app_ref = el.find('./epo:application-reference/epo:document-id[@document-id-type="docdb"]',NS)	

		if app_ref is not None:
			
			b=get_complete_patent_num(app_ref) #not being used for now in the output of family members

			#doc_db_list.append(b)
			

	return doc_db_list

def get_inventor_data(tree):
	inventor_name = ""
	
	for el in tree.findall('./epo:parties/epo:inventors/epo:inventor[@data-format="original"]/epo:inventor-name/epo:name', NS):
		inventor_name += el.text
		#print inventor_name
	return inventor_name



def get_complete_patent_num(base_object): 
	number=base_object.find('./epo:doc-number',NS).text
	country=base_object.find('./epo:country',NS).text
	kind=base_object.find('./epo:kind',NS).text

	return country+number+kind

#############################################################
# API Calls

def family_data_api(client, patent): #returns complete family data
	country, pat_num, kind= get_kind_code(patent)
	response=client.family(reference_type='publication', 
		input=epo_ops.models.Docdb(pat_num, country, kind), 
		endpoint=None, constituents=None)
	#save_to_xmlfile(response.content) #view xml response
	tree = XMLparser(response)

	return get_family_data(tree)

def published_data_api(client, patent): #returns complete biblio data
	country, pat_num, kind= get_kind_code(patent)
	response = client.published_data(  # Retrieve bibliography data
  reference_type = 'publication',  # publication, application, priority
  input = epo_ops.models.Docdb(pat_num, country, kind),  # original, docdb, epodoc
  endpoint = 'biblio',  # optional, defaults to biblio in case of published_data
   #optional, list of constituents
   )
	tree = XMLparser(response) #parse the xml
	bib_data=get_bibdata(tree, NS) #get all biblo (title, dates)
	return bib_data

##############################################################

def export_to_excel(frame):
	frame.to_excel("output.xlsx")
	print "***Excel downloaded!***"

def push_to_mainframe(frame,data):
	f1= pd.DataFrame(data, index=[0], columns=col) #make a data frame from dict
	return frame.append(f1,ignore_index = True) #append data frame to the main frame
	
def list_to_str(lst):
	string=""
	for element in lst:
		string+= str(element) + "| "

	return string

def populate_doc(frameX,frameY,patent_listX, patent_listY):
    template = "TEMPLATE 5.docx"
    document = MailMerge(template)
    XListofdict=[]
    YListofdict=[]
    XList2ofdict=[]
   
    for x in range(len(patent_listX)):
    	Xdict={}
        Xdict["X_PAT_NUMBER"]=frameX.iloc[x,0]
        Xdict["X_PAT_TITLE"]=frameX.iloc[x,1]
        Xdict["X_PAT_ASSIGNEE"]=frameX.iloc[x,6]
        Xdict["X_PAT_PUBDATE"]=frameX.iloc[x,5]
        Xdict["X_PAT_APPDATE"]=frameX.iloc[x,3]
        Xdict["X_PAT_PRIORDATE"]=frameX.iloc[x,4]
        Xdict["X_PAT_INVENTORS"]=frameX.iloc[x,7]
        Xdict["X_PAT_FAMILY"]=frameX.iloc[x,8]
        XListofdict.append(Xdict)

    if len(patent_listY)>1:
    	print patent_listY
    	for x in range(len(patent_listY)):
    		Ydict={}
	        Ydict["Y_PAT_NUMBER"]=frameY.iloc[x,0]
        	Ydict["Y_PAT_TITLE"]=frameY.iloc[x,1]
       		Ydict["Y_PAT_ASSIGNEE"]=frameY.iloc[x,6]
        	Ydict["Y_PAT_PUBDATE"]=frameY.iloc[x,5]
        	Ydict["Y_PAT_APPDATE"]=frameY.iloc[x,3]
        	Ydict["Y_PAT_PRIORDATE"]=frameY.iloc[x,4]
        	Ydict["Y_PAT_INVENTORS"]=frameY.iloc[x,7]
        	Ydict["Y_PAT_FAMILY"]=frameY.iloc[x,8]
        	YListofdict.append(Ydict)

    for x in range(len(patent_listX)):
        Xdict1 = {}
        Xdict1["X_PAT_{}_NUMBER".format(x+1)]=frameX.iloc[x,0]
        Xdict1["X_PAT_{}_TITLE".format(x+1)]=frameX.iloc[x,1]
        Xdict1["X_PAT_{}_ASSIGNEE".format(x+1)]=frameX.iloc[x,6]
        Xdict1["X_PAT_{}_PUBDATE".format(x+1)]=frameX.iloc[x,5]
        Xdict1["X_PAT_{}_APPDATE".format(x+1)]=frameX.iloc[x,3]
        Xdict1["X_PAT_{}_PRIORDATE".format(x+1)]=frameX.iloc[x,4]
        Xdict1["X_PAT_{}_INVENTORS".format(x+1)]=frameX.iloc[x,7]
        Xdict1["X_PAT_{}_FAMILY".format(x+1)]=frameX.iloc[x,8]
        XList2ofdict.append(Xdict1)

    #print YListofdict    
    document.merge_rows('X_PAT_NUMBER', XListofdict)
    document.merge_rows('Y_PAT_NUMBER', YListofdict)
    document.merge_pages(XList2ofdict)
    #document.merge(**Ydict)
    document.write('NEW REPORT1.docx')

# US8139109B2,US5606609A,EP1417800B1
if __name__ == "__main__":

	frameX=pd.DataFrame() #define mainframe
	frameY=pd.DataFrame()
	col=['Patent No.', 'Title', 'Family Id', 'Application Date','Earliest priority', 'Publication date', 'Assignee','Inventors','Family members']
	client = epo_ops.Client(key='62kB2O6tJtmG2RQsoOMJZUOhmbAlAkJ5', secret='WpsdCAOg9GyWw8i1')  # Instantiate client
	patent_listX, patent_listY, dir_path, f1, f2= main() #to work with gui

	tick= time.time() #start timer

	for patent in patent_listX:
		try:
			print "\n Processing "+patent+ "....\n"
			data = published_data_api(client,patent)
			family_list = family_data_api(client, patent) #list and piper separated string
			data['Family members']=list_to_str(list(set(family_list)))[:-2] #remove last piper and cache to dict #list(set(data)) removes duplicates, 
			data['Patent No.']=patent.replace(" ","")
			frameX=push_to_mainframe(frameX,data)
			print data

		except epo_ops.exceptions.MissingRequiredValue:
			print patent, ": ERROR: Number, country code and kind code must be present!"
			pass
		except :
			print "HTTP Error"
			pass
	
	for patent in patent_listY:
		try:
			print "\n Processing "+patent+ "....\n"
			data = published_data_api(client,patent)
			family_list = family_data_api(client, patent) #list and piper separated string
			data['Family members']=list_to_str(list(set(family_list)))[:-2] #remove last piper and cache to dict #list(set(data)) removes duplicates, 
			data['Patent No.']=patent.replace(" ","")
			frameY=push_to_mainframe(frameY,data)
			print data

		except epo_ops.exceptions.MissingRequiredValue:
			print patent, ": ERROR: Number, country code and kind code must be present!"
			pass
		except :
			print "HTTP Error"
			pass

	#print frame.head()
	export_to_excel(frameX) #export to excel sheet # default name output.xlsx
	populate_doc(frameX,frameY,patent_listX, patent_listY)
	tock=time.time()
	print "Execution time: ", tock-tick, " Sec"





#Playground below:
# US8139109B2,US5606609A,EP1417800B1
'''
def write_to_xml(tree):
	tree.write('output11.xml')

documents = tree.findall("./epo:exchange-documents/epo:exchange-document", NS)
for document in documents:
	i=1
	while(1):
		bib_data = document.find("./epo:bibliographic-data", NS)
		pub_date=bib_data.find("./epo:publication-reference/epo:document-id[@document-id-type='epodoc']/epo:date", NS).text
		prior_date=bib_data.find('./epo:priority-claims/epo:priority-claim[@sequence="'+str(i)+'"]/epo:document-id[@document-id-type="epodoc"]/epo:date', NS)
		if prior_date!= None:
			priority_list.append(int(prior_date.text))
			i=i+1
		else:
			break
	print pub_date, priority_list
'''
'''
documents = tree.findall("./epo:exchange-documents/epo:exchange-document", NS)
	for document in documents:
	            data = dict()
	            data["family_id"] = document.attrib["family-id"]
	            bib_data = document.find("./epo:bibliographic-data", NS)
	            title = bib_data.find("./epo:invention-title[@lang='en']", NS).text
	            if title is None: #when title in not present in english
	                title = bib_data.find("./epo:invention-title", NS)
	            pub_date=bib_data.find("./epo:publication-reference/epo:document-id[@document-id-type='epodoc']/epo:date", NS).text
	
	print bib_data, title, pub_date
'''