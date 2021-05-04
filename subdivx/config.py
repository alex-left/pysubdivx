__version__ = "0.3"
MAX_THREADS = 16
DOMAIN = "www.subdivx.com"
PROTO = "https://"
BASE_ENDPOINT = "{}{}/index.php".format(PROTO, DOMAIN)
HEADERS = {'user-agent': 'subsfinder/{}'.format(__version__)}
DEBUG = False
MAX_PAGES = 30
