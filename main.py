import urllib.request as urlReq
import os
import zipfile
import argparse
import io
import gzip

from bs4 import BeautifulSoup

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output directory')
    parser.add_argument('-c', '--chapters', type=int, help = 'How many chapters should be downloaded')
    return parser.parse_args()

def get_page_content(url):
    response = urlReq.urlopen(url)
    content = response.read()
    if response.headers['Content-Encoding'] == 'gzip':
        compressedstream = io.BytesIO(content)
        gzipper = gzip.GzipFile(fileobj=compressedstream, mode="rb")
        content = gzipper.read()
    return content

def zip_and_zap(target_folder, output_file):
    zipf = zipfile.ZipFile(output_file, 'w')

    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, file)
            os.remove(file_path)

    zipf.close()
    os.rmdir(target_folder)

def download_chapter_images(target_folder, base_image_url, default_ext):
    for n in range(1, page_count + 1):
        nImageBase = base_image_url + digits_format.format(n)
        nUrl = nImageBase + default_ext
        print (nUrl)

        try:
            urlReq.urlretrieve(nUrl, target_folder + digits_format.format(n) + default_ext)
        except urlReq.HTTPError as E:
            if default_ext != '.jpg':
                nUrl = nImageBase + '.jpg'
            else:
                nUrl = nImageBase + '.png'

            try:
                urlReq.urlretrieve(nUrl, target_folder + digits_format.format(n) + default_ext)
            except urlReq.HTTPError as innerE:
                print ('Unexpected case')


args = setup_arguments()

output = "/tmp/comics.cbz"
temp_dl_folder = "/tmp/tmp_manga/"
chapters = 1

url = args.url
if args.output:
    output = args.output

if args.chapters:
    chapters = args.chapters

for ch in range(1, chapters + 1):
    content = get_page_content(url)
    soup = BeautifulSoup(content)

    pages = soup.find(id='page_select')
    page_count = len(pages.find_all('option'))

    if ch < chapters:
        chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
        current_chapter = chapter_select.find("option", selected="selected")
        next_chapter = current_chapter.previous_sibling
        url = next_chapter['value']

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

    chapter_output = output
    if chapters > 1:
        chapter_output = output + "ch-" + str(ch) + ".cbz"

    try:
        os.remove(chapter_output)
    except OSError:
        pass

    download_chapter_images(temp_dl_folder, img_base, img_ext)
    zip_and_zap(temp_dl_folder, chapter_output)

