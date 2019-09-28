import epo_ops
from lxml import etree as ET
from mailmerge import MailMerge
from datetime import date

NS = {
    "ops": "http://ops.epo.org",
    "epo": "http://www.epo.org/exchange",
    "ft": "http://www.epo.org/fulltext",
    "reg": "http://www.epo.org/register",
}

patent_list='EP1417800B1'

def read_patent_from_excel(path):
	df=path #to be developed


def get_kind_code(patent):
	# assumes country code is of two characters
	patent=(str(patent)).strip().replace(" ","") #sanatization, remove spaces
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

            data["family_id"] = document.attrib["family-id"]
            bib_data = document.find("./epo:bibliographic-data", NS)
            title=get_title(bib_data) #title
            pub, prior=get_the_dates(bib_data) #dates
            assignee=get_assignee(bib_data)#assignee/applicant
       
            #data logging

            data["title"]= title
            data["publication_date"]= pub
            data['earliest priority']= min(prior)
            data['assignee']=assignee

   	return data
    
def get_assignee(bib_data):
	assignee =	bib_data.find('./epo:parties/epo:applicants/epo:applicant/[@data-format="original"]/epo:applicant-name/epo:name', NS).text #many has data-format="original"
	return assignee


def get_title(bib_data):
	title = bib_data.find("./epo:invention-title[@lang='en']", NS).text
	if title is None: #when title in not present in english
		title = bib_data.find("./epo:invention-title", NS)
	return title

def XMLparser(response):
	xml=response.text
	tree = ET.fromstring(xml.encode("utf-8"))  
	return tree

def published_data_api(client):
	response=get_published_data(client) #get the xml
	tree = XMLparser(response) #parse the xml
	bib_data=get_bibdata(tree, NS) #get all biblo (title, dates)
	return bib_data

def get_family_data(tree):
	doc_db_list = list()
	for el in tree.findall("./ops:patent-family/ops:family-member", NS):
		pub_ref = el.find('./epo:publication-reference/epo:document-id[@document-id-type="docdb"]',NS)
		if pub_ref is not None:

			a=get_complete_patent_num(pub_ref)

			doc_db_list.append(a)

		app_ref = el.find('./epo:application-reference/epo:document-id[@document-id-type="docdb"]',NS)	

		if app_ref is not None:
			
			b=get_complete_patent_num(app_ref)

			doc_db_list.append(b)

	return doc_db_list

def get_complete_patent_num(base_object): 
	number=base_object.find('./epo:doc-number',NS).text
	country=base_object.find('./epo:country',NS).text
	kind=base_object.find('./epo:kind',NS).text

	return country+number+kind


# API Calls

def family_data_api(client):
	country, pat_num, kind= get_kind_code(patent_list)
	response=client.family(reference_type='publication', 
		input=epo_ops.models.Docdb(pat_num, country, kind), 
		endpoint=None, constituents=None)
	tree = XMLparser(response)

	return get_family_data(tree)

def get_published_data(client):
	country, pat_num, kind= get_kind_code(patent_list)
	response = client.published_data(  # Retrieve bibliography data
  reference_type = 'publication',  # publication, application, priority
  input = epo_ops.models.Docdb(pat_num, country, kind),  # original, docdb, epodoc
  endpoint = 'biblio',  # optional, defaults to biblio in case of published_data
   #optional, list of constituents
   )
	return response

if __name__ == "__main__":
	
	client = epo_ops.Client(key='62kB2O6tJtmG2RQsoOMJZUOhmbAlAkJ5', secret='WpsdCAOg9GyWw8i1')  # Instantiate client
	print published_data_api(client)
	print family_data_api(client)
	data = published_data_api(client)
	family = family_data_api(client)


#Playground below:
	
'''
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