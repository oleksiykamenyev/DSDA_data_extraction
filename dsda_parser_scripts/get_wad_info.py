"""Gets WAD info for a single WAD on DSDA"""

import operator
import re

import dsda_parser_scripts.helper_functions.helper_functions as hf

__author__ = '4shockblast'


WAD_URL_TEMPLATE = 'http://doomedsda.us/wad{}.html'
OUTPUT_TEMPLATE = """filename: {filename}
author: {author}
compatibility: {compat}
iwad: {iwad}"""

# Static dictionary of wads on DSDA that are paginated mapping their filenames
# to the info needed in order to avoid iterating over all of their pages
# Not expected to change
PAGINATED_WAD_INFO = {
    'doom2': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'id Software'},
    'doom': {'compat': 'vanilla', 'iwad': 'doom', 'author': 'id Software'},
    'tnt': {'compat': 'vanilla', 'iwad': 'tnt', 'author': 'TeamTNT'},
    'plutonia': {'compat': 'vanilla', 'iwad': 'plutonia',
                 'author': 'Dario Casali & Milo Casali'},
    'hr': {'compat': 'vanilla', 'iwad': 'doom2',
           'author': 'Yonatan Donner & Haggay Niv'},
    'scythe': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'Erik Alm'},
    'mm': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'Various'},
    'av (2nd Release)': {'compat': 'vanilla', 'iwad': 'doom2',
                         'author': 'Various'},
    'mm2': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'Various'},
    'requiem': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'Various'}
}
# IWADs are handled separately
IWADS = {
    'doom': {'compat': 'vanilla', 'iwad': 'doom', 'author': 'id Software'},
    'doom2': {'compat': 'vanilla', 'iwad': 'doom2', 'author': 'id Software'},
    'doom2bfg': {'compat': 'vanilla', 'iwad': 'doom2',
                 'author': 'id Software'},
    'plutonia': {'compat': 'vanilla', 'iwad': 'plutonia',
                 'author': 'Dario Casali & Milo Casali'},
    'tnt': {'compat': 'vanilla', 'iwad': 'tnt', 'author': 'TeamTNT'},
    'chex': {'compat': 'vanilla', 'iwad': 'doom', 'author': 'Digital Café'},
    'hacx': {'compat': 'vanilla', 'iwad': 'hacx', 'author': 'Banjo Software'},
    'freedoom-0.9': {'compat': 'vanilla', 'iwad': 'freedoom/freedoom2',
                     'author': 'Various'},
    'freedoom-0.10.1': {'compat': 'vanilla', 'iwad': 'freedoom/freedoom2',
                        'author': 'Various'},
    'freedoom-0.11': {'compat': 'vanilla', 'iwad': 'freedoom/freedoom2',
                      'author': 'Various'}
}
# Hardcoded info because auto-IWAD guesser would get it wrong (are there any
# others?)
CHEX_WADS = {
    'chex2': {'compat': 'vanilla', 'iwad': 'doom', 'author': 'Digital Café'},
    'chexres': {'compat': 'limit-removing', 'iwad': 'doom',
                'author': 'joe-ilya'}
}

