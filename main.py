#/usr/bin/python3

import urllib.request as urlReq
import os
import zipfile
import argparse
import io
import gzip
import re

from bs4 import BeautifulSoup

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output', default = "/tmp/comics.cbz")
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded', default=1)
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence', default=1)
    parser.add_argument('-q', '--questionable', action="store_true", help = 'Some hack for testing purposes')
    parser.add_argument('-e', '--exact', action="store_true", help = 'Get next image by parsing instead of guessing. ' +
                                                                     'This is slower but more accurate.')
    return parser.parse_args()

def get_page_content(url):
    response = urlReq.urlopen(url)
    content = response.read()
    if response.headers['Content-Encoding'] == 'gzip':
        compressedstream = io.BytesIO(content)
        gzipper = gzip.GzipFile(fileobj=compressedstream, mode="rb")
        content = gzipper.read()
    return content

def get_image_url(soup):
    img = soup.find(id='comic_page')
    return img['src']

def zip_and_zap(target_folder, output_file):
    try:
        os.remove(output_file)
    except OSError:
        pass

    zipf = zipfile.ZipFile(output_file, 'w')

    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, file)
            os.remove(file_path)

    zipf.close()

def download_chapter_images(target_folder, soup, page_count):
    img_url = get_image_url(soup)
    digits = len(str(page_count))

    #asssume three character extension plus dot
    base_image_url = img_url[:-4 - digits ]
    default_ext = img_url[-4:]

    for n in range(1, page_count + 1):
        formatted_n = str(n).zfill(digits)

        if args.exact:
            url, soup = get_next_image_url_by_parse(soup)
        else:
            url = get_next_image_url_by_pattern(base_image_url, default_ext, formatted_n)

        target_file = target_folder + formatted_n + url[-4:]

        if args.exact:
            download_image(url, target_file, False)
        else:
            download_chapter_image_by_trial(url, target_file);


def get_next_image_url_by_pattern(base_image_url, default_ext, formmated_n):
    return base_image_url + formatted_n + default_ext

def get_next_image_url_by_parse(soup):
    img = soup.find(id='comic_page')
    next_page_url = img.parent['href']
    content = get_page_content(next_page_url)
    soup = BeautifulSoup(content)
    return img['src'], soup

def download_chapter_image_by_trial(url, target_file):
    try:
        download_image(url, target_file, True)
    except urlReq.HTTPError as E:
        if url[-4:] != '.jpg':
            url = url[:4] + ".jpg"
            target_file = target_file[:4] + ".jpg"
        else:
            url = url[:4] + ".png"
            target_file = target_file[:4] + ".png"

        try:
            download_image(url, target_file, True)
        except urlReq.HTTPError as innerE:
            print ('Unexpected case')


def download_image(url, target_file, should_throw):
    try:
        urlReq.urlretrieve(url, target_file)
        print (url + ' -> ' + target_file)
    except urlReq.HTTPError as E:
        print ('Can not get ' + url)
        if (should_throw):
            raise urlReq.HTTPError(E)


args = setup_arguments()

temp_dl_folder = "/tmp/tmp_manga/images/"
temp_chapter_folder = "/tmp/tmp_manga/chapters/"

url = args.url

chapter_names = []

# Prepare temp dl folder
try:
    os.makedirs(temp_dl_folder)
except OSError:
    pass

if args.chapters > 1:
    try:
        os.makedirs(temp_chapter_folder)
    except OSError:
        pass

ch = 0

while ch < args.chapters:
    chapter_output = args.output
    chapter_archive = "ch " + str(ch + args.initialchapter).zfill(3) + ".cbz"

    content = get_page_content(url)
    soup = BeautifulSoup(content)

    pages = soup.find(id='page_select')
    page_count = len(pages.find_all('option'))

    chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
    current_chapter = chapter_select.find("option", selected="selected")
    next_chapter = current_chapter.previous_sibling

    if ch != args.chapters - 1:
        url = next_chapter['value']

    chapter_title = current_chapter.string

    if (args.questionable):
        # Remove v2 or v3 in chapter name
        chapter_title = re.sub(r'(.*\d+)(?:v|V)\d(.*)',r'\1\2', chapter_title)
        if (re.match(r'.*\d+\.\d.*', chapter_title)):
            print (" omake? " + chapter_title)
            ch = ch - 1
            chapter_archive = "ch " +str(ch + args.initialchapter).zfill(3) + ".5.cbz"

    chapter_names.append(chapter_archive + ':' + chapter_title)

    if args.chapters > 1:
        chapter_output = temp_chapter_folder + chapter_archive

    print(chapter_archive)
    download_chapter_images(temp_dl_folder, soup, page_count)
    zip_and_zap(temp_dl_folder, chapter_output)

    ch = ch + 1

if args.chapters > 1:
    with open(temp_chapter_folder + 'comics.txt', 'w') as comics_info:
        comics_info.write('\n'.join(chapter_names))
    zip_and_zap(temp_chapter_folder, args.output)
