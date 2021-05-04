from .parser import HtmlParser
from .downloader import fetch_html
from .config import BASE_ENDPOINT, MAX_PAGES

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

        for page in range(MAX_PAGES):
            params["pg"] = str(page)
            parser = HtmlParser(fetch_html(BASE_ENDPOINT, params))
            temp_result = parser.get_subtitles()
            if not temp_result:
                break
            results.extend(temp_result)

        for sub in results:
            setattr(sub, "from_search", search)
        return results
