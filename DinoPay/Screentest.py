from tkinter import *

def create_win():
    def close(): win1.destroy();win2.destroy()
    win1 = Toplevel()
    win1.geometry('%dx%d%+d+%d'%(sw,sh,-sw,0))
    Button(win1,text="Exit1",command=close).pack()
    win2 = Toplevel()
    win2.geometry('%dx%d%+d+%d'%(sw,sh,sw,0))
    Button(win2,text="Exit2",command=close).pack()

root=Tk()
sw,sh = root.winfo_screenwidth(),root.winfo_screenheight()
#print "screen1:",sw,sh
#w,h = 800,600 
a= 0
b = 0

fm = Frame(root)
Button(fm, text='Top').pack(side=TOP, anchor=W, fill=X, expand=YES)
Button(fm, text='Center').pack(side=TOP, anchor=W, fill=X, expand=YES)
Button(fm, text='Bottom').pack(side=TOP, anchor=W, fill=X, expand=YES)
Button(fm, text='Left').pack(side=LEFT)
Button(fm, text='This is the Center button').pack(side=LEFT)
Button(fm, text='Right').pack(side=LEFT)        
fm.pack(fill=BOTH, expand=YES)

root.geometry("{0}x{1}+{2}+{3}".format(sw,sh,a,b))
root.mainloop()