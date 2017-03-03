"""Gets port info from DSDA

Pulls port info from main page and can pull port info from all wads for
cross-comparison.
"""

import operator
import re

from collections import defaultdict

import dsda_parser_scripts.helper_functions.helper_functions as hf

__author__ = '4shockblast'


MAIN_PAGE = 'http://doomedsda.us/index.html'
WAD_URL_TEMPLATE = 'http://doomedsda.us/wad{}.html'
OUTPUT_TEMPLATE = """family: {family}
version: {version}"""

HARDCODED_PORT_INFO = {
    'MBF': ['v2.03'],
    'TASDoom': [''],
    'TASMBF': ['']
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
VERSIONED_PORT_RE = re.compile(r'^.*((r\d+)|(v\d\.?(\d\.)*)).*$')
VERSION_RE = re.compile(r'^.*((r\d+)|(v\d\.?(\d\.)*)).*$')
SOURCE_PORTS_RE = re.compile(r'^\s*source\s*ports\s*$', re.IGNORECASE)


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


def get_ports_for_wad_url(wad_url):
    """Gets ports for wad URL list"""
    ports = defaultdict(list)
    rows = get_demo_rows_for_wad_url(wad_url)
    for row in rows[1:]:
        if len(row) > 2:
            port = row[-2].text
            if re.match(VERSIONED_PORT_RE, port):
                port_split = port.rsplit(' ', 1)
                port_family = port_split[0]
                if len(port_split) > 1:
                    if port_family == 'PRBoom':
                        port_version = port_split[1].split('cl')[0]
                    else:
                        port_version = port_split[1]
                    if port_family in ports:
                        if port_version not in ports[port_family]:
                            ports[port_family].append(port_version)
                    else:
                        ports[port_family].append(port_version)
                else:
                    port_version = ''
                    if port_family in ports:
                        if port_version not in ports[port_family]:
                            ports[port_family].append(port_version)
                    else:
                        ports[port_family].append(port_version)
            else:
                port_sanitized = port.strip()
                port_version = ''
                if port_sanitized in ports:
                    if port_version not in ports[port_sanitized]:
                        ports[port_sanitized].append(port_version)
                else:
                    ports[port_sanitized].append(port_version)

    return ports


def get_wad_port_info(wad_id):
    return get_ports_for_wad_url(WAD_URL_TEMPLATE.format(wad_id))


def get_main_port_info():
    tree = hf.get_web_page_html(MAIN_PAGE)
    info_lists = tree.xpath('//li')
    source_ports_elem = None
    for info_list in info_lists:
        if len(info_list):
            if re.match(SOURCE_PORTS_RE, info_list[0].text_content()):
                source_ports_elem = info_list
    if source_ports_elem is None or not len(source_ports_elem):
        return None

    ports = defaultdict(list)
    cur_port_family = None
    for elem in source_ports_elem:
        if elem.tag == 'span':
            cur_port_family = elem.text
        if elem.tag == 'a':
            if cur_port_family is not None:
                ports[cur_port_family].append(elem.text)

    return ports


def main():
    """Main function"""
    main_ports = get_main_port_info()
    if main_ports is not None:
        main_ports.update(HARDCODED_PORT_INFO)
        for family, versions in main_ports.items():
            for version in versions:
                print(OUTPUT_TEMPLATE.format(
                    family=family,
                    version=version
                ))

    print()
    wad_ports = get_wad_port_info('586')
    if wad_ports is not None:
        for family, versions in wad_ports.items():
            for version in versions:
                print(OUTPUT_TEMPLATE.format(
                    family=family,
                    version=version
                ))


if (__name__ == '__main__' or
        __name__ == 'get_port_info__main__'):
    main()
