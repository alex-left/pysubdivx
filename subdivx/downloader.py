from concurrent.futures import ThreadPoolExecutor
from time import sleep
import requests

from .config import HEADERS, MAX_THREADS, BASE_ENDPOINT

def fetch_html(url, params=None, headers=HEADERS, retries=3):
    """Get the html.

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



def pages_async_downloader(pages, params):
    """Download asyncronously the rest of the pages of a subtitule search.
    Call fetch_html function to retrieve the html

    Parameters
    ----------
    pages : int
        Number of the total pages of a subtitle search. Obtained from get_pages method.
        The first page was downloaded by searcher, this download from 2th page to "pages"
    params : dict
        Params of the url, requests library compose the url using that.
        "Buscar" is the main field, haves the string to search.
        "Action" this should not change unless the engine of website changes.
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
