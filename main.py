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
    parser.add_argument('-o', '--output', help = 'Archive output')
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded')
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence')
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

def download_chapter_images(target_folder, base_image_url, default_ext, page_count):
    for n in range(1, page_count + 1):
        formatted_n = str(n).zfill(digits)
        nImageBase = base_image_url + formatted_n
        nUrl = nImageBase + default_ext
        print (nUrl)

        try:
            urlReq.urlretrieve(nUrl, target_folder + formatted_n + default_ext)
        except urlReq.HTTPError as E:
            if default_ext != '.jpg':
                nUrl = nImageBase + '.jpg'
            else:
                nUrl = nImageBase + '.png'

            try:
                urlReq.urlretrieve(nUrl, target_folder + formatted_n + default_ext)
            except urlReq.HTTPError as innerE:
                print ('Unexpected case')


args = setup_arguments()

output = "/tmp/comics.cbz"
temp_dl_folder = "/tmp/tmp_manga/images/"
temp_chapter_folder = "/tmp/tmp_manga/chapters/"
chapters = 1
initial_chapter = 1

url = args.url
if args.output:
    output = args.output

if args.chapters:
    chapters = args.chapters

if args.initialchapter:
    initial_chapter = args.initialchapter

chapter_names = []

for ch in range(0, chapters):
    chapter_output = output
    chapter_archive = "ch-" + str(ch + initial_chapter).zfill(3) + ".cbz"
    print (chapter_archive)

    if chapters > 1:
        chapter_output = temp_chapter_folder + chapter_archive

    content = get_page_content(url)
    soup = BeautifulSoup(content)

    pages = soup.find(id='page_select')
    page_count = len(pages.find_all('option'))

    chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
    current_chapter = chapter_select.find("option", selected="selected")
    next_chapter = current_chapter.previous_sibling
    url = next_chapter['value']
    chapter_title = current_chapter.string
    chapter_names.append(chapter_archive + ':' + chapter_title)

    digits = len(str(page_count))

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
        os.makedirs(temp_chapter_folder)
    except OSError:
        pass

    try:
        os.remove(chapter_output)
    except OSError:
        pass

    download_chapter_images(temp_dl_folder, img_base, img_ext, page_count)
    zip_and_zap(temp_dl_folder, chapter_output)

if chapters > 1:
    with open(temp_chapter_folder + 'comics.txt', 'w') as comics_info:
        comics_info.write('\n'.join(chapter_names))
    zip_and_zap(temp_chapter_folder, output)
