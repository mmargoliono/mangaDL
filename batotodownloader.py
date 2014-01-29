import re
from basedownloader import BaseDownloader

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

    def get_next_page_url(self, soup):
        img = soup.find(id='comic_page')
        next_page_url = img.parent['href']
        return next_page_url

    def get_next_chapter_url(self, soup):
        pages = soup.find(id='page_select')
        last_page = pages.find_all('option')[-1]
        last_page_soup = self.get_page_soup(last_page['value'])
        return self.get_next_page_url(last_page_soup)
