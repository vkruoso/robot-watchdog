import json
import Queue
import requests
import threading

__all__ = ['watchdog']

FINISH = 1


class sender(object):

    def __init__(self, queue):
        self.queue = queue
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            data = self.queue.get()
            if data == FINISH:
                return

            # Handle the data
            data = json.dumps(data, ensure_ascii=False).encode('utf8')

            try:
                requests.post('http://localhost:2688/', data)
            except:
                pass


class watchdog(object):

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.queue = Queue.Queue()
        self.sender = sender(self.queue)

    def close(self):
        self.queue.put(FINISH)

    def start_suite(self, name, attributes):
        self.queue.put({
            'op': 'start_suite',
            'name': name,
            'attributes': attributes,
        })

    def end_suite(self, name, attributes):
        self.queue.put({
            'op': 'end_suite',
            'name': name,
            'attributes': attributes,
        })

    def start_test(self, name, attributes):
        self.queue.put({
            'op': 'start_test',
            'name': name,
            'attributes': attributes,
        })

    def end_test(self, name, attributes):
        self.queue.put({
            'op': 'end_test',
            'name': name,
            'attributes': attributes,
        })

    def start_keyword(self, name, attributes):
        self.queue.put({
            'op': 'start_keyword',
            'name': name,
            'attributes': attributes,
        })

    def end_keyword(self, name, attributes):
        self.queue.put({
            'op': 'end_keyword',
            'name': name,
            'attributes': attributes,
        })
