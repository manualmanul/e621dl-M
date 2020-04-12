VERSION = '5.0.0'

MAX_SEARCH_RESULTS = 320
MAX_SEARCH_TAGS = 38
MAX_REQUESTS_PER_SECOND = 1
PARTIAL_DOWNLOAD_EXT = 'request'

DEFAULT_CONFIG_TEXT = '''auth:
    username:
    api_key:

# Note that if you included your auth above, then your account blacklist will already be applied.
blacklist:

search_defaults:
    days: 1
    min_score: 0
    min_fav_count: 0
    allowed_ratings:
        - s

searches:
    cats:
        tags:
            - cat
            - yellow_fur
    dogs:
        tags:
            - dog
            - brown_fur

# The most common search structure has already been exemplified, but you may overwrite any of the default search settings for a specific search.
#
# searches:
#   dogs:
#       days: 30
#       min_score: 10
#       min_fav_count: 10
#       allowed_ratings:
#           - s
#           - q
#           - e
#       tags:
#           - dog
#           - brown_fur'''
