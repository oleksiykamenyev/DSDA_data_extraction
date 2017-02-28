"""DSDA comment getter

Gets list of comments and frequency for each comment
"""

import helper_functions.helper_functions as hf
import io
import operator
import os
import re

__author__ = '4shockblast'


PLAYER_NAME_TO_URL_DICT = {}
PLAYER_NAME_TO_URL_FILE_NAME = 'player_name_to_url.txt'
FDA_RE = re.compile(r'^Final Time: ', re.IGNORECASE)
RATING_RE = re.compile(r'^rating\s*-\s*', re.IGNORECASE)
PLAYS_BACK_WITH_RE = re.compile(r'^Plays back with ', re.IGNORECASE)
UV_MAX_ATTEMPT_RE = re.compile(r'^UV[- ]Max attempt', re.IGNORECASE)
THROUGH_RE = re.compile(r'^Through ', re.IGNORECASE)
INCLUDES_RE = re.compile(r'^Includes ', re.IGNORECASE)
ATTEMPT_RE = re.compile(r'^.*attempt.*$', re.IGNORECASE)
DEMONSTRATES_RE = re.compile(r'^.*demonstrates.*$', re.IGNORECASE)
REQUIRES_RE = re.compile(r'^.*requires.*$', re.IGNORECASE)


def write_to_file(sorted_comment_count):
    for comment, count in sorted_comment_count:
        with io.open('comment_to_count.txt', 'a', encoding='utf8') \
                as comment_to_count_file:
            comment_to_count_file.write('{comment}|{comment_count}\n'.format(
                comment=comment.replace('\n', '\n '),
                comment_count=count
            ))

    with io.open('comment_to_count.txt', 'a', encoding='utf8') \
            as comment_to_count_file:
        comment_to_count_file.write('\n')


def main():
    """Main function"""
    if not PLAYER_NAME_TO_URL_DICT:
        if os.path.isfile(PLAYER_NAME_TO_URL_FILE_NAME):
            with io.open(PLAYER_NAME_TO_URL_FILE_NAME, encoding='utf8') \
                    as player_name_to_url_file:
                player_mappings = player_name_to_url_file.readlines()

            for player_map in player_mappings:
                player, url = player_map.rsplit('=')
                PLAYER_NAME_TO_URL_DICT[player] = url
        else:
            print("That's not how it works.")

    comment_to_count_dict = {}
    """
    for player, player_url in PLAYER_NAME_TO_URL_DICT.items():
        tree = hf.get_web_page_html(player_url.rstrip())

        # All comment rows on DSDA have this class
        rows = tree.xpath('//td[@class="comments"]')
        for row in rows:
            row_text = row.text
            if row_text in comment_to_count_dict:
                comment_to_count_dict[row_text] += 1
            else:
                comment_to_count_dict[row_text] = 1
    """

    fda_comments = {comment:count for comment, count in huge_thing.items()
                    if re.match(FDA_RE, comment)}
    rating_comments = {comment:count for comment, count in huge_thing.items()
                       if re.match(RATING_RE, comment)}
    plays_back_with_comments = {comment:count for comment, count in huge_thing.items()
                                if re.match(PLAYS_BACK_WITH_RE, comment)}
    uv_max_attempt_comments = {comment:count for comment, count in huge_thing.items()
                               if re.match(UV_MAX_ATTEMPT_RE, comment)}
    through_comments = {comment:count for comment, count in huge_thing.items()
                        if re.match(THROUGH_RE, comment)}
    includes_comments = {comment:count for comment, count in huge_thing.items()
                         if re.match(INCLUDES_RE, comment)}
    attempt_comments = {comment:count for comment, count in huge_thing.items()
                        if (re.match(ATTEMPT_RE, comment) and
                            not re.match(UV_MAX_ATTEMPT_RE, comment))}
    demonstrates_comments = {comment:count for comment, count in huge_thing.items()
                             if re.match(DEMONSTRATES_RE, comment)}
    requires_comments = {comment:count for comment, count in huge_thing.items()
                         if re.match(REQUIRES_RE, comment)}
    other_comments = {comment:count for comment, count in huge_thing.items()
                      if (not re.match(FDA_RE, comment) and
                          not re.match(RATING_RE, comment) and
                          not re.match(PLAYS_BACK_WITH_RE, comment) and
                          not re.match(UV_MAX_ATTEMPT_RE, comment) and
                          not re.match(THROUGH_RE, comment) and
                          not re.match(INCLUDES_RE, comment) and
                          not re.match(ATTEMPT_RE, comment) and
                          not re.match(DEMONSTRATES_RE, comment) and
                          not re.match(REQUIRES_RE, comment))
                      }
    sorted_fda_comments = sorted(fda_comments.items(),
                                 key=operator.itemgetter(1),
                                 reverse=True)
    sorted_rating_comments = sorted(rating_comments.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)
    sorted_plays_back_with_comments = sorted(plays_back_with_comments.items(),
                                             key=operator.itemgetter(1),
                                             reverse=True)
    sorted_uv_max_attempt_comments = sorted(uv_max_attempt_comments.items(),
                                            key=operator.itemgetter(1),
                                            reverse=True)
    sorted_through_comments = sorted(through_comments.items(),
                                     key=operator.itemgetter(1),
                                     reverse=True)
    sorted_includes_comments = sorted(includes_comments.items(),
                                      key=operator.itemgetter(1),
                                      reverse=True)
    sorted_attempt_comments = sorted(attempt_comments.items(),
                                     key=operator.itemgetter(1),
                                     reverse=True)
    sorted_demonstrates_comments = sorted(demonstrates_comments.items(),
                                          key=operator.itemgetter(1),
                                          reverse=True)
    sorted_requires_comments = sorted(requires_comments.items(),
                                      key=operator.itemgetter(1),
                                      reverse=True)
    sorted_other_comments = sorted(other_comments.items(),
                                   key=operator.itemgetter(1),
                                   reverse=True)
    write_to_file(sorted_fda_comments)
    write_to_file(sorted_rating_comments)
    write_to_file(sorted_plays_back_with_comments)
    write_to_file(sorted_uv_max_attempt_comments)
    write_to_file(sorted_through_comments)
    write_to_file(sorted_includes_comments)
    write_to_file(sorted_attempt_comments)
    write_to_file(sorted_demonstrates_comments)
    write_to_file(sorted_requires_comments)
    write_to_file(sorted_other_comments)

if (__name__ == '__main__' or
        __name__ == 'dsda_command_line__main__'):
    main()