import tempfile
import win32api
import win32print
import time


def main():
	printer_name = 'CUSTOM VKP80 II'
	filename = 'receipt.pdf'
	test = win32api.ShellExecute (
  	0,
   "print",
   filename,
   #
   # If this is None, the default printer will
   # be used anyway.
   #
   '/d:"%s"' % printer_name,
   ".",
   0
   )
	print (test)
     

if __name__ == '__main__':
    main()
    #test()
    