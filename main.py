import os, glob
from tkinter import *
from tkinter import filedialog
from video import VideoPlayer
from database import DBConnector
from PIL import Image, ImageTk

class Window:
    def __init__(self) -> None:
        self.dir = None
        self.window = Tk()
        self.window.title('Tagger')
        self.window.geometry("1000x500")
        self.window.config(background = "white")
        self.button_explore = Button(self.window, text = "Browse Files", command = self.openFolder)
        self.button_explore.grid(column = 1, row = 1)  
        self.button_exit = Button(self.window, text = "Exit", command = exit)
        self.button_exit.grid(column = 2, row = 1)
        self.listFrame = Frame(self.window, width = 500, height = self.window.winfo_height() - self.button_explore.winfo_height())
        self.thumbFrame = Frame(self.window, width = 500, height = self.window.winfo_height() - self.button_explore.winfo_height())
        self.window.bind('<Configure>', self.frameResize)
        self.searchEntry = Entry(self.window, background='#cccccc')
        self.searchEntry.grid(row = 1, column = 3)
        self.searchEntry.bind('<KeyRelease>', self.getSearchEntry)

    def getSearchEntry(self, event = None):
        self.searchFilter = self.searchEntry.get()
        self.the_listbox.delete(0, END)
        self.tags_listbox.delete(0, END)
        for file in self.files:
            tags = db.getTags(file)
            if self.searchFilter.lower() in tags.lower() or self.searchFilter in file:
                self.the_listbox.insert(END, file)
                self.tags_listbox.insert(END, tags)

    def openFolder(self):
        self.dir = filedialog.askdirectory(title = "Select folder to open")
        db.createTable(self.dir)
        self.listFilesInFolder()

    def frameResize(self, event = None):
        self.listFrame.config(height=self.window.winfo_height() - self.button_explore.winfo_height(), width = self.window.winfo_width() / 2)
        self.thumbFrame.config(height=self.window.winfo_height() - self.button_explore.winfo_height(), width = self.window.winfo_width() / 2)
        self.thumbFrame.place(relx=0.5, y = self.button_explore.winfo_height())

    def onItemSelection(self, event = None):
        index = event.widget.curselection()[-1]
        w, h = (self.window.winfo_width() - self.listFrame.winfo_width(), self.listFrame.winfo_height())
        try:
            thumb = Image.open(self.dir + '/' + self.the_listbox.get(index))
            if thumb.height > thumb.width:
                w /= thumb.height / thumb.width
            else:
                h /= thumb.width / thumb.height
            thumb = thumb.resize((int(w), int(h)))
            tk_thumb = ImageTk.PhotoImage(thumb)
            for widgets in self.thumbFrame.winfo_children():
                widgets.destroy()
            label = Label(self.thumbFrame, image=tk_thumb)
            label.image = tk_thumb
            label.place(relx=0.5, rely=0.5, anchor=CENTER)
        except:
            for widgets in self.thumbFrame.winfo_children():
                widgets.destroy()
            video = VideoPlayer(self.thumbFrame, self.dir + '/' + self.the_listbox.get(index), w, h)

    def onEnterKey(self, event = None):
        self.active_list = event.widget
        self.curselect_list = self.active_list.curselection()

        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))
        self.tagsEntry = Entry(self.topFrame)
        self.tagsEntry.pack(ipadx=(self.thumbFrame.winfo_width()-125)/2)
        self.tagsEntry.bind('<Return>', self.onEntrySubmit)
        self.topFrame.bind('<Escape>', self.destroyTop)
        if len(self.curselect_list) == 1:
            self.tagsEntry.insert(0, self.tags_listbox.get(self.curselect_list[-1]))
        self.tagsEntry.focus_set()

    def destroyTop(self, event):
        self.topFrame.destroy()

    def onEntrySubmit(self, event = None):
        tags = self.tagsEntry.get()
        for index in self.curselect_list:
            self.tags_listbox.delete(index)
            self.tags_listbox.insert(index, tags)
            self.active_list.selection_set(index)
            db.setTags(self.the_listbox.get(index), tags)
        self.topFrame.destroy()
        self.active_list.activate(self.curselect_list[-1])

    def listFilesInFolder(self):
        self.frameResize()
        
        self.the_listbox = Listbox(self.listFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white", selectmode=EXTENDED)
        self.the_listbox.place(relx = 0, rely = 0, relwidth = 0.4, relheight = 1)
        self.the_listbox.bind('<<ListboxSelect>>', self.onItemSelection)
        self.the_listbox.bind('<MouseWheel>', self.onMouseWheel)
        self.the_listbox.bind('<Return>', self.onEnterKey)
        self.the_listbox.bind('<Up>', self.onKeyUpDown)
        self.the_listbox.bind('<Down>', self.onKeyUpDown)

        self.tags_listbox = Listbox(self.listFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white", selectmode=EXTENDED)
        self.tags_listbox.place(relx = 0.4, rely = 0, relwidth = 0.6, relheight = 1)
        self.tags_listbox.bind('<<ListboxSelect>>', self.onItemSelection)
        self.tags_listbox.bind('<Return>', self.onEnterKey)
        self.tags_listbox.bind('<MouseWheel>', self.onMouseWheel)
        self.tags_listbox.bind('<Up>', self.onKeyUpDown)
        self.tags_listbox.bind('<Down>', self.onKeyUpDown)
        
        the_scrollbar = Scrollbar(self.tags_listbox, orient=VERTICAL,command=self.onScroll)
        self.the_listbox.config(yscrollcommand=the_scrollbar.set)
        self.tags_listbox.config(yscrollcommand=the_scrollbar.set)
        the_scrollbar.pack(side=RIGHT, fill=Y)
        self.listFrame.place(x = 0, y = self.button_explore.winfo_height())

        files = list(filter(os.path.isfile, glob.glob(self.dir + "\*")))
        files.sort(key=os.path.getctime)
        files.reverse()
        self.files = [file.split("\\")[-1] for file in files]
        for file in self.files:
            self.the_listbox.insert(END, file)
            self.tags_listbox.insert(END, db.getTags(file))
        self.the_listbox.insert(END, "")
        self.tags_listbox.insert(END, "")
        self.the_listbox.insert(END, "Total Files: " + str(len(files)))
        self.tags_listbox.insert(END, "")

    def onScroll(self, *args):
        self.the_listbox.yview(*args)
        self.tags_listbox.yview(*args)

    def onMouseWheel(self, event):
        self.the_listbox.yview("scroll", int(-event.delta / 10), "units")
        self.tags_listbox.yview("scroll", int(-event.delta / 10),"units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"
    
    def onKeyUpDown(self, event):
        index = 0
        if event.keysym == 'Up':
            index = -1
        elif event.keysym == 'Down':
            index = 1
        selection = event.widget.curselection()[-1]
        self.the_listbox.see(selection + index)
        self.tags_listbox.see(selection + index)

if __name__ == '__main__':
    db = DBConnector('database.db')
    window = Window()
    window.window.mainloop()