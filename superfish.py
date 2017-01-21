# SUPERFLUFFY (c) 2017 Billy Charlton <billy@okbecause.com>
import sys
import time
import logging
import json
import os
import ntpath
from urllib.request import Request, urlopen
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

watch_folder = 'onSite'
save_folder = 'edited'
api_key = os.environ['FISH_API_KEY']

fish_url = 'https://private-anon-f9a54eb248-fishnflrdq.apiary-mock.com/content/hostname/rdq/v3/prod'
#fish_url = 'https://fishapi.fishsoftware.com/content/hostname/rdq/v3/prod'


class FileEvent(FileSystemEventHandler):
    def on_modified(self, event):
        process_file(event.src_path)


def fetch_details(badge_id):
    payload = '{"auth_id" : ' + api_key + ', "badge_id": ' + badge_id + '}'
    headers = {'Content-Type': 'application/json'}

    request = Request(fish_url, data=payload.encode('utf-8'), headers=headers)
    response_body = urlopen(request).read().decode('utf-8')
    jbody = json.loads(response_body, encoding='utf-8')

    result = {}
    result['FirstName'] = jbody['first_name']
    result['LastName'] = jbody['last_name']
    result['EmailAddress'] = jbody['email']

    return result


def process_file(src_path):
    with open(src_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            badge_id = data['BadgeID']
            del data['BadgeID']

            details = fetch_details(badge_id)
            for k,v in details.items():
                data[k] = v

        except:
            print("Couldn't munge:", src_path)
            return

    outfile = os.path.join(save_folder, ntpath.basename(src_path))

    with open(outfile, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    path = sys.argv[1] if len(sys.argv) > 1 else watch_folder

    logger = LoggingEventHandler()
    file_eventer = FileEvent()

    observer = Observer()
    observer.schedule(logger, path, recursive=False)
    observer.schedule(file_eventer, path, recursive=False)
    observer.start()

    # loop forever but listen for ctrl-c
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
