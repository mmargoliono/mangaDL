import re
from basedownloader import BaseDownloader

class BatotoDownloader(BaseDownloader):
    ''' Downloader implementation that are targeted at batoto.com '''

    def get_page_count(self, soup):
        ''' Get the number of pages in the chapter '''
        pages = soup.find(id='page_select')
        page_count = len(pages.find_all('option'))
        return page_count

    def get_image_url(self, soup):
        ''' Get current page's image url '''
        img = soup.find(id = 'comic_page')
        return img['src']

    def get_current_chapter_tag(self, soup):
        chapter_select = soup.find("select", attrs = {"name":"chapter_select"})
        current_chapter = chapter_select.find("option", selected="selected")
        return current_chapter

    def get_chapter_title(self, soup):
        ''' Get the current chapter's title.

        This implementation will try to remove 'v2' (or any vX) 
        which is usually used by scanlations to indicate an updated release.
        '''
        current_chapter_tag = self.get_current_chapter_tag(soup)
        chapter_title = current_chapter_tag.string
        chapter_title = re.sub(r'(.*\d+)(?:v|V)\d(.*)',r'\1\2', chapter_title)
        return chapter_title

    def get_next_page_url(self, soup):
        ''' Get the url of the next page. '''
        img = soup.find(id='comic_page')
        next_page_url = img.parent['href']
        return next_page_url

    def get_next_chapter_url(self, soup):
        ''' Get the url of next chapter.
        
        The url is calculated by getting the next page url of 
        current chapter's last page. There is no easy way to determine 
        which one is the next chapter from the chapter drop down 
        when there are more than one translations for one chapter.
        '''
        pages = soup.find(id='page_select')
        last_page = pages.find_all('option')[-1]
        last_page_soup = self.get_page_soup(last_page['value'])
        return self.get_next_page_url(last_page_soup)
