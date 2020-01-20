from collections import namedtuple
from bs4 import BeautifulSoup
from .subtitle import Subtitle
import re
try:
    import lxml
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"


class HtmlParser:
    # The data for a subtitle is split in two different sections.
    # Returned by _pair_sections() and used by get_subtitles()

    def __init__(self, html, parser=PARSER):
        self.soup = BeautifulSoup(html, parser)
        self.pages = 0

    _PairedSections = namedtuple("PairedSections", ["title", "data"])

    def _pair_sections(self):
        # Pair the two sections of html for a single subtitle
        titles = self.soup.find_all('div', {"id": "menu_detalle_buscador"})
        datas = self.soup.find_all('div', {"id": "buscador_detalle"})
        return [self._PairedSections(title, data) for title, data in zip(titles, datas)]

    @staticmethod
    def get_downloads(strings):
        """Receives a iterable of html strings, return int with number of downloads."""
        downloads = 0
        all_strings = list(strings)
        for index, line in enumerate(all_strings):
            if "downloads" in line.lower():
                downloads = all_strings[index + 1]
                break
        if downloads:
            try:
                return int(re.sub(r'[^\d]', "", downloads, re.UNICODE))
            except Exception:
                pass
        return downloads

    def get_pages(self):
        """Find the total result pages of a specific search."""
        if not self.pages:
            data = self.soup.find_all('div', {"class": "pagination"})[-1]
            urls = data.find_all("a")
            if urls:
                self.pages = int(urls[-2].contents[0])
        return self.pages

    def get_subtitles(self):
        """Return a list with all subtitle objects of the html input."""
        subs_pairs = self._pair_sections()
        return [Subtitle({
            "title": sub.title.text,
            "description": sub.data.div.get_text(),
            "downloads": self.get_downloads(sub.data.strings),
            "link": sub.title.a.get("href"),
        }) for sub in subs_pairs]