# Regexes matching executables used by players on DSDA mapped
# to their respective compatibilities
EXECUTABLE_REGEXES = {
    # Original Boom port versions
    re.compile(r'^Boom.*$'): 'Boom',

    # Initially a modified doom2.exe, eventually based on MBF with extra
    # features. Currently only recordings by port author for vanilla
    # mapsets.
    re.compile(r'^CDooM.*$'): 'limit-removing',

    # Designed to emulate vanilla Doom as closely as possible, mapped to
    # limit-removing to be safe
    re.compile(r'^Chocolate DooM.*$'): 'limit-removing',

    # Modified Chocolate with extra speedrun-oriented features, only
    # vanilla compatible demos supported
    re.compile(r'^CNDoom.*$'): 'limit-removing',

    # Modified Chocolate with limits removed
    re.compile(r'^Crispy Doom.*$'): 'limit-removing',

    # Vanilla Doom, Doom 2, or Final Doom exes all map to limit-removing
    # to be safe
    re.compile(r'^DooM2? v1.\d+\.?\d*f?$'): 'limit-removing',

    # Doom 95 exes map to limit-removing to be safe
    re.compile(r'^DooM2? v95f?$'): 'limit-removing',

    # Doom 64 port to PC, maps to its own compatibility
    re.compile(r'^Doom64 EX.*$'): 'Doom 64',

    # Advanced source port, features mostly limited to hi-res textures and
    # fancy effects, but still does not correspond easily to any
    # obvious compatibility
    re.compile(r'^Doomsday.*$'): 'Unknown',

    # Earliest source port, mostly equivalent to vanilla
    re.compile(r'^DosDooM.*$'): 'limit-removing',

    # Version of DosDoom designed for TAS, also should be mostly equivalent
    # to vanilla
    re.compile(r'^TasDooM.*$'): 'limit-removing',

    # Advanced source port, impossible to map to anything, as its features
    # are in between PrBoom and (G)ZDoom
    re.compile(r'^Eternity.*$'): 'Unknown',

    # Advanced source port
    re.compile(r'^GZDoom.*$'): 'GZDoom',

    # Initially very similar to DOSDoom, later added many advanced features
    re.compile(r'^Legacy.*$'): 'Unknown',

    # Modified version of (G)ZDoom with some extra features and difficulty
    # settings, maps to GZDoom compatibility I guess
    re.compile(r'^ManDoom.*$'): 'GZDoom',

    # Modified Boom with extra features, maps to MBF compatibility
    re.compile(r'^MBF.*$'): 'MBF',

    # Version of MBF supporting TAS, it doesn't look like any demos are
    # marked with this even though there are MBF TAS demos on DSDA
    re.compile(r'^TASMBF.*$'): 'MBF',

    # Encompasses both the original PrBoom and PrBoom+, if a compatiblity
    # level is specified, then that gives the wad compat mapping, otherwise
    # doesn't map to anything
    re.compile(r'^PRBoom.*$'): 'PrBoom',

    # Modified version of Chocolate with some limits removed
    re.compile(r'^Strawberry DooM.*$'): 'limit-removing',

    # Old multiplayer port of ZDoom, with limited exceptions commonly
    # used for rocket jump maps, so it maps to its own compatibility,
    # some exceptions are that recordings for ZDoom maps and
    # co-op demos that are not too common
    re.compile(r'^ZDaemon.*$'): 'ZDaemon',

    # Advanced source port, maps to GZDoom compatibility as there
    # is no clear distinction that can be made between the
    # two based on the version of (G)ZDoom used
    re.compile(r'^ZDoom.*$'): 'GZDoom'
}
D1_MAP_NUMBER_REGEX = re.compile(r'^E[0-9]M[0-9][0-9]?$')
D1_EPISODE_REGEX = re.compile(r'^D[0-9]EP[0-9]$')


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


def get_demo_rows_for_wad_url(wad_url):
    """Gets demo rows for a wad URL"""
    tree = hf.get_web_page_html(wad_url)
    # Demos for wads on DSDA are placed in a table, and there are at
    # most two tables on a particular page (demo and page navigation
    # tables), so the first one is needed to parse the demos
    tables = tree.xpath('//table')
    # All demo rows on DSDA have these classes
    rows = tables[0].xpath('.//tr[@class="row1" or @class="row2" or'
                           ' @class="row1top" or @class="row2top"]')
    return rows


def guess_compat_by_wad_url(wad_url):
    """Guesses compat for a wad URL

    This guess is performed according to the most used source
    port. Each source port is mapped to a particular compatibility,
    and the compatibility mapping for the most used source port
    is used as the guess for the wad.

    In case a source port cannot be mapped to a clear compatibility,
    it is marked as Unknown except in the case of generic PrBoom being
    used. Because many demos on DSDA use PrBoom as a source port
    but do not specify the compatibility used, the count from those
    demos is added to the most used compatibility that is supported
    by PrBoom+. If there are no other compatibilities in the list
    supported by PrBoom+, those entries are converted to Unknown.

    The script will output any ports that were entirely unrecognized.
    This can happen if there is a mistake on any existing source
    port field on DSDA or a new source port is added to DSDA.
    """
    compatibility_counts = {}
    known_unmapped_ports = {}
    unrecognized_ports = {}
    rows = get_demo_rows_for_wad_url(wad_url)
    for row in rows[1:]:
        if len(row) > 2:
            port = row[-2].text
            port_matched = False
            for port_regex in EXECUTABLE_REGEXES:
                if re.match(port_regex, port):
                    current_compat = EXECUTABLE_REGEXES[port_regex]
                    if EXECUTABLE_REGEXES[port_regex] != 'PrBoom':
                        if current_compat in compatibility_counts:
                            compatibility_counts[current_compat] += 1
                        else:
                            compatibility_counts[current_compat] = 1
                        if current_compat == 'Unknown':
                            if port in known_unmapped_ports:
                                known_unmapped_ports[port] += 1
                            else:
                                known_unmapped_ports[port] = 1
                    else:
                        port_split = port.split('cl')
                        if len(port_split) > 1:
                            compatibility_guess = guess_prboom_compat(port_split)
                            if compatibility_guess == 'PrBoom':
                                if port in known_unmapped_ports:
                                    known_unmapped_ports[port] += 1
                                else:
                                    known_unmapped_ports[port] = 1

                            if compatibility_guess in compatibility_counts:
                                compatibility_counts[compatibility_guess] += 1
                            else:
                                compatibility_counts[compatibility_guess] = 1
                        else:
                            if 'PrBoom' in compatibility_counts:
                                compatibility_counts['PrBoom'] += 1
                            else:
                                compatibility_counts['PrBoom'] = 1
                            if port in known_unmapped_ports:
                                known_unmapped_ports[port] += 1
                            else:
                                known_unmapped_ports[port] = 1
                    port_matched = True
            if not port_matched:
                if port in unrecognized_ports:
                    unrecognized_ports[port] += 1
                else:
                    unrecognized_ports[port] = 1

    if unrecognized_ports:
        print('Unrecognized ports for WAD URL: {}'.format(wad_url))
        print(unrecognized_ports)

    if 'PrBoom' in compatibility_counts:
        compats_sorted = sorted(compatibility_counts.items(),
                                key=operator.itemgetter(1),
                                reverse=True)
        pushed_down = False
        for compat in compats_sorted:
            # Compatibilities supported by PrBoom
            if (compat[0] == 'limit-removing' or
                        compat[0] == 'Boom' or
                        compat[0] == 'MBF'):
                compatibility_counts[compat[0]] += compatibility_counts['PrBoom']
                pushed_down = True
                break
        if not pushed_down:
            if 'Unknown' in compatibility_counts:
                compatibility_counts['Unknown'] += compatibility_counts['PrBoom']
            else:
                compatibility_counts['Unknown'] = compatibility_counts['PrBoom']

        compatibility_counts.pop('PrBoom')

    if compatibility_counts.items():
        max_compat = max(compatibility_counts.items(), key=operator.itemgetter(1))
    else:
        # This will only be executed if a wad has no demos on DSDA
        # presumably that can happen if all demos were removed on
        # request for a particular wad
        print('Error: no compats for wad URL: {}'.format(wad_url))
        max_compat = ['Unknown']
    return max_compat


