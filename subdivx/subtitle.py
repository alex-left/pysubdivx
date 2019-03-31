from tempfile import NamedTemporaryFile, TemporaryDirectory
from patoolib import extract_archive
from collections import namedtuple
from pathlib import Path
import requests
import re

from .exceptions import SubtitleFailedDownload, SubtitleFailedExtraction

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

    Subtitle_file = namedtuple("Subtitle_file", ["extension", "content"])

    def __init__(self, data):
        """Init object.

        Parameters
        ----------
        data : dict
            dict with all attributes of the subtitle.

        """
        for k, v in data.items():
            setattr(self, k, v)

    def get_subtitle(self):
        """Get bytes object with subtitle.

        Returns
        -------
        bytes
            bytes object or None

        """
        try:
            data = self._download()
            subtitle_file = self._uncompress(data)
        except SubtitleFailedDownload:
            print("Can't download the subtitile")
            raise
        except SubtitleFailedExtraction:
            raise

        return subtitle_file

    def _uncompress(self, data):
        temp_file = NamedTemporaryFile()
        temp_dir = TemporaryDirectory()
        with open(temp_file.name, "wb") as f:
            f.write(data)
        try:
            extract_archive(archive=temp_file.name, outdir=temp_dir.name)
        except Exception as e:
            raise (SubtitleFailedExtraction(e))
        path = Path(temp_dir.name)
        files = list(path.iterdir())
        try:
            result = next(file for file in files if file.suffix.lower() in self.VALID_EXTENSIONS)
        except Exception:
            raise SubtitleFailedExtraction("not found valid subtitle in downloaded file")
        return self.Subtitle_file(result.suffix, result.read_bytes())

    def _download(self):
        """Download the file corresponding to the subtitle.

        Returns
        -------
        bytes
            bytes object or None

        """
        res = requests.get(self.download_link)
        # Subdivx don't return 404 with wrong url. This check if url haves extensions to ensure that returns a file.
        file_pattern = r'\..{3}$'
        if res.status_code <= 400 and re.search(file_pattern, res.url):
            return res.content
        else:
            raise SubtitleFailedDownload()
