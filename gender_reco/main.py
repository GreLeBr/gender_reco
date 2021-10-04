from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from lxml import html
import requests
import re
import os

site="https://www.project-a.com/"
savelocation="/data"
direc=site[12:-5]
page_list=[]
resultsss=[]
img_lins=[]
formats= ["jpg", "png", "gif", "jpeg"] #"svg"
relevant_pages=["job", "about", "career", "jobs", "careers", "join", "team"]

def process_links(links):
  """ Function to process the list of links and filter required links."""
  links_list = []
  for link in links:
      # if os.path.splitext(link)[1][1:].strip().lower() in formats:
      if link[-3:].lower() in formats:
          links_list.append(link)
  return links_list  

response = requests.get(site)
soup = BeautifulSoup(response.text, 'html.parser')
for x in soup.find_all("a"):  
  if "href" in x.attrs.keys():
    if x.string != None:
      if x.string != None and x.string.lower() in relevant_pages:
        if 'http' not in x.attrs["href"]:
            resultsss.append(site[:-1]+x.attrs["href"])
        else:  resultsss.append(x.attrs["href"])    
      if x.span and len([s for s in relevant_pages if s in x.span.text.lower()])>0: # and x.span.text.lower().split()) in relevant_pages:
        if 'http' not in x.attrs["href"]:
            resultsss.append(site[:-1]+x.attrs["href"])
        else:  resultsss.append(x.attrs["href"])  
      # page_list.append(x.string.lower())
      # found_page=
      # for x.string.lower() in relevant_pages:
      #   print(x)
# for s in [x for x in page_list if x in relevant_pages]:
#     if 'http' not in x.attrs["href"]:
#       resultsss.append(site+x.attrs["href"])
#       else:  resultsss.append(x.attrs["href"])    
#     if x.span and len([s for s in relevant_pages if s in x.span.text.lower()])>0: # and x.span.text.lower().split()) in relevant_pages:
#       if 'http' not in x.attrs["href"]:
#           resultsss.append(site+x.attrs["href"])
#       else:  resultsss.append(x.attrs["href"])  
resultsss
if resultsss !=[]:
  for s in resultsss:
    site1=s
    tree = html.fromstring(response.text)

    response = requests.get(site1)
    img = tree.xpath('//img/@src')
    links = tree.xpath('//a/@href')
    img_list = process_links(img)
    img_links = process_links(links)
    img_list.extend(img_links)

    # soup = BeautifulSoup(response.text, 'html.parser')
    # img_tags = soup.find_all(['picture', "img"])
    # Making sure I capture the pictures, only jpg and gif for now, should it be gif only?

 

    # for x in img_list:
    #   urlparse(x)

    
    for x in img_list:
      # if urlparse(x)..path[-3:] in format_list:
      if urlparse(x).scheme=="":
        x="https:"+x
      if urlparse(x).netloc=="":
        x=site+x
      img_request = requests.request('get', x, stream=True)
      if img_request.status_code==200:
        if x[-3:] != "svg" or int(img_request.headers["Content-Length"])>1000:
            img_content = img_request.content
            base=f"{savelocation}/{direc}/"
            if os.path.exists(base) is False:
                  os.mkdir(base)
            with open(base+x.split('/')[-1], 'wb') as f:
                byte_image = bytes(img_content)
                f.write(byte_image)
