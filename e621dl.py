#!/usr/bin/env python3

import os
import httpx
from e621dl import constants
from e621dl import local
from e621dl import remote

if __name__ == '__main__':
    print(f"[i] Running e621dl version {constants.VERSION}.")

    print("[i] Getting config...")
    config = local.get_config()
    
    blacklist = config.get('blacklist') if config.get('blacklist') is not None else []
    search_defaults = config.get('search_defaults')

    searches = []
    for key, value in config.get('searches').items():
        if len(value.get('tags')) > constants.MAX_SEARCH_TAGS:
            print(f"[i] Too many tags in search '{key}'. Tags after {constants.MAX_SEARCH_TAGS} will be discarded.")
            value['tags'] = value['tags'][:constants.MAX_SEARCH_TAGS]
    
        searches.append({
            'directory': key,
            'tags': value.get('tags'),
            'start_date': local.get_start_date(value.get('days', search_defaults.get('days', 1))),
            'min_score': value.get('min_score', search_defaults.get('min_score', 0)),
            'min_fav_count': value.get('min_fav_count', search_defaults.get('min_fav_count', 0)),
            'allowed_ratings': value.get('allowed_ratings', search_defaults.get('allowed_ratings', ['s']))
        })

    with httpx.Client(
        headers = {'user-agent': f"e621dl.py/{constants.VERSION} (by Wulfre)"},
        auth = (config.get('auth').get('username'), config.get('auth').get('api_key')) if config.get('auth').get('api_key') is not None else None
    ) as client:
        for search in searches:
            print(f"[i] Getting posts for search '{search['directory']}'.")

            last_id = None
            while True:
                posts = remote.get_posts(client, ' '.join(search['tags']), search['start_date'], last_id)
                
                for post in posts:
                    path = local.make_path(search.get('directory'), post.get('id'), post.get('file').get('ext'))

                    if os.path.isfile(path):
                        print(f"[i] Post {post.get('id')} was already downloaded.")
                    elif post.get('file').get('url') is None:
                        print(f"[✗] Post {post.get('id')} was skipped for being hidden to guests.")
                    elif post.get('rating') not in search.get('allowed_ratings'): 
                        print(f"[✗] Post {post.get('id')} was skipped for having a mismatched rating.")
                    elif any(x in [x for y in post.get('tags').values() for x in y] for x in blacklist):
                        print(f"[✗] Post {post.get('id')} was skipped for having a blacklisted tag.")
                    elif post.get('score').get('total') < search.get('min_score'):
                        print(f"[✗] Post {post.get('id')} was skipped for having a low score.")
                    elif post.get('fav_count') < search.get('min_fav_count'):
                        print(f"[✗] Post {post.get('id')} was skipped for having a low favorite count.")
                    else:
                        print(f"[✓] Post {post.get('id')} is being downloaded.")
                        remote.download_post(client, post.get('file').get('url'), path)

                last_id = posts[-1].get('id') if posts else None
                if last_id is None:
                    break

    print('[i] All searches complete.')
    raise SystemExit
