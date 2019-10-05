import urllib.request

import re


def get_url_content(url, timeout=1):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        return resp.read().decode(errors="ignore")


def remove_tags(text):
    regular = re.compile('<.*?>')
    text = re.sub(regular, '', text)
    regular = re.compile('[\n\r\t]')
    text = re.sub(regular, '', text)
    text = ' '.join(text.split())
    return text


def get_text_from_url(url, timeout=1, tags=False):
    content = get_url_content(url, timeout)
    if not tags:
        return remove_tags(content)
    return content
