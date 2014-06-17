import unittest
from batotodownloader import BatotoDownloader

class TestDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = BatotoDownloader("","")
        self.soup = self.downloader.get_page_soup("http://www.batoto.net/read/_/1496/iris-zero_v1_ch2_by_ala-atra-scans")

    def test_omake_number(self):
        self.assertEqual(5, self.downloader.get_omake_number("Vol.9 Ch.87.5"))
        self.assertEqual(5, self.downloader.get_omake_number("Vol.4 Ch.20.5: Omake"))
        self.assertEqual(6, self.downloader.get_omake_number("Vol.10 Ch.96.6: Special Omake - Anime Anguish Monologue"))
        
    def test_page_count(self):
        self.assertEqual(31, self.downloader.get_page_count(self.soup))

    def test_image_url(self):
        self.assertEqual("http://arc.batoto.net/comics/i/iris-zero/02/ala-atra/English/" + \
                         "read4d79b43745b62/%5BAAS_SS%5D%20Iris%20Zero" + \
                         "%20v01%20ch02_Iris-credits4d79b43772e5a.jpg", 
                         self.downloader.get_image_url(self.soup))

    def test_chapter_title(self):
        self.assertEqual("Vol.1 Ch.2: Episode 2 - The Thing Called Destiny",
                         self.downloader.get_chapter_title(self.soup))

    def test_next_page_url(self):
        self.assertEqual("http://www.batoto.net/read/_/1496/iris-zero_v1_ch2_by_ala-atra-scans/2",
                         self.downloader.get_next_page_url(self.soup))

    def test_next_chapter_url(self):
        self.assertEqual("http://www.batoto.net/read/_/703/iris-zero_v1_ch3_by_ala-atra-scans",
                         self.downloader.get_next_chapter_url(self.soup))


if __name__ == '__main__':
    unittest.main()
