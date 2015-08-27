import Queue
import time
import threading

from MeteorClient import MeteorClient


__all__ = ['robotwatchdog']

FINISH = 1


class _MeteorSender(object):

    def __init__(self, queue):
        self.run = None
        self.queue = queue
        self.thread = threading.Thread(target=self.work)
        self.client = MeteorClient('ws://127.0.0.1:3000/websocket')
        self.client.on('connected', self.connected_event)
        self.client.connect()

        self.configs = {
            # run
            'start_run': {
                'method': 'startRun',
                'callback': self.handle_run_call
            },

            # suites
            'start_suite': {'method': 'startSuite'},
            'end_suite': {'method': 'endSuite'},

            # tests
            'start_test': {'method': 'startTest'},
            'end_test': {'method': 'endTest'},

            # keywords
            'start_keyword': {'method': 'startKeyword'},
            'end_keyword': {'method': 'endKeyword'},

            # messages
            'log_message': {'method': 'logMessage'}
        }

    def connected_event(self):
        self.connected = True
        self.thread = threading.Thread(target=self.work)
        self.thread.start()

    def handle_call(self, error, result):
        self.error = error
        self.called = True

    def handle_run_call(self, error, result):
        self.handle_call(error, result)
        self.run = result.get('run', None)

    def work(self):
        while True:
            data = self.queue.get()
            if data == FINISH:
                return

            if self.run:
                data.update({'run': self.run})

            # Handle the data
            op = data['op']
            del data['op']
            if op not in self.configs:
                continue

            config = self.configs[op]
            method = config.get('method')
            callback = config.get('callback', self.handle_call)

            try:
                self.called = False
                self.client.call(method, [data], callback)
                while not self.called:
                    time.sleep(0.05)
            except:
                pass

    def close(self):
        self.thread.join()


class _Counter(object):

    def __init__(self, id_):
        self.id = id_
        self.count = 0

    def add(self):
        self.count = self.count + 1


class robotwatchdog(object):

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.ids = []
        self.queue = Queue.Queue()
        self.sender = _MeteorSender(self.queue)
        self.queue.put({'op': 'start_run'})

    def close(self):
        self.queue.put(FINISH)
        self.sender.close()

    def start_suite(self, name, attributes):
        self.ids.append(_Counter(attributes['id']))
        self.queue.put({
            'op': 'start_suite',
            'name': name,
            'attributes': attributes,
        })

    def end_suite(self, name, attributes):
        self.ids.pop()
        self.queue.put({
            'op': 'end_suite',
            'name': name,
            'attributes': attributes,
        })

    def start_test(self, name, attributes):
        self.ids.append(_Counter(attributes['id']))
        self.queue.put({
            'op': 'start_test',
            'name': name,
            'attributes': attributes,
        })

    def end_test(self, name, attributes):
        self.ids.pop()
        self.queue.put({
            'op': 'end_test',
            'name': name,
            'attributes': attributes,
        })

    def start_keyword(self, name, attributes):
        id_ = self._build_id()
        self.ids.append(_Counter(id_))

        attributes.update({'id': id_})
        self.queue.put({
            'op': 'start_keyword',
            'name': name,
            'attributes': attributes,
        })

    def end_keyword(self, name, attributes):
        counter = self.ids.pop()
        attributes.update({'id': counter.id})

        self.queue.put({
            'op': 'end_keyword',
            'name': name,
            'attributes': attributes,
        })

    def log_message(self, message):
        self.queue.put({
            'op': 'log_message',
            'id': self.ids[-1].id,
            'message': message,
        })

    def _build_id(self):
        counter = self.ids[-1]
        counter.add()
        return '%s-k%s' % (counter.id, counter.count)
