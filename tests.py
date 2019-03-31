import unittest
import subdivx
from pathlib import Path


class FunctionalMockedParserTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        data = Path("subdivx/tests/terror.4pages.html").read_text()
        self.parser = subdivx.HtmlParser(data)
        # self.search_results = subdivx.search_by_name("the terror")
        super().__init__(*args, **kwargs)

    def test_get_pages(self):
        self.assertGreaterEqual(4, self.parser.get_pages())

    def test_get_subtitles(self):
        self.results = self.parser.get_subtitles()
        self.assertGreaterEqual(20, len(self.results))
        description = 'the terror (1963)  v3ndetta - avi 922 05 mb - 29 971 fps - duración 01:18:33 - subtítulo de pantheon (crédito y agradecimiento a él), sincronizado por mí para esta versión que se baja por  '
        link = 'http://www.subdivx.com/X6XMzQyOTkwX-the-terror-1963.html'
        title = 'Subtitulo de The Terror (1963)'
        self.assertEqual(title, self.results[10].title)
        self.assertEqual(link, self.results[10].link)
        self.assertEqual(description, self.results[10].description)
        self.assertEqual(331, self.results[10].downloads)

    def test_get_subtitles_types(self):
        self.results = self.parser.get_subtitles()
        str_attributes = [
            "description",
            "title",
            "link"
        ]
        for sub in self.results:
            self.assertIsInstance(getattr(sub, "downloads"), int)
            for attr in str_attributes:
                self.assertTrue(getattr(sub, attr))
                self.assertIsInstance(getattr(sub, attr), str)


if __name__ == "__main__":
    unittest.main()
