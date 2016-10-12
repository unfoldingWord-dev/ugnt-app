from __future__ import unicode_literals, print_function
import codecs
import inspect
import os
import re
from general_tools.file_utils import make_dir
from general_tools.url_utils import get_url
import common

body_re = re.compile(r'<body.*?>(.*)</body>', re.UNICODE | re.DOTALL)
verse_re = re.compile(r'<a name=\'\d{4}(\d{2})\'>.*?<table>(.*?)</table>', re.UNICODE | re.DOTALL)
tags_ai_re = re.compile(r'(?:<a.*?>|<i.*?>)(.*?)(?:</a.*?>|</i.*?>)', re.UNICODE)
spans_re = re.compile(r'</?span.*?>', re.UNICODE)
td_re = re.compile(r'(<td)(.*?)(>)', re.UNICODE)
values_re = re.compile(r'<td>(.*?)</td>', re.UNICODE)


if __name__ == '__main__':
    nt_books = common.get_versification()  # type: list<dict>
    this_dir = os.path.dirname(inspect.stack()[0][1])
    out_dir = os.path.join(this_dir, 'OutFiles')
    make_dir(out_dir)

    all_file_lines = ['"book_num","book_id","chapter","verse","manuscript","date","words"']

    for nt_book in nt_books:  # type: dict
        file_lines = ['"book_num","book_id","chapter","verse","manuscript","date","words"']
        book_id = nt_book['idx'] - 40
        book_id_str = str(book_id).zfill(2)
        url = 'http://greek-language.com/cntr/collation/{0}{1}.htm'

        for nt_chapter in nt_book['chapters']:
            print('Getting {0} {1}.'.format(nt_book['id'], nt_chapter[0]))
            page_raw = get_url(url.format(book_id_str, str(nt_chapter[0]).zfill(2)))

            # remove the header
            body = body_re.search(page_raw).group(1)
            for match in re.finditer(verse_re, body):
                verse_num = match.group(1)
                table_data = match.group(2)
                table_data = table_data.replace('<tr>', '').replace('\r', '')
                rows = table_data.split('\n')

                for row in rows:
                    row = row.strip()
                    if not row:
                        continue

                    row = tags_ai_re.sub(r'\1', row)
                    row = spans_re.sub(r'', row)
                    row = td_re.sub(r'\1\3', row)

                    vals = values_re.findall(row)
                    if len(vals) < 3:
                        continue

                    if len(vals[1]) == 4 and int(vals[1]) > 1920:
                        continue

                    out_csv = '"{0}","{1}","{2}","{3}"'.format(book_id, nt_book['id'], nt_chapter[0], int(verse_num))
                    for val in vals:
                        out_csv += ',"{0}"'.format(val)

                    # add end-of-row marker
                    out_csv += ',"|"'

                    file_lines.append(out_csv)
                    all_file_lines.append(out_csv)

        with codecs.open(os.path.join(out_dir, '{0}.csv'.format(nt_book['id'])), 'w', encoding='utf-8') as out_file:
            for file_line in file_lines:
                out_file.write(file_line + '\n')

    with codecs.open(os.path.join(out_dir, 'NewTestament.csv'), 'w', encoding='utf-8') as out_file:
        for file_line in all_file_lines:
            out_file.write(file_line + '\n')
