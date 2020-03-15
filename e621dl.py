#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Internal Imports
import os
from distutils.version import StrictVersion
from fnmatch import fnmatch

# Personal Imports
from e621dl import constants
from e621dl import local
from e621dl import remote

# This block will only be read if e621dl.py is directly executed as a script. Not if it is imported.
if __name__ == '__main__':
    # Create the requests session that will be used throughout the run.
    with remote.requests_retry_session() as session:
        # Set the user-agent. Requirements are specified at https://e621.net/help/show/api#basics.
        session.headers['User-Agent'] = f"e621dl.py/{constants.VERSION} (by Wulfre)"
        
        # Check if a new version is released on github. If so, notify the user.
        if StrictVersion(constants.VERSION) < StrictVersion(remote.get_github_release(session)):
            print('A NEW VERSION OF e621dl IS AVAILABLE ON GITHUB AT https://github.com/Wulfre/e621dl/releases/latest.')

        print(f"[i] Running e621dl version {constants.VERSION}.")
        print('')
        print("[i] Checking for partial downloads...")

        remote.finish_partial_downloads(session)

        print('')
        print("[i] Parsing config...")

        config = local.get_config()

        # Initialize the lists that will be used to filter posts.
        searches = []

        # Initialize last_id
        last_id = None

        # Initialize user configured options in case any are missing.
        default_days = config['default_search'].get('days', 1)
        default_score = config['default_search'].get('min_score', -0x7F_FF_FF_FF)
        default_favs = config['default_search'].get('min_favs', 0)
        default_ratings = config['default_search'].get('ratings', ['s'])

        #blacklist = [remote.get_tag_alias(tag.lower(), session) for tag in config['blacklist']]
        blacklist = config['blacklist']

        for key, value in config['searches'].items():
            # Get the tags that will be searched for. Tags are aliased to their acknowledged names.
            #section_tags = [remote.get_tag_alias(tag.lower(), session) for tag in value['tags']]
            section_tags = value['tags']

            # Replace options that are specified by the user.
            section_date = local.get_date(value.get('days', default_days))
            section_score = value.get('min_score', default_score)
            section_favs = value.get('min_favs', default_favs)
            section_ratings = value.get('ratings', default_ratings)

            # Append the final values that will be used for the specific section to the list of searches.
            # Note section_tags is a list within a list.
            searches.append({
                'directory': key, 
                'tags': section_tags, 
                'ratings': section_ratings, 
                'min_score': section_score, 
                'min_favs': section_favs, 
                'earliest_date': section_date
            })

        for search in searches:
            print('')

            # Creates the string to be sent to the API.
            # Currently only 38 items can be sent directly so the rest are discarded to be filtered out later.
            if len(search['tags']) > constants.MAX_TAGS:
                search_string = ' '.join(search['tags'][:constants.MAX_TAGS])
            else:
                search_string = ' '.join(search['tags'])

            # Sets up a loop that will continue indefinitely until the last post of a search has been found.
            while True:
                print("[i] Getting posts...")
                results = remote.get_posts(search_string, search['earliest_date'], last_id, session)['posts']

                # Gets the id of the last post found in the search so that the search can continue.
                try:
                    last_id = results[-1]['id']
                except IndexError:
                    last_id = None
                    print('[i] No more posts for current search.')

                for post in results:
                    path = local.make_path(search['directory'], post['id'], post['file']['ext'])
                    tags = [x for y in post['tags'].values() for x in y]

                    if os.path.isfile(path):
                        print(f"[✗] Post {post['id']} was already downloaded.")
                    elif post['file']['url'] == None:
                        print(f"[✗] Post {post['id']} was skipped for being hidden to guest users.")
                    elif post['rating'] not in search['ratings']:
                        print(f"[✗] Post {post['id']} was skipped for missing a requested rating.")
                    # Using fnmatch allows for wildcards to be properly filtered.
                    elif [x for x in tags if any(fnmatch(x, y) for y in blacklist)]:
                        print(f"[✗] Post {post['id']} was skipped for having a blacklisted tag.")
                    elif not set(search['tags'][(constants.MAX_TAGS - 1):]).issubset(tags):
                        print(f"[✗] Post {post['id']} was skipped for missing a requested tag.")
                    elif int(post['score']['total']) < search['min_score']:
                        print(f"[✗] Post {post['id']} was skipped for having a low score.")
                    elif int(post['fav_count']) < search['min_favs']:
                        print(f"[✗] Post {post['id']} was skipped for having a low favorite count.")
                    else:
                        print(f"[✓] Post {post['id']} is being downloaded.")
                        remote.download_post(post['file']['url'], path, session)

                # Break while loop. End program.
                if last_id == None:
                    break

    # End program.
    print('')
    input("[✓] All searches complete. Press ENTER to exit...")
    raise SystemExit
