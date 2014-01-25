#!/usr/bin/env python

import urllib.request as urlReq
import os
import zipfile
import argparse
import io
import gzip
import re
import tempfile

from bs4 import BeautifulSoup

class DownloadHelper:


    def get_page_content(self, url):
        request = urlReq.Request(url)
        request.add_header("Accept-Encoding","gzip")
        response = urlReq.urlopen(request)
        content = response.read()
        if response.headers['Content-Encoding'] == 'gzip':
            compressedstream = io.BytesIO(content)
            gzipper = gzip.GzipFile(fileobj=compressedstream, mode="rb")
            content = gzipper.read()

        return content

    def get_page_soup(self, url):
        content = self.get_page_content(url)
        return BeautifulSoup(content)

    def download_image(self, url, target_file):
        try:
            urlReq.urlretrieve(url, target_file)
            print (url + ' -> ' + target_file)
        except urlReq.HTTPError as E:
            print ('Can not get ' + url)


download_helper = DownloadHelper()

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output', default = "/tmp/comics.cbz")
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded', default=1)
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence', default=1)
    return parser.parse_args()

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

def download_chapter_images(target_folder, soup):
    page_count = get_page_count(soup)
    digits = len(str(page_count))
    for n in range(1, page_count + 1):
        formatted_n = str(n).zfill(digits)
        url = get_image_url(soup)
        soup = get_next_page_soup(soup)
        target_file = target_folder + formatted_n + url[-4:]
        download_helper.download_image(url, target_file)

def get_next_image_url_by_pattern(soup, digits, formatted_n):
    img_url = get_image_url(soup)

    #asssume three character extension plus dot
    base_image_url = img_url[:-4 - digits ]
    default_ext = img_url[-4:]
    return base_image_url + formatted_n + default_ext

def get_next_page_soup(soup):
    img = soup.find(id='comic_page')
    next_page_url = img.parent['href']
    return download_helper.get_page_soup(next_page_url)


def write_comic_info(output, chapter_names, temp_chapter_folder):
    with open(temp_chapter_folder + 'comics.txt', 'w') as comics_info:
        comics_info.write('\n'.join(chapter_names))
    zip_and_zap(temp_chapter_folder, output)

def download_chapter_archive(soup, archive_name):
    print (archive_name)
    with tempfile.TemporaryDirectory() as temp_images_folder:
        download_chapter_images(temp_images_folder + "/", soup)
        zip_and_zap(temp_images_folder, archive_name)

def get_current_chapter_tag(soup):
    chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
    current_chapter = chapter_select.find("option", selected="selected")
    return current_chapter

def get_chapter_title(soup):
    current_chapter_tag = get_current_chapter_tag(soup)
    chapter_title = current_chapter_tag.string
    chapter_title = re.sub(r'(.*\d+)(?:v|V)\d(.*)',r'\1\2', chapter_title)
    return chapter_title

def get_next_chapter_soup_traverse(soup):
    pages = soup.find(id='page_select')
    last_page = pages.find_all('option')[-1]    
    last_page_soup = download_helper.get_page_soup(last_page['value'])    
    return get_next_page_soup(last_page_soup)

def get_page_count(soup):
    pages = soup.find(id='page_select')
    page_count = len(pages.find_all('option'))
    return page_count

def get_omake_number(chapter_title):
    omake_number = 0
    match = re.match(r'.*\d+\.(\d).*', chapter_title)
    if match:
        omake_number = int(match.group(1))
    else:
        match = re.match(r'.*(?:O|o)make\s*(\d).*', chapter_title)
        if match:
            omake_number = int(match.group(1))
        else:
            match = re.match(r'.*(?:O|o)make((:.*)|$)', chapter_title)
            if match:
                omake_number = 5

    if omake_number != 0:
        print (str(omake_number) + " omake? " + chapter_title)

    return omake_number

def get_archive_name(chapter, omake_number):
    if omake_number != 0:
        return "ch " +str(chapter - 1).zfill(3) + "." + str(omake_number)  + ".cbz"
    else:
        return "ch " +str(chapter).zfill(3) + ".cbz"

def main():
    args = setup_arguments()
    soup = download_helper.get_page_soup(args.url)

    if args.chapters > 1:
        chapter_names = []
        downloaded_chapter = 0
        index = 0

        with tempfile.TemporaryDirectory() as temp_chapter_folder:
            while index < args.chapters:
                chapter_title = get_chapter_title(soup)
                omake_number = get_omake_number(chapter_title)

                chapter = args.initialchapter + downloaded_chapter
                chapter_archive = get_archive_name(chapter, omake_number)
                chapter_output = temp_chapter_folder + "/" + chapter_archive
                download_chapter_archive(soup, chapter_output)
                chapter_names.append(chapter_archive + ':' + chapter_title)

                if downloaded_chapter != args.chapters - 1 or omake_number > 0:
                    soup = get_next_chapter_soup_traverse(soup)

                if omake_number == 0:
                    downloaded_chapter = downloaded_chapter + 1
                
                index = index + 1
            write_comic_info(args.output, chapter_names, temp_chapter_folder + "/")
    else:
        download_chapter_archive(soup, args.output)

if __name__ == '__main__':
    main()
