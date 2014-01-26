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

class BaseDownloader:


    def __init__(self, url, output, chapters=1, initial_chapter=1):
        self.url = url
        self.output = output
        self.initial_chapter = initial_chapter
        self.chapters = chapters

    def download(self):
        soup = self.get_page_soup(self.url)
        if self.chapters > 1:
            chapter_names = []
            downloaded_chapter = 0
            index = 0

            with tempfile.TemporaryDirectory() as temp_chapter_folder:
                while index < self.chapters:
                    chapter_title = self.get_chapter_title(soup)
                    omake_number = self.get_omake_number(chapter_title)

                    chapter = self.initial_chapter + downloaded_chapter
                    chapter_archive = self.get_archive_name(chapter, omake_number)
                    chapter_output = temp_chapter_folder + "/" + chapter_archive
                    self.download_chapter_archive(soup, chapter_output)
                    chapter_names.append(chapter_archive + ':' + chapter_title)

                    if downloaded_chapter != args.chapters - 1 or omake_number > 0:
                        soup = self.get_next_chapter_soup_traverse(soup)

                    if omake_number == 0:
                        downloaded_chapter = downloaded_chapter + 1

                    index = index + 1
                self.write_comic_info(self.output, chapter_names, temp_chapter_folder + "/")
        else:
            self.download_chapter_archive(soup, self.output)


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

    def download_chapter_images(self, target_folder, soup):
        page_count = self.get_page_count(soup)
        digits = len(str(page_count))
        for n in range(1, page_count + 1):
            formatted_n = str(n).zfill(digits)
            url = self.get_image_url(soup)
            target_file = target_folder + formatted_n + url[-4:]
            self.download_image(url, target_file)
            soup = self.get_next_page_soup(soup)

    def download_chapter_archive(self, soup, archive_name):
        print (archive_name)
        with tempfile.TemporaryDirectory() as temp_images_folder:
            self.download_chapter_images(temp_images_folder + "/", soup)
            self.zip_and_zap(temp_images_folder, archive_name)

    def get_omake_number(self, chapter_title):
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

    def get_archive_name(self, chapter, omake_number):
        if omake_number != 0:
            return "ch " +str(chapter - 1).zfill(3) + "." + str(omake_number)  + ".cbz"
        else:
            return "ch " +str(chapter).zfill(3) + ".cbz"

    def zip_and_zap(self, target_folder, output_file):
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

    def write_comic_info(self, output, chapter_names, temp_chapter_folder):
        with open(temp_chapter_folder + 'comics.txt', 'w') as comics_info:
            comics_info.write('\n'.join(chapter_names))
        self.zip_and_zap(temp_chapter_folder, output)



class BatotoDownloader(BaseDownloader):


    def get_page_count(self, soup):
        pages = soup.find(id='page_select')
        page_count = len(pages.find_all('option'))
        return page_count

    def get_image_url(self, soup):
        img = soup.find(id = 'comic_page')
        return img['src']

    def get_current_chapter_tag(self, soup):
        chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
        current_chapter = chapter_select.find("option", selected="selected")
        return current_chapter

    def get_chapter_title(self, soup):
        current_chapter_tag = self.get_current_chapter_tag(soup)
        chapter_title = current_chapter_tag.string
        chapter_title = re.sub(r'(.*\d+)(?:v|V)\d(.*)',r'\1\2', chapter_title)
        return chapter_title

    def get_next_page_soup(self, soup):
        img = soup.find(id='comic_page')
        next_page_url = img.parent['href']
        return self.get_page_soup(next_page_url)

    def get_next_chapter_soup_traverse(self, soup):
        pages = soup.find(id='page_select')
        last_page = pages.find_all('option')[-1]
        last_page_soup = self.get_page_soup(last_page['value'])
        return self.get_next_page_soup(last_page_soup)


def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output', default = "/tmp/comics.cbz")
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded', default=1)
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence', default=1)
    return parser.parse_args()

if __name__ == '__main__':
    args = setup_arguments()
    downloader = BatotoDownloader(args.url, args.output, args.chapters, args.initialchapter)
    downloader.download()
