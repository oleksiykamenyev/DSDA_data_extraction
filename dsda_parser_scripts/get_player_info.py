"""Gets WAD info for a single WAD on DSDA"""

import operator
import re

import dsda_parser_scripts.helper_functions.helper_functions as hf

__author__ = '4shockblast'


PLAYER_URL_TEMPLATE = 'http://doomedsda.us/player{}.html'
PLAYER_LMPS_URL_TEMPLATE = 'http://doomedsda.us/player{}lmps.html'
OUTPUT_TEMPLATE = """name: {player_name}
profile_text: {profile_text}"""


def get_player_info(player_id):
    player_lmps_url = PLAYER_LMPS_URL_TEMPLATE.format(player_id)
    tree = hf.get_web_page_html(player_lmps_url)
    # Player name on DSDA has no class or id, but always is a th
    # element and always uses colspan="6"
    title_elem = tree.xpath('//th[@colspan="6"]')
    if title_elem is None or len(title_elem) == 0:
        print('Invalid ID.')
        return None

    if title_elem[0][0].tag == 'a':
        player_name = title_elem[0][0].text_content()
    else:
        player_name = title_elem[0].text

    player_url = PLAYER_URL_TEMPLATE.format(player_id)
    tree = hf.get_web_page_html(player_url)
    # Profile text on DSDA is always a div element and has class="textbox"
    profile_elem = tree.xpath('//div[@class="textbox"]')
    print(profile_elem)
    player_profile_text = ''
    if profile_elem is not None and len(profile_elem) > 0:
        for elem in profile_elem:
            player_profile_text += elem.text_content() + '\n'

    print(OUTPUT_TEMPLATE.format(
        player_name=player_name,
        profile_text=player_profile_text
    ))

    return None


def main():
    """Main function"""
    get_player_info('322')


if (__name__ == '__main__' or
        __name__ == 'get_player_info__main__'):
    main()
