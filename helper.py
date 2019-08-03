from urllib.parse import urlparse

def getFaviconUri(url):
    parsed_uri = urlparse(url)
    result = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(uri=parsed_uri)
    print(result)
    return result
