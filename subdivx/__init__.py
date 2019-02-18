import requests
import re
from bs4 import BeautifulSoup
from collections import namedtuple
from time import sleep
from concurrent.futures import ThreadPoolExecutor

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

def pages_async_downloader(pages, params):
    """Function to download asyncronously the rest of the pages of a subtitule search.
    Call fetch_html function to retrieve the html

    Parameters
    ----------
    pages : int
        Number of the total pages of a subtitle search. Obtained from get_pages method.
        The first page was downloaded by searcher, this download from 2th page to "pages"
    params : dict
        Params of the url, requests library compose the url using that.
        "Buscar" is the main field, haves the string to search.
        "Action" this should not change unless the engine of website change.
        Example:
            params = {
                "buscar": "game+of+thrones+s01e01",
                "accion": "5"
                }

    Returns
    -------
    list
        List with all html's from all pages.

    """
    executor = ThreadPoolExecutor(MAX_THREADS)
    threads_pool = []
    _params = params.copy()
    for page_number in range(2, pages + 1):
        _params["pg"] = str(page_number)
        threads_pool.append(executor.submit(fetch_html, BASE_ENDPOINT, _params))
    return [thread.result() for thread in threads_pool]


def search_by_name(search, params=PARAMS):
    """Function to search subtitle by name (string).

    Parameters
    ----------
    search : str
        String with text to search.
        Example: "game of thrones s01e01"
    params : dict
        Params of the url, requests library compose the url using that.
        "Buscar" is the main field, haves the string to search.
        "Action" this should not change unless the engine of website change.
        Example:
            params = {
                "buscar": "game+of+thrones+s01e01",
                "accion": "5"
                }

    Returns
    -------
    Results
        result object with all subtitles of the search.

    """
    params["buscar"] = '+'.join(search.split())
    parser = HtmlParser(fetch_html(BASE_ENDPOINT, params))
    results = Results()
    results.extend(parser.get_subtitles())
    pages = parser.get_pages()
    if pages:
        for html in pages_async_downloader(pages, params):
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
    """Structure for the data of a single subtitle.

    Attributes
    ----------
    title : str
        title of the subtitle
    link : str
        url of the subtitle
    description : str
        Description of the subtitle
    downloads : int
        Amount fo downloads
    download_link : str
        Url to download the subtitle file

    Methods
    -------
    download
        Download the file corresponding to the subtitle.

    """

    def __init__(self, data):
        """Init object.

        Parameters
        ----------
        data : dict
            dict with all attributes of the subtitle.

        """
        self.title = data["title"]
        self.description = data["description"]
        self.downloads = data["downloads"]
        self.link = data["link"]
        self.download_link = data["download_link"]

    def download(self):
        """Download the file corresponding to the subtitle.

        Returns
        -------
        bytes
            bytes object with content of subtitle file downloaded or None

        """
        res = requests.get(self.download_link)
        # Subdivx don't return 404 with wrong url. This check if url haves extensions to ensure that returns a file.
        file_pattern = r'\..{3}$'
        if res.status_code <= 400 and re.search(file_pattern, res.url):
            return res.content
        else:
            return None


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
        """Return a list with all subtitle objects of the html input"""
        subs_pairs = self._pair_sections()
        print(subs_pairs[0].title.text)
        return [Subtitle({
            "title": self.sub.text,
            "description": sub.data.div.get_text(),
            "downloads": self.get_downloads(sub.data.strings),
            "link": sub.title.a.get("href"),
            "download_link": sub.data.find("a", {"target": "new"}).get("href")
        }) for sub in subs_pairs]


class Results(list):
    pass