def guess_prboom_compat(port_split):
    """Guesses engine compatibility based on PrBoom+ complevel"""
    # PrBoom entries with complevels use the
    # complevel for guessing the compat
    complevel = int(port_split[1])
    # Lower complevels correspond to
    # limit-removing/vanilla
    if 0 <= complevel <= 6:
        compatibility_guess = 'limit-removing'
    # Boom/LxDoom complevels
    elif 7 <= complevel <= 10:
        compatibility_guess = 'Boom'
    elif complevel == 11:
        compatibility_guess = 'MBF'
    # All higher complevels and -1 correspond
    # to versions of PrBoom/PrBoom+
    else:
        compatibility_guess = 'PrBoom'
    return compatibility_guess


def guess_iwad_by_wad_url(wad_url):
    """Guesses IWAD for a wad URL

    This guess is performed according to whether the majority of the map
    numbers match one of the following formats:
        E#M#
        D1EP#
        D1ALL

    Anything with MAP##, D2EP#, or D2ALL is ignored because it could be one
    of several IWADs.
    """
    doom1_map_counts = 0
    other_map_counts = 0
    tree = hf.get_web_page_html(wad_url)
    # Demos for wads on DSDA are placed in a table, and there are at
    # most two tables on a particular page (demo and page navigation
    # tables), so the first one is needed to parse the demos
    tables = tree.xpath('//table')
    # All demo rows on DSDA have these classes
    rows = tables[0].xpath('.//tr[@class="row1top" or @class="row2top"]')
    for row in rows:
        map_number = row[0].text_content()
        if (re.match(D1_MAP_NUMBER_REGEX, map_number) or
                re.match(D1_EPISODE_REGEX, map_number) or
                map_number == 'D1ALL'):
            doom1_map_counts += 1
        else:
            other_map_counts += 1

    if doom1_map_counts > other_map_counts:
        return 'doom'
    else:
        return 'unknown'


def get_wad_info(wad_id):
    wad_url = WAD_URL_TEMPLATE.format(wad_id)
    tree = hf.get_web_page_html(wad_url)
    # Wad title on DSDA has no class or id, but always is a th
    # element and always uses colspan="5"
    title_elem = tree.xpath('//th[@colspan="5"]')
    if title_elem is None or len(title_elem) == 0:
        print('Invalid ID.')
        return None

    wad_filename = title_elem[0][0].text_content()
    if wad_filename in IWADS:
        print(OUTPUT_TEMPLATE.format(
            filename=wad_filename,
            author=IWADS[wad_filename]['author'],
            compat=IWADS[wad_filename]['compat'],
            iwad = IWADS[wad_filename]['iwad']
        ))
        return None
    if wad_filename in PAGINATED_WAD_INFO:
        print(OUTPUT_TEMPLATE.format(
            filename=wad_filename,
            author=PAGINATED_WAD_INFO[wad_filename]['author'],
            compat=PAGINATED_WAD_INFO[wad_filename]['compat'],
            iwad = PAGINATED_WAD_INFO[wad_filename]['iwad']
        ))
        return None

    wad_author = title_elem[0][2].text_content()
    guessed_compat = guess_compat_by_wad_url(wad_url)
    guessed_iwad = guess_iwad_by_wad_url(wad_url)
    print(OUTPUT_TEMPLATE.format(
        filename=wad_filename,
        author=wad_author,
        compat=guessed_compat,
        iwad=guessed_iwad
    ))
    return None


def main():
    """Main function"""
    get_wad_info('2')


if (__name__ == '__main__' or
        __name__ == 'dsda_command_line__main__'):
    main()
