from time import sleep
from e621dl import constants

def get_posts(client, search_string, start_date, last_id):
    response = client.get(
        url = 'https://e621.net/posts.json',
        params = {
            'limit': constants.MAX_SEARCH_RESULTS,
            'tags': f"{search_string} date:>={start_date} {'id:<' + str(last_id) if last_id else ''}"
        }
    )
    response.raise_for_status()

    if response.elapsed.total_seconds() < 1:
        sleep(1 - response.elapsed.total_seconds())

    return response.json().get('posts')

def download_post(client, url, path):
    with client.stream('GET', url) as response:
        response.raise_for_status()
        
        with open(path, 'wb') as file:
            for chunk in response.iter_bytes():
                file.write(chunk)
