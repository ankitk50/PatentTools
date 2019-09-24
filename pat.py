import epo_ops
import xmltodict, json
import xml.etree.ElementTree as ET
import pprint 
client = epo_ops.Client(key='62kB2O6tJtmG2RQsoOMJZUOhmbAlAkJ5', secret='WpsdCAOg9GyWw8i1')  # Instantiate client
response = client.published_data(  # Retrieve bibliography data
  reference_type = 'publication',  # publication, application, priority
  input = epo_ops.models.Docdb('1417800', 'EP', 'B1'),  # original, docdb, epodoc
  endpoint = 'biblio',  # optional, defaults to biblio in case of published_data
   # optional, list of constituents
)

doc = xmltodict.parse(response.text)

#print doc 

data=[]
for article in doc['ops:world-patent-data']['exchange-documents']['exchange-document']['bibliographic-data']['publication-reference']['document-id']:
    if article['@document-id-type'] == 'docdb':
    	#print article
    	country=article['country']
        patnum = country + article['doc-number']
        
        kind = article['kind']
        publication_date = article['date']
        print "Patent Num:", patnum+kind+ ", has the publication date: ", publication_date
        break

da=doc['ops:world-patent-data']['exchange-documents']['exchange-document']['bibliographic-data']['priority-claims']['priority-claim'][1]
da=da['document-id'][0]
priorpat = da['doc-number']
priority_date = da['date']
print "here"

print priorpat
print priority_date

#print "Patent Num:", patnum+ ", has the priority date: ", priority_date +", the patent takes the priority from ",priorpat 
   
