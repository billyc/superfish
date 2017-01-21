# SUPERFLUFFY (c) 2017 Billy Charlton <billy@okbecause.com>

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler


class FileEvent(FileSystemEventHandler):
    def on_modified(self, event):
        print("Got one: ",event.src_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
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
    
    