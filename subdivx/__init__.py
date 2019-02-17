import requests
from bs4 import BeautifulSoup
from collections import namedtuple
from time import sleep
from threading import Thread
import re

try:
    import lxml
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

__version__ = "0.1"
MAX_THREADS = 8
DOMAIN = "www.subdivx.com"
PROTO = "https://"
BASE_ENDPOINT = "{}{}/index.php".format(PROTO, DOMAIN)
HEADERS = {'user-agent': 'subsfinder/{}'.format(__version__)}
PARAMS = {'buscar': 'game+of+thrones+s01e01', 'accion': '5'}
DEBUG = False


class AsyncDownloader(Thread):
    def __init__(self, url, params):
        super().__init__()
        self.url = url
        self.params = params

    def run(self):
        self.result = fetch_html(self.url, self.params)

    def join(self):
        Thread.join(self)
        return self.result


def pages_downloader(pages):
    """Download multiple pages asynchronously.
    """


def search_by_name(search, params=PARAMS):
    params["buscar"] = '+'.join(search.split())
    parser = HtmlParser(fetch_html(BASE_ENDPOINT, params))
    results = Results()
    results.extend(parser.get_subtitles())
    pages = parser.get_pages()
    if pages:
        counter = 0
        threads_pool = []
        for page_number in range(2, pages + 1):
            params["pg"] = str(page_number)
            threads_pool.append(AsyncDownloader(BASE_ENDPOINT, params))
        for thread in threads_pool:
            if counter <= MAX_THREADS:
                thread.start()
                counter += 1
            else:
                sleep(1)
                thread.start()
                counter = 1

        htmls = [thread.join() for thread in threads_pool]
        for html in htmls:
            page_parser = HtmlParser(html)
            results.extend(page_parser.get_subtitles())
    return results


def fetch_html(url, params=None, headers=HEADERS, retries=3):
    """Function to get the html.

    Parameters
    ----------
    url : str
        String with complete url.
        Example: http://www.subdivx.com/index.php
    params : dict
        Params of the url, requests library compose the url using that.
        "Buscar" is the main field, haves the string to search.
        "Action" this should not change unless the engine of website change.
        Example:
            params = {
                "buscar": "game+of+thrones+s01e01",
                "accion": "5"
                }
    headers : dict
        Optional. A dict with headers of the request.

    Returns
    -------
    str
        String with all html code.

    """
    try:
        response = requests.get(url, params=params, headers=headers)
        if retries and 500 <= response.status_code < 600:
            sleep(1)
            return fetch_html(url, params, headers, retries - 1)
        else:
            return response.text
    except Exception as e:
        raise Exception("Something was wrong fetching data. {}".format(e))


class Subtitle:
    """Structure for all data of a single subtitle.

    Parameters
    ----------
    data : dict
        dict with all attributes

    Attributes
    ----------
    link : str
        url of the subtitle
    description : str
        Description of the subtitle
    downloads : int
        Amount fo downloads
    download_link : str
        Url to download the subtitle file

    """

    def __init__(self, data):
        self.link = data["link"]
        self.description = data["description"]
        self.downloads = data["downloads"]
        self.download_link = data["download_link"]
        self.score = 0
        # self.title = data["title"]

    def download_subtitle(self):
        data = requests.get()


class HtmlParser:
    # The data for a subtitle is split in two different sections.
    # Returned by _pair_sections() and used by get_subtitles()
    PairedSections = namedtuple("PairedSections", ["title", "data"])

    def __init__(self, html, parser=PARSER):
        self.soup = BeautifulSoup(html, parser)
        self.pages = 0

    def _pair_sections(self):
        # Pair the two sections of html for a single subtitle
        titles = self.soup.find_all('div', {"id": "menu_detalle_buscador"})
        datas = self.soup.find_all('div', {"id": "buscador_detalle"})
        return [self.PairedSections(title, data) for title, data in zip(titles, datas)]

    @staticmethod
    def _extract_downloads(strings):
        """Receives a iterable of html strings ,return int with number of downloads."""
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

    def process_pages(self):
        pass

    def get_pages(self):
        """Find the total result pages of a specific search."""
        if not self.pages:
            data = self.soup.find_all('div', {"class": "pagination"})[-1]
            urls = data.find_all("a")
            if urls:
                self.pages = int(urls[-2].contents[0])
        return self.pages

    def get_subtitles(self):
        subs_pairs = self._pair_sections()
        return [Subtitle({
            "link": sub.title.a.get("href"),
            "description": sub.data.div.get_text(),
            "download_link": sub.data.find("a", {"target": "new"}).get("href"),
            "downloads": self._extract_downloads(sub.data.strings)
        }) for sub in subs_pairs]


class Results(list):
    pass
