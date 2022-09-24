import threading
class ThreadWithCallback(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        target = kwargs.pop('target')
        super(ThreadWithCallback, self).__init__(target=self.target_with_callback, *args, **kwargs, daemon=True)
        self.callback = callback
        self.method = target
        self.callback_args = callback_args

    def target_with_callback(self, *args):
        ret = self.method(*args)
        if self.callback is not None:
            self.callback(ret)
