from pathlib import Path
from io import BytesIO
import mimetypes
import re
import tempfile
import requests
from bs4 import BeautifulSoup

from .extractors import extract_text_from_file

PDF_CT = {"application/pdf"}

def _filename_from_headers(url: str, resp: requests.Response) -> str:
    cd = resp.headers.get("content-disposition", "")
    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^\";]+)', cd, re.I)
    if m:
        return m.group(1)
    return Path(url).name or "downloaded"


def _extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def fetch_and_extract(url: str) -> tuple[str, str]:
    
    with requests.get(url, stream=True, timeout=20) as r:
        r.raise_for_status()
        ct = r.headers.get("content-type", "").split(";")[0].lower().strip()
        filename = _filename_from_headers(url, r)

        if ct in PDF_CT or filename.lower().endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in r.iter_content(chunk_size=65536):
                    tmp.write(chunk)
                tmp_path = Path(tmp.name)
            text = extract_text_from_file(tmp_path)
            return filename, text

        html = r.text
        text = _extract_html_text(html)
        return filename or "webpage", text
