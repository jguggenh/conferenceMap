from urllib import request
from datetime import datetime
import re

class Conference(object):
    def __init__(self):
        # MSAR
        self.abbrv = ''
        self.name = ''
        self.citations = 0
        self.H = 0
        self.category = ''
        # WikiCFP
        self.url = ''
        self.date = datetime.now()
        self.location = ''
        self.deadline = datetime.now()

    def __repr__(self):
        return ('abbrv:"' + self.abbrv + '",'
                'name:"' + self.name + '",'
                'citations:"' + str(self.citations) + '",'
                'H:"' + str(self.H) + '",'
                'category:"' + self.category + '",'
                'url:"' + self.url + '",'
                'date:"' + str(self.date) + '",'
                'location:"' + self.location + '",'
                'deadline:"' + str(self.deadline) + '",'
                )

    def toJS(self):
        return ('\t{'
                '\n\t\t"abbrv": "'    + self.abbrv          + '",'
                '\n\t\t"name": "'     + self.name           + '",'
                '\n\t\t"citations": ' + str(self.citations) + ','
                '\n\t\t"H": '         + str(self.H)         + ','
                '\n\t\t"category": "' + self.category       + '",'
                '\n\t\t"url": "'      + self.url            + '",'
                '\n\t\t"date": "'     + datetime.strftime(self.date,'%Y-%m-%d') + '",'
                '\n\t\t"location": "' + self.location       + '",'
                '\n\t\t"deadline": "' + datetime.strftime(self.deadline,'%Y-%m-%d') + '"'
                '\n\t}')

print('Scraping...this will take some time.')
html_msar = str(request.urlopen('http://www.conferenceranks.com/data/msar.min.js').read())
conferences = []
for token in re.finditer(r'{"abbrv":"([^"]+)","name":"([^"]+)","citations":(\d+),"H":(\d+),"category":"([^"]+)"}',html_msar):
    c = Conference()
    
    # Read Data from MSAR token
    c.abbrv = token.group(1)
    c.name = token.group(2)
    c.citations = int(token.group(3))
    c.H = int(token.group(4))
    c.category = token.group(5)
    
    # Look Up Conference in WikiCFP to Scrape Remaining Data
    url_name = re.sub(' ','+',c.name)
    url_wikicfp = 'http://www.wikicfp.com/cfp/servlet/tool.search?q=' + url_name + '&year=t'
    html_wikicfp = str(request.urlopen(url_wikicfp).read())
    try:
        url_info = 'http://www.wikicfp.com' + re.findall(r'<td rowspan="2" align="left"><a href="([^"]+)">',html_wikicfp)[0]
        html_info = str(request.urlopen(url_info).read())
        c.url = re.findall(r'Link: <a href="([^"]+)"',html_info)[0]
        datestr = re.findall(r'<th>When</th>[^/]+?([A-Za-z]+ \d+, \d+)',html_info)[0]
        c.date = datetime.strptime(datestr,'%b %d, %Y')
        c.location = re.findall(r'<th>Where</th>[^/]+?([A-Za-z ,]+)</td>',html_info)[0]
        datestr = re.findall(r'<th>Submission Deadline</th>.+?([A-Za-z]+ \d+, \d+)',html_info)[0]
        c.deadline = datetime.strptime(datestr,'%b %d, %Y')
        
        conferences.append(c)
    except IndexError:
        print('Unable to scrape information for ' + c.name)

    if len(conferences)>10:
        break

# Write Conferences to JS File
print('Writing Data to File')
with open('conferences.js','w') as file:
    file.write('var conference = [\n')
    file.write(conferences[0].toJS())
    for c in conferences[1:]:
        file.write(',\n' + c.toJS())
    file.write('\n];')

print('Done.')
