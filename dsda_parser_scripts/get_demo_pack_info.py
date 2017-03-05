"""Gets demo info for all demos for a single WAD on DSDA"""

import operator
import re

import dsda_parser_scripts.helper_functions.helper_functions as hf

__author__ = '4shockblast'


DEMO_PACK_URL_TEMPLATE = 'http://doomedsda.us/col{}.html'
OUTPUT_TEMPLATE = """filename: {filename}"""


def get_demo_pack_info(demo_pack_id):
    demo_pack_url = DEMO_PACK_URL_TEMPLATE.format(demo_pack_id)
    demo_pack_tree = hf.get_web_page_html(demo_pack_url)
    # Demo pack title on DSDA has no class or id, but always
    # is a th element and always uses colspan="6"
    demo_pack_title_elem = demo_pack_tree.xpath('//th[@colspan="6"]')
    if (demo_pack_title_elem is None or
            len(demo_pack_title_elem) == 0):
        print('Invalid demo pack ID.')
        demo_pack_file_name = None
    else:
        demo_pack_file_name = demo_pack_title_elem[0][0].text_content()

    print(OUTPUT_TEMPLATE.format(filename=demo_pack_file_name))


def main():
    """Main function"""
    get_demo_pack_info('425')


if (__name__ == '__main__' or
        __name__ == 'get_demo_pack_info__main__'):
    main()
