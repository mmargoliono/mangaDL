import urllib.request as urlReq
import os
import zipfile
from bs4 import BeautifulSoup


url = 'http://www.batoto.net/read/_/147955/houkago%E2%98%86idol_by_casanova/48'
content = urlReq.urlopen(url).read()
soup = BeautifulSoup(content)


output = "/tmp/tmp_manga/"


pages = soup.find(id='page_select')
page_count = len(pages.find_all('option'))

digits = len(str(page_count))
digits_format = "{0:0" + str(digits) + "d}"

img = soup.find(id='comic_page')
#asssume three character extension plus dot
img_base = img['src'][:-4 - digits ]
img_ext = img['src'][-4:]

for n in range(1, page_count + 1):
    nImageBase = img_base + digits_format.format(n)
    nUrl = nImageBase + img_ext
    print (nUrl)

    try:
        urlReq.urlretrieve(nUrl, output + digits_format.format(n) + img_ext)
    except urlReq.HTTPError as E:
        if img_ext != '.jpg':
            nUrl = nImageBase + '.jpg'
        else:
            nUrl = nImageBase + '.png'
        
        try: 
            urlReq.urlretrieve(nUrl, output + digits_format.format(n) + img_ext)
        except urlReq.HTTPError as innerE:
            print ('Unexpected case')


zipf = zipfile.ZipFile(output + 'comics.cbz', 'w')

for root, dirs, files in os.walk(output):
    for file in files:
        zipf.write(os.path.join(root, file), file)

zipf.close()

