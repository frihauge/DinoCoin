import datetime
import queue 
import logging
import signal
import time
import threading
import json
import tkinter as tk
from TaskRun import TaskRun

from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W


logger = logging.getLogger(__name__)
cmd_queue = queue.Queue()

class MainTask(threading.Thread):
    """Class to display the time every seconds
    Every 5 seconds, the time is displayed using the logging.ERROR level
    to show that different colors are associated to the log levels
    """

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def run(self):
        logger.debug('Main Task Started')
        logger.info('Loading appsettings')
        appsettings = self.ReadSetupFile()
        self.tr = TaskRun(logger, appsettings)
        previous_sec = -1
        previous_min = -1 
        while not self._stop_event.is_set():
            self.tr.runfast()
            if not cmd_queue.empty():
                try:
                    item = cmd_queue.get(block=True, timeout=2)
                    logger.info( "CMD Exe:: %s" % (item))
                    self.tr.customcmd(item)
                except:
                   print("Queue Error")     
            now = datetime.datetime.now()
            if previous_sec != now.second:
                previous_sec = now.second
                if (previous_sec % 10) == 0: 
                    level = logging.INFO
                    self.tr.run10s()
                if (previous_sec % 60) == 0: 
                    level = logging.INFO
                    self.tr.run1m()
            time.sleep(0.2)

    def stop(self):
        self._stop_event.set()
    
    def ReadSetupFile(self):
        data = None
        try:
            jsonFile = open('MainSetup.json', "r") # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
        except Exception as e:
            print('Json read error: ' , e)
        finally:   
            jsonFile.close() # Close the JSON file
        return data  


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logging.basicConfig(filename='test.log',
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')  
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


class FormUi:

    def __init__(self, frame):
        self.frame = frame
        # Create a combobbox to select the logging level
        values = ['DEBUG', 'INFO','Prize']
        self.level = tk.StringVar()
        ttk.Label(self.frame, text='Command:').grid(column=0, row=0, sticky=W)
        self.combobox = ttk.Combobox(
            self.frame,
            textvariable=self.level,
            width=25,
            state='readonly',
            values=values
        )
        self.combobox.current(0)
        self.combobox.grid(column=1, row=0, sticky=(W, E))
        # Create a text field to enter a message
        self.message = tk.StringVar()
        ttk.Label(self.frame, text='Message:').grid(column=0, row=1, sticky=W)
        ttk.Entry(self.frame, textvariable=self.message, width=25).grid(column=1, row=1, sticky=(W, E))
        # Add a button to log the message
        self.button = ttk.Button(self.frame, text='Submit', command=self.submit_message)
        self.button.grid(column=1, row=2, sticky=W)

    def submit_message(self):
        # Get the logging level numeric value
#        if self.level.get() =='Prize':
         lvl = getattr(logging, self.level.get())
         logger.log(lvl, self.message.get())
         cmd_queue.put( self.message.get())


class ThirdUi:

    def __init__(self, frame):
        self.frame = frame
    #    ttk.Label(self.frame, text='Text for third frame').grid(column=0, row=1, sticky=W)
    #    ttk.Label(self.frame, text='here!').grid(column=0, row=4, sticky=W)


class App:

    def __init__(self, root):
        self.root = root
        root.title('DINOCOIN Service Application')
        #root.attributes("-topmost", True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        form_frame = ttk.Labelframe(horizontal_pane, text="Manuel control")
        form_frame.columnconfigure(1, weight=1)
        horizontal_pane.add(form_frame, weight=1)
        console_frame = ttk.Labelframe(horizontal_pane, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        third_frame = ttk.Labelframe(vertical_pane, text="Status ")
        vertical_pane.add(third_frame, weight=1)
        # Initialize all frames

        self.form = FormUi(form_frame)
        self.console = ConsoleUi(console_frame)
        self.third = ThirdUi(third_frame)
        self.MainTask = MainTask()
        self.MainTask.start()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)




    def quit(self, *args):
        self.MainTask.stop()
        self.root.destroy()
