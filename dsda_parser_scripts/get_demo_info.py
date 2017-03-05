"""Gets demo info for all demos for a single WAD on DSDA"""

import operator
import re

import dsda_parser_scripts.helper_functions.helper_functions as hf

__author__ = '4shockblast'


WAD_URL_TEMPLATE = 'http://doomedsda.us/wad{}.html'
OUTPUT_TEMPLATE = """filename: {filename}
wad: {wad}
level: {level}
time: {time}
category: {category}
engine: {engine}
players: {players}
is_tas: {is_tas}
is_pack: {is_pack}
comment: {comment}"""

# Static list of wads on DSDA that are paginated, not expected
# to change
PAGINATED_WADS = [
    'doom2',
    'doom',
    'tnt',
    'plutonia',
    'hr',
    'scythe',
    'mm',
    'av (2nd Release)',
    'mm2',
    'requiem'
]


def get_demo_rows_for_wad_url(wad_url):
    """Gets demo rows for a wad URL"""
    tree = hf.get_web_page_html(wad_url)
    # Demos for wads on DSDA are placed in a table, and there are at
    # most two tables on a particular page (demo and page navigation
    # tables), so the first one is needed to parse the demos
    for br in tree.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    tables = tree.xpath('//table')
    # All demo rows on DSDA have these classes
    rows = tables[0].xpath('.//tr[@class="row1" or @class="row2" or'
                           ' @class="row1top" or @class="row2top"]')
    return rows


def get_wad_urls_for_paginated_wad(wad_url):
    """Gets all wad URLs fo a paginated wad"""
    # Current URL will always be the first page of a paginated wad
    wad_urls = [wad_url]
    tree = hf.get_web_page_html(wad_url)
    # Gets the second table on a page, which will always exist for
    # paginated wads as the first is the demo table and the second is
    # the navigation table
    tables = tree.xpath('//table')
    rows = tables[1].xpath('.//tr[@class="row1" or @class="row2"]')
    for row in rows:
        for col in row:
            # Sometimes columns in the table will be blank for padding
            if len(col):
                page_url = col[0].get('href')
                wad_urls.append('http://doomedsda.us/{}'.format(page_url))
    return wad_urls


def get_demo_info(demo_id):
    wad_url = WAD_URL_TEMPLATE.format(demo_id)
    tree = hf.get_web_page_html(wad_url)
    # Wad title on DSDA has no class or id, but always is a th
    # element and always uses colspan="5"
    title_elem = tree.xpath('//th[@colspan="5"]')
    if title_elem is None or len(title_elem) == 0:
        print('Invalid ID.')
        return None

    wad_filename = title_elem[0][0].text_content()
    if wad_filename in PAGINATED_WADS:
        wad_urls = get_wad_urls_for_paginated_wad(wad_url)
    else:
        wad_urls = [wad_url]

    demos = []
    for wad_url in wad_urls:
        rows = get_demo_rows_for_wad_url(wad_url)
        cur_map = None
        cur_category = None
        for row in rows[1:]:
            if len(row) > 2:
                is_pack = False
                demo_link = row[-1][0].get('href')
                if demo_link.startswith('col'):
                    is_pack = True
                    demo_pack_tree = hf.get_web_page_html(
                        'http://doomedsda.us/{}'.format(demo_link)
                    )
                    # Demo pack title on DSDA has no class or id, but always
                    # is a th element and always uses colspan="6"
                    demo_pack_title_elem = demo_pack_tree.xpath(
                        '//th[@colspan="6"]'
                    )
                    if (demo_pack_title_elem is None or
                            len(demo_pack_title_elem) == 0):
                        print('Invalid demo pack ID.')
                        demo_file_name = None
                    else:
                        demo_file_name = demo_pack_title_elem[0][0].text_content()
                else:
                    demo_file_name = demo_link

                if len(row) > 3:
                    cur_category = row[0].text
                if len(row) > 4:
                    cur_map = row[0].text
                    cur_category = row[1].text
                engine = row[-2].text
                players = row[-3].text
                time_text = row[-1].text_content()
                is_tas = False
                if 'TAS' in time_text:
                    is_tas = True
                time = time_text.split()[0]
                cur_demo_info = {
                    'filename': demo_file_name,
                    'wad': wad_filename,
                    'level': cur_map,
                    'time': time,
                    'category': cur_category,
                    'engine': engine,
                    'players': players,
                    'is_tas': is_tas,
                    'is_pack': is_pack
                }
                demos.append(cur_demo_info)
            else:
                comment = row[0].text_content()
                last_demo = demos.pop()
                last_demo['comment'] = comment
                demos.append(last_demo)

    return demos


def main():
    """Main function"""
    demo_info = get_demo_info('2391')
    for demo in demo_info:
        print(OUTPUT_TEMPLATE.format(
            filename=demo['filename'],
            wad=demo['wad'],
            level=demo['level'],
            time=demo['time'],
            category=demo['category'],
            engine=demo['engine'],
            players=demo['players'],
            is_tas=demo['is_tas'],
            is_pack=demo['is_pack'],
            comment=demo.get('comment')
        ))
        print()


if (__name__ == '__main__' or
        __name__ == 'get_demo_info__main__'):
    main()
