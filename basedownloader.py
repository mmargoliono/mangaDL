import tempfile
import zipfile
import gzip
import io
import re
import os
import urllib.request as urlreq

from bs4 import BeautifulSoup

class BaseDownloader():


    def __init__(self, url, output, chapters=1, initial_chapter=1):
        self.url = url
        self.output = output
        self.initial_chapter = initial_chapter
        self.chapters = chapters

    def download(self):
        if self.chapters > 1:
            chapter_names = []
            urls = self.get_chapters_urls(self.url, self.chapters)
            downloaded_chapter = 0

            with tempfile.TemporaryDirectory() as temp_chapter_folder:
                for url in urls:
                    soup = self.get_page_soup(url)
                    chapter_title = self.get_chapter_title(soup)
                    omake_number = self.get_omake_number(chapter_title)

                    chapter = self.initial_chapter + downloaded_chapter
                    chapter_archive = self.get_archive_name(chapter, omake_number)
                    chapter_output = temp_chapter_folder + "/" + chapter_archive
                    self.download_chapter_archive(soup, chapter_output)
                    chapter_names.append(chapter_archive + ':' + chapter_title)

                    if omake_number == 0:
                        downloaded_chapter = downloaded_chapter + 1

                self.write_comic_info(self.output, chapter_names, temp_chapter_folder + "/")
        else:
            soup = self.get_page_soup(self.url)
            self.download_chapter_archive(soup, self.output)

    def get_chapters_urls(self, start_url, chapter_count):
        urls = [start_url]
        url = start_url
        for i in range(chapter_count - 1):
            soup = self.get_page_soup(url)
            url = self.get_next_chapter_url(soup)
            urls.append(url)
        return urls

    def get_page_content(self, url):
        request = urlreq.Request(url)
        request.add_header("Accept-Encoding","gzip")
        response = urlreq.urlopen(request)
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
            urlreq.urlretrieve(url, target_file)
            print (url + ' -> ' + target_file)
        except urlreq.HTTPError as E:
            print ('Can not get ' + url)

    def download_chapter_images(self, target_folder, soup):
        page_count = self.get_page_count(soup)
        digits = len(str(page_count))
        for n in range(1, page_count + 1):
            formatted_n = str(n).zfill(digits)
            url = self.get_image_url(soup)
            target_file = target_folder + formatted_n + url[-4:]
            self.download_image(url, target_file)
            next_page_url = self.get_next_page_url(soup)
            soup = self.get_page_soup(next_page_url)

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
