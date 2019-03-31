from .parser import HtmlParser
from .downloader import fetch_html, pages_async_downloader
from .config import BASE_ENDPOINT

class Searcher:
    PARAMS = {'buscar': None, 'accion': '5'}

    def search(self, search, params=None):
        """Search subtitle by name (string).

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
        if params is None:
            params = Searcher.PARAMS
        try:
            params["buscar"] = '+'.join(search.split())
        except Exception:
            raise
        parser = HtmlParser(fetch_html(BASE_ENDPOINT, params))
        results = []
        results.extend(parser.get_subtitles())
        pages = parser.get_pages()
        if pages:
            for html in pages_async_downloader(pages, params):
                page_parser = HtmlParser(html)
                results.extend(page_parser.get_subtitles())
        for sub in results:
            setattr(sub, "search", search)
        return results
