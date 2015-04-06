import unittest
from mangahere_downloader import MangahereDownloader

class MangahereDownloaderTest(unittest.TestCase):

    def setUp(self):
        self.downloader = MangahereDownloader("","")
        self.soup = self.downloader.get_page_soup("http://www.mangahere.co/manga/yamada_kun_to_7_nin_no_majo/c077/")

    def test_page_count(self):
        self.assertEqual(21, self.downloader.get_page_count(self.soup))

    def test_image_url(self):
        self.assertTrue(self.downloader.get_image_url(self.soup).startswith(
                        "http://a.mhcdn.net/store/manga/10642/077.0/compressed/"
                        "fyamada-kun_to_007-nin_no_majo_077_001.jpg"))

    def test_chapter_title(self):
        self.assertEqual("Ch 077: Filth!",
                         self.downloader.get_chapter_title(self.soup))

    def test_next_page_url(self):
        self.assertEqual("http://www.mangahere.co/manga/yamada_kun_to_7_nin_no_majo/c077/2.html",
                         self.downloader.get_next_page_url(self.soup))

    def test_next_chapter_url(self):
        self.assertEqual("http://www.mangahere.co/manga/yamada_kun_to_7_nin_no_majo/c078/",
                         self.downloader.get_next_chapter_url(self.soup))


if __name__ == '__main__':
    unittest.main()
