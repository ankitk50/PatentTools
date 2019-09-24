import epo_ops
import xmltodict, json
import xml.etree.ElementTree as ET
import pprint 

client = epo_ops.Client(key='GTfPiUhprNpUavoL2B1WBT7MK0y1A3jw', secret='b1D4WcgkXNXQ5VTq')  # Instantiate client
response = client.published_data(  # Retrieve bibliography data
  reference_type = 'publication',  # publication, application, priority
  input = epo_ops.models.Docdb('1417800', 'EP', 'B1'),  # original, docdb, epodoc
  endpoint = 'biblio',  # optional, defaults to biblio in case of published_data
   # optional, list of constituents
)
xml=response.content


with open('data.xml', 'w') as f:
    f.write(xml)

tree = ET.parse('data.xml')
root = tree.getroot()
print root[0]

for child in root:
	print child.tag, child.attrib
	node2= ET.Element(child.tag)

node= ET.Element("publication-reference")
print node

pat_num=tree.find('.//publication-reference/document-id[@document-id-type="epodoc"]/doc-number').text
publication_date=tree.find('.//publication-reference/document-id[@document-id-type="epodoc"]/date').text
priority_list=[]
for i in range(1,10):
	prior_date=tree.find('.//priority-claims/priority-claim[@sequence="'+str(i)+'"]/document-id[@document-id-type="epodoc"]/date')
	if prior_date!= None:
		priority_list.append(int(prior_date.text))
	else:
		break
assignee =	tree.find('.//parties/applicants/applicant/[@data-format="epodoc"]/applicant-name/name').text
title = tree.find('.//invention-title[@lang="en"]').text
print pat_num, publication_date, min(priority_list), assignee, title #use min for earliest priority


