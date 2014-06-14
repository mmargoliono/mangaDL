import tempfile
import zipfile
import gzip
import io
import re
import os
import urllib.request as urlreq

from bs4 import BeautifulSoup

class BaseDownloader():
    ''' A comic downloader that will crawl website and download the image as an archive. '''

    def __init__(self, url, output, chapters=1, initial_chapter=1):
        ''' Init the downloader with the download options. '''
        self.url = url
        self.output = output
        self.current_chapter = initial_chapter
        self.chapters = chapters

    def download(self):
        ''' Download manga based on the option specified. '''
        if self.chapters > 1:
            chapter_names = []
            with tempfile.TemporaryDirectory() as temp_chapter_folder:
                for url in self.get_chapters_urls(self.url, self.chapters):
                    soup = self.get_page_soup(url)
                    chapter_title = self.get_chapter_title(soup)
                    omake_number = self.get_omake_number(chapter_title)

                    chapter_archive = self.get_archive_name(omake_number)
                    chapter_output = temp_chapter_folder + "/" + chapter_archive
                    self.download_chapter_archive(soup, chapter_output)
                    chapter_names.append(chapter_archive + ':' + chapter_title)

                self.write_comic_info(self.output, chapter_names, temp_chapter_folder + "/")
        else:
            soup = self.get_page_soup(self.url)
            self.download_chapter_archive(soup, self.output)

    def get_chapters_urls(self, start_url, chapter_count):
        ''' Get the list of chapter's base url. '''        
        url = start_url
        yield url
        for i in range(chapter_count - 1):
            soup = self.get_page_soup(url)
            url = self.get_next_chapter_url(soup)
            yield url

    def get_page_content(self, url):
        ''' Get a webpage content string. '''
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
        ''' Get a webpage as a BeautifulSoup object. '''
        content = self.get_page_content(url)
        return BeautifulSoup(content)

    def download_image(self, url, target_file):
        ''' Download a single image. '''
        try:
            urlreq.urlretrieve(url, target_file)
            print (url + ' -> ' + target_file)
        except urlreq.HTTPError as E:
            print ('Can not get ' + url)

    def download_chapter_images(self, target_folder, soup):
        ''' Download a chapter images to a folder. '''
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
        ''' Download a chapter as a zip archive. '''
        print (archive_name)
        with tempfile.TemporaryDirectory() as temp_images_folder:
            self.download_chapter_images(temp_images_folder + "/", soup)
            self.zip_and_zap(temp_images_folder, archive_name)

    def get_omake_number(self, chapter_title):
        ''' Get a dot point number for omake chapter. '''
        match = re.match(r'.*\d+\.(\d).*', chapter_title)
        if match:
            omake_number = int(match.group(1))
            return omake_number

        match = re.match(r'.*(?:O|o)make\s*(\d).*', chapter_title)
        if match:
            omake_number = int(match.group(1))
            return omake_number

        match = re.match(r'.*(?:O|o)make((:.*)|$)', chapter_title)
        if match:
            omake_number = 5
            return omake_number

        return 0

    def get_archive_name(self, omake_number):
        ''' Get archive name for the current chapter. '''
        if omake_number != 0:
            return "ch " +str(self.current_chapter).zfill(3) + "." + str(omake_number)  + ".cbz"
        else:
            archive_name = "ch " +str(self.current_chapter).zfill(3) + ".cbz"
            self.current_chapter = self.current_chapter + 1
            return archive_name

    def zip_and_zap(self, target_folder, output_file):
        ''' Create a zip archive and remove source files. '''
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
        ''' Create a comic book collection.
        
        The comic will be created as calibre comic format (.cbc).
        See: http://manual.calibre-ebook.com/conversion.html#comic-book-collections
        '''
        with open(temp_chapter_folder + 'comics.txt', 'w') as comics_info:
            comics_info.write('\n'.join(chapter_names))
        self.zip_and_zap(temp_chapter_folder, output)
