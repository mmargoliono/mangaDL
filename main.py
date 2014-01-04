import urllib.request as urlReq
import os
import zipfile
import argparse

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('url', help = 'Url of any page within a chapter')
parser.add_argument('-o', '--output', help = 'Archive output directory')
args = parser.parse_args()

output = "/tmp/comics.cbz"
temp_dl_folder = "/tmp/tmp_manga/"

url = args.url
if args.output:
    output = args.output

response = urlReq.urlopen(url)
content = response.read()
soup = BeautifulSoup(content)

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
        urlReq.urlretrieve(nUrl, temp_dl_folder + digits_format.format(n) + img_ext)
    except urlReq.HTTPError as E:
        if img_ext != '.jpg':
            nUrl = nImageBase + '.jpg'
        else:
            nUrl = nImageBase + '.png'
        
        try: 
            urlReq.urlretrieve(nUrl, temp_dl_folder + digits_format.format(n) + img_ext)
        except urlReq.HTTPError as innerE:
            print ('Unexpected case')


zipf = zipfile.ZipFile(output, 'w')

for root, dirs, files in os.walk(temp_dl_folder):
    for file in files:
        zipf.write(os.path.join(root, file), file)

zipf.close()

