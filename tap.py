import epo_ops
import xmltodict, json
import xml.etree.ElementTree as ET
import sys

def beautify(response):
	#the function gets rid of some troublesome namespaces in the xml
	string='<ops:world-patent-data xmlns="http://www.epo.org/exchange" xmlns:ops="http://ops.epo.org" xmlns:xlink="http://www.w3.org/1999/xlink">'
	string1='</ops:world-patent-data>'
	xml=response.content
	xml=xml.replace(string,'')
	xml=xml.replace(string1,'')
	return xml

def get_dates():
	#gives publication and application dates
	publication_date=tree.find('.//publication-reference/document-id[@document-id-type="epodoc"]/date').text
	priority_list=[]
	for i in range(1,10):
		prior_date=tree.find('.//priority-claims/priority-claim[@sequence="'+str(i)+'"]/document-id[@document-id-type="epodoc"]/date')
		if prior_date!= None:
			priority_list.append(int(prior_date.text))
		else:
			break
	return publication_date, priority_list

def savefile(xml):
	with open('data.xml', 'w') as f:
		f.write(xml)

def published_data(client):

	response = client.published_data(  # Retrieve bibliography data
  reference_type = 'publication',  # publication, application, priority
  input = epo_ops.models.Docdb('101430697', 'CN', 'B'),  # original, docdb, epodoc
  endpoint = 'biblio',  # optional, defaults to biblio in case of published_data
   #optional, list of constituents
   )
	return response


#main
if __name__ == "__main__":

	pat= sys.argv # to be used in case of working with agrguments
	client = epo_ops.Client(key='GTfPiUhprNpUavoL2B1WBT7MK0y1A3jw', secret='b1D4WcgkXNXQ5VTq')  # Instantiate client

	#get data from epo
	response=published_data(client)
	

	xml=beautify(response) #cleaning XML

	savefile(xml) #saving XML doc for parsing

	tree = ET.parse('data.xml')
	root = tree.getroot()

	pat_num=tree.find('.//publication-reference/document-id[@document-id-type="epodoc"]/doc-number').text #obselete stuff
	publication_date, priority_list= get_dates()
	assignee =	tree.find('.//parties/applicants/applicant/[@data-format="original"]/applicant-name/name').text #many has data-format="original"
	try:
		title = tree.find('.//invention-title[@lang="en"]').text #some times not present, cases CN
	except AttributeError:
		print "Error: Title could not be extracted!"
		title="Error!!!"
	print pat_num, assignee, title, publication_date, priority_list 
