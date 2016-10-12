from __future__ import unicode_literals
import json
from general_tools.url_utils import get_url


def get_versification():
    """
    Get the versification file and parse it into book, chapter and verse information
    :return: list<Book>
    """

    api_root = 'https://raw.githubusercontent.com/unfoldingWord-dev/uw-api/develop/static'
    vrs_file = api_root + '/versification/{0}/{0}.vrs'
    book_file = api_root + '/versification/{0}/books.json'

    # get the list of books
    books = json.loads(get_url(book_file.format('ufw')))

    # get the versification file
    raw = get_url(vrs_file.format('ufw'))
    lines = [l for l in raw.replace('\r', '').split('\n') if l and l[0:1] != '#']

    scheme = []
    for key, value in iter(books.items()):

        if int(value[1]) < 41:
            continue

        book = {'id': key, 'name': value[0], 'idx': int(value[1]), 'chapters': []}

        # find the key in the lines
        for line in lines:
            if line[0:3] == key:
                chapters = line[4:].split()
                for chapter in chapters:
                    parts = chapter.split(':')
                    book_chapter = (int(parts[0]), int(parts[1]))
                    book['chapters'].append(book_chapter)
                scheme.append(book)
                break

    return scheme
