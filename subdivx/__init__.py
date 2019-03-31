from .searcher import Searcher
from .config import __version__ as version
from .parser import HtmlParser
from .subtitle import Subtitle

searcher = Searcher()
search = searcher.search
