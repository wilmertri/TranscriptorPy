from urllib.parse import urlparse

_HOSTS_PERMITIDOS = {"youtube.com", "youtu.be"}


def es_url_youtube(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host in _HOSTS_PERMITIDOS
