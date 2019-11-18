
class MobilePayTaskThread(threading.Thread):

    def __init__(self, root, log, host):
        super().__init__()
        self.root = root
        self.log = log
       
    def run(self):
       while not self._stop_event.is_set():
            if not Adam_Set_Cmd.empty():
                pass

    def stop(self):
        self.stop = True
        self._stop_event.set()
