import logging
import tkinter as tk
from GUI import  MainGui



   
def main():
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    app =MainGui.App(root)
    app.root.mainloop()


     

if __name__ == '__main__':
    main()
    