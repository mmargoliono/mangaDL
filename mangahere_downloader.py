import re
from basedownloader import BaseDownloader

class MangahereDownloader(BaseDownloader):
    ''' Downloader implementation that are targeted at mangahere.com '''

    def get_page_count(self, soup):
        ''' Get the number of pages in the chapter '''
        pages = soup.select('select.wid60')[0]
        page_count = len(pages.find_all('option'))
        return page_count

    def get_image_url(self, soup):
        ''' Get current page's image url '''
        img = soup.find(id = 'image')
        return img['src']

    def get_chapter_title(self, soup):
        ''' Get the current chapter's title.

        This implementation will try to remove 'v2' (or any vX)
        which is usually used by scanlations to indicate an updated release.
        '''
        js_location = re.search(r'http://www.mangahere.co/get_chapters\d+.js\?v=\d+', soup.getText()).group()
        self.js_content = str(self.get_page_content(js_location))
        self.js_chapter = re.search(r'var\s*current_chapter\s*=\s*"([^"]*)"', soup.getText()).group(1)
        chapter_regex = r'\["([^"]*)","http://www.mangahere.co/manga/"\+series_name\+"/' + self.js_chapter
        chapter_title = re.search(chapter_regex, self.js_content).group(1)
        chapter_title = chapter_title.replace("\\'","'")
        chapter_title = re.sub(r'(.*\d+)(?:v|V)\d(.*)',r'\1\2', chapter_title)
        return chapter_title

    def get_next_page_url(self, soup):
        ''' Get the url of the next page. '''
        img = soup.find(id='image')
        next_page_url = img.parent['href']
        if ("javascript" in next_page_url):
            series_name = re.search(r'var\s*series_name\s*=\s*"([^"]*)"', soup.getText()).group(1)
            next_url_regex = re.compile(r'"http://www.mangahere.co/manga/"\+series_name\+"/' + self.js_chapter + '/"][^\]]*' + 
                                         '"(http://www.mangahere.co/manga/"\+series_name\+"/[^"]*)"' , re.MULTILINE)
            next_page_url = next_url_regex.search(self.js_content).group(1)
            next_page_url = next_page_url.replace("\"+series_name+\"",series_name)
        return next_page_url

    def get_next_chapter_url(self, soup):
        ''' Get the url of next chapter.
        
        The url is calculated by getting the next page url of 
        current chapter's last page. There is no easy way to determine 
        which one is the next chapter from the chapter drop down 
        when there are more than one translations for one chapter.
        '''
        pages = soup.select('select.wid60')[0]
        last_page = pages.find_all('option')[-1]        
        last_page_soup = self.get_page_soup(last_page['value'])
        return self.get_next_page_url(last_page_soup)
