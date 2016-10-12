from __future__ import unicode_literals, print_function
import codecs
import inspect
import os
import re
import unicodedata
from unidecode import unidecode
from general_tools.file_utils import make_dir
import common

ref_split_re = re.compile(r'\.|:', re.UNICODE)
remove_re = re.compile(r'\r|\n|\[|\]|\.|,|:|\?|;', re.UNICODE)

nestle_books = ['Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col',
                '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet',
                '1John', '2John', '3John', 'Jude', 'Rev']


def book_from_ref(ref_book, book_list):
    global nestle_books

    book_idx = nestle_books.index(ref_book)
    return [nt_book for nt_book in book_list if nt_book['idx'] == book_idx + 41][0]


def load_existing_manuscripts(source_file_name):
    with codecs.open(source_file_name, 'r', 'utf-8-sig') as in_file2:
        temp_lines = in_file2.readlines()

    return_val = []
    for temp_line in temp_lines:
        temp_line = temp_line.strip()[1:-1]
        return_val.append(temp_line.split('","'))

    return return_val


def get_manuscript_verse(book_id, chapter_num, verse_num, manuscript_lines):

    found_lines = [l for l in manuscript_lines if l[1] == book_id and l[2] == chapter_num and l[3] == verse_num]
    return found_lines


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    n_left = unidecode(normalize_caseless(left))
    n_right = unidecode(normalize_caseless(right))

    # check for missing value
    if len(left) == 0 or len(n_left) == 0:
        return False

    # look for exact match
    if n_left == n_right:
        return True

    len_l = len(n_left)
    len_r = len(n_right)

    # if lengths are equal and you are here, the strings are NOT equal
    if len_l == len_r:
        return False

    # check for abbreviations
    if len(left) == 2:
        if n_left[0] == n_right[0] and n_left[-1] == n_right[-1]:
            return True

    if len_l > len_r and n_left[0:len_r] == n_right:
        return True

    if len_r > len_l and n_right[0:len_l] == n_left:
        return True

    if len_l > 2 and len_r > 2:
        return n_left[0:2] == n_right[0:2]

    return False


def get_index_of_word(start_idx, nestle_word):
    global manuscript_verse_data

    if not manuscript_verse_data:
        return start_idx

    for i in range(start_idx, len(manuscript_verse_data[0]) - 1):

        # loop through each of the manuscripts at this word index
        for verse_data in manuscript_verse_data:
            if caseless_equal(verse_data[i], nestle_word):
                return i

    # if you are here, the word was not found
    return None


if __name__ == '__main__':
    nt_books = common.get_versification()  # type: list<dict>
    this_dir = os.path.dirname(inspect.stack()[0][1])
    out_dir = os.path.join(this_dir, 'Nestle')
    make_dir(out_dir)
    source_dir = os.path.join(this_dir, 'Source')

    # load the existing manuscripts
    manuscripts = load_existing_manuscripts(os.path.join(this_dir, 'OutFiles', 'NewTestament.csv'))

    all_file_lines = ['"book_num","book_id","chapter","verse","manuscript","date","words"']

    with codecs.open(os.path.join(source_dir, 'nestle1904.txt'), 'r', 'utf-8-sig') as in_file:
        nestle_content = in_file.readlines()

    for line in nestle_content:

        line_parts = line.split('\t')
        ref_parts = ref_split_re.split(line_parts[0])
        book = book_from_ref(ref_parts[0], nt_books)

        ref_csv = '"{0}","{1}","{2}","{3}","Nestle","1904"'.format(book['idx'] - 40, book['id'],
                                                                   ref_parts[1], ref_parts[2])

        clean_text = remove_re.sub('', line_parts[1])
        words = clean_text.split(' ')  # type: list

        manuscript_verse_data = get_manuscript_verse(book['id'], ref_parts[1], ref_parts[2], manuscripts)

        # verse words start at index 6
        found_index = 5
        current_index = 6
        for idx in range(0, len(words)):

            found_index = get_index_of_word(found_index + 1, words[idx])

            # if the word is not in any of the manuscripts, exit the loop
            if found_index is None:
                ref_csv += ',"NOT ABLE"'
                break

            # insert any blank indexes
            while found_index > current_index + 1:
                ref_csv += ',""'
                current_index += 1

            ref_csv += ',"{0}"'.format(words[idx].strip())
            current_index = found_index

        ref_csv += ',"|"'
        all_file_lines.append(ref_csv)
        print(ref_csv)

    with codecs.open(os.path.join(out_dir, 'NewTestament.csv'), 'w', encoding='utf-8') as out_file:
        for file_line in all_file_lines:
            out_file.write(file_line + '\n')
