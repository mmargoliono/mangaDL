import urllib.request as urlReq
import os
import zipfile
import argparse
import io
import gzip

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
if response.headers['Content-Encoding'] == 'gzip':
    compressedstream = io.BytesIO(content)
    gzipper = gzip.GzipFile(fileobj=compressedstream, mode="rb")
    content = gzipper.read()

soup = BeautifulSoup(content)

pages = soup.find(id='page_select')
page_count = len(pages.find_all('option'))

digits = len(str(page_count))
digits_format = "{0:0" + str(digits) + "d}"

img = soup.find(id='comic_page')
#asssume three character extension plus dot
img_base = img['src'][:-4 - digits ]
img_ext = img['src'][-4:]

# Prepare temp dl folder
try:
    os.makedirs(temp_dl_folder)
except OSError:
    pass

try:
    os.remove(output)
except OSError:
    pass

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
        file_path = os.path.join(root, file)
        zipf.write(file_path, file)
        os.remove(file_path)

zipf.close()

os.rmdir(temp_dl_folder)
