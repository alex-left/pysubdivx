from tempfile import NamedTemporaryFile, TemporaryDirectory
from patoolib import extract_archive
from pathlib import Path
import requests

from bs4 import BeautifulSoup
from .downloader import fetch_html

from urllib.parse import urlparse, parse_qs
try:
    import lxml
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

from .exceptions import SubtitleFailedDownload, SubtitleFailedExtraction
from .config import PROTO, DOMAIN

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
    VALID_EXTENSIONS = {
        "srt",
        "ssa",
        "ass",
        "sub",
        "usf",
        "ssf"
    }

    def __init__(self, data):
        """Init object.

        Parameters
        ----------
        data : dict
            dict with all attributes of the subtitle.

        """
        for k, v in data.items():
            setattr(self, k, v)
        self.download_link = None

    def get_subtitles(self):
        """Return a list with the data of all subtitles files

        Returns
        -------
        list 
          dict:
            "filename": str - name of the subtitile
            "extension": str - extension of the subititle, 
            "data": bytes - subtitle data

        """
        try:
            data = self._download()
            subtitle_files = self._uncompress(data)
        except SubtitleFailedDownload:
            print("Can't download the subtitle")
            raise
        except SubtitleFailedExtraction:
            raise

        return subtitle_files

    def _uncompress(self, data):
        temp_file = NamedTemporaryFile()
        temp_dir = TemporaryDirectory()
        with open(temp_file.name, "wb") as f:
            f.write(data)
        try:
            extract_archive(archive=temp_file.name, outdir=temp_dir.name)
        except Exception as e:
            raise (SubtitleFailedExtraction(e))
        finally:
            temp_file.close()
        temp_path = Path(temp_dir.name)
        subtitles_files = [file for file in temp_path.iterdir() if file.suffix.lower().replace(".", "") in self.VALID_EXTENSIONS]

        if not subtitles_files:
            raise SubtitleFailedExtraction("not found valid subtitle in downloaded file")   
        
        subs = [{
            "filename": sub.name, 
            "extension": sub.suffix, 
            "data": sub.read_bytes()} for sub in subtitles_files]
        
        temp_dir.cleanup()
        return subs

    def _get_download_link_v2(self):
        """parse uncommon link."""
        soup = BeautifulSoup(fetch_html(self.link), PARSER)
        lines = soup.find_all('a', {"class": "detalle_link"})
        d_link = None
        for line in lines:
            if line.get_text().lower() == "download":
                d_link = line.get("href")
        return d_link

    def _get_download_link_v1(self):
        """common way."""
        soup = BeautifulSoup(fetch_html(self.link), PARSER)
        lines = soup.find_all('a', {"class": "link1"})
        try:
            d_link = lines[0].get("href")
        except:
            d_link = None
        return d_link

    def _get_download_link(self):
        """gets a main link of a subtitle page and returns the download link."""
        d_link = self._get_download_link_v1()
        if not d_link:
            d_link = self._get_download_link_v2()
        if not d_link:
            raise("Not download link found")
        final_link = "{}{}/{}".format(PROTO, DOMAIN, d_link)
        return final_link

    def _download(self):
        """Download the file corresponding to the subtitle.

        Returns
        -------
        bytes
            bytes object or None

        """
        if not self.download_link:
            self.download_link = self._get_download_link()

        parsed_url = urlparse(self.download_link)
        parsed_params = parse_qs(parsed_url.query)
        download_link = "{}://{}/sub{}/{}".format(parsed_url.scheme, parsed_url.hostname, parsed_params["u"][0], parsed_params["id"][0])
        res = requests.get(download_link + ".zip")
        if res.status_code <= 400:
            return res.content
        res = requests.get(download_link + ".rar")
        if res.status_code <= 400:
            return res.content
        raise SubtitleFailedDownload()
