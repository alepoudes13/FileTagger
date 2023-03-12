import os, glob
from tkinter import *
from tkinter import filedialog
from video import VideoPlayer
from database import DBConnector
from dictionary import Dict
from PIL import Image, ImageTk

class Window:
    def __init__(self) -> None:
        self.dir = None
        self.leftIndex = None
        self.lastIndex = None
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
        search_mode = 0
        if '|' in self.searchFilter:
            search_mode = 1 if self.searchFilter[0:2] == '||' else 2
        self.the_listbox.delete(0, END)
        self.tags_listbox.delete(0, END)
        print(search_mode)
        for file in self.files:
            tags = db.getTags(file)
            match search_mode:
                case 0:
                    if self.searchFilter.lower() in file:
                        self.the_listbox.insert(END, file)
                        self.tags_listbox.insert(END, tags)
                case 1:
                    if tags == '':
                        continue
                    fit, size, tags_size = 0, 0, 0
                    for search in self.searchFilter.lower().split('|'):
                        if search == '':
                            continue
                        size += 1
                        tags_size = 0
                        for tag in tags.split('|'):
                            if tag == '':
                                continue
                            tags_size += 1
                            if search in tag[:len(search)]:
                                fit += 1
                    if fit == size == tags_size:
                        self.the_listbox.insert(END, file)
                        self.tags_listbox.insert(END, tags)
                case 2:
                    if tags == '':
                        continue
                    fit, size = 0, 0
                    for search in self.searchFilter.lower().split('|'):
                        if search == '':
                            continue
                        size += 1
                        for tag in tags.split('|'):
                            if tag == '':
                                continue
                            if search in tag[:len(search)]:
                                fit += 1
                    if fit == size:
                        self.the_listbox.insert(END, file)
                        self.tags_listbox.insert(END, tags)
        
        self.the_listbox.insert(END, "")
        self.tags_listbox.insert(END, "")
        self.the_listbox.insert(END, "Total Files: " + str(self.the_listbox.size() - 1))
        self.tags_listbox.insert(END, "")

    def openFolder(self):
        self.dir = filedialog.askdirectory(title = "Select folder to open")
        db.createTable(self.dir)
        self.dict = Dict(db)
        self.listFilesInFolder()

    def frameResize(self, event = None):
        self.listFrame.config(height=self.window.winfo_height() - self.button_explore.winfo_height(), width = self.window.winfo_width() / 2)
        self.thumbFrame.config(height=self.window.winfo_height() - self.button_explore.winfo_height(), width = self.window.winfo_width() / 2)
        self.thumbFrame.place(relx=0.5, y = self.button_explore.winfo_height())

    def onItemSelection(self, event = None):
        if self.leftIndex == event.widget.curselection()[0]:
            self.lastIndex = event.widget.curselection()[-1]
        else:
            self.lastIndex = event.widget.curselection()[0]
        self.leftIndex = event.widget.curselection()[0]
        w, h = (self.window.winfo_width() - self.listFrame.winfo_width(), self.listFrame.winfo_height())
        try:
            thumb = Image.open(self.dir + '/' + self.the_listbox.get(self.lastIndex))
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
            video = VideoPlayer(self.thumbFrame, self.dir + '/' + self.the_listbox.get(self.lastIndex), w, h)

    def onEnterKey(self, event = None):
        self.active_list = event.widget
        self.curselect_list = self.active_list.curselection()

        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))
        self.tagsEntry = Entry(self.topFrame)
        self.tagsEntry.pack()
        self.tagsEntry.bind('<Return>', self.onEntrySubmit)
        self.tagsEntry.bind('<KeyRelease>', self.onTagsEntryKeyRelease)
        self.tagsEntry.bind('<Tab>', self.onTab)
        self.tagsEntry.bind('<Down>', self.onEntryDown)
        self.topFrame.bind('<Escape>', self.destroyTop)
        self.hints_listbox = Listbox(self.topFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white")
        self.hints_listbox.pack(expand=True, fill=BOTH)
        self.hints_listbox.bind('<Return>', self.onHintSelection)
        self.tagsEntry.focus_set()

    def onEntryDown(self, event):
        self.hints_listbox.focus_set()
        self.hints_listbox.selection_set(0)

    def onHintSelection(self, event):
        try:
            hint = event.widget.get(event.widget.curselection()[0])
            self.tagsEntry.delete(0, END)
            self.tagsEntry.insert(END, hint)
            self.tagsEntry.focus_set()
        except:
            pass

    def destroyTop(self, event):
        self.topFrame.destroy()
        self.active_list.activate(self.lastIndex)
        self.active_list.selection_set(self.lastIndex)

    def onEntrySubmit(self, event = None):
        tag = self.tagsEntry.get()
        for index in self.curselect_list:
            tags = self.tags_listbox.get(index)
            db.setTag(self.the_listbox.get(index), tag)
            self.tags_listbox.delete(index)
            self.tags_listbox.insert(index, db.getTags(self.the_listbox.get(index)))
            self.active_list.selection_set(index)
            self.dict.addTag(tag)
        db.commit()
        self.tagsEntry.delete(0, END)

    def onTagsEntryKeyRelease(self, event):
        word = self.tagsEntry.get()
        hints = self.dict.getHints(word)
        self.hints_listbox.delete(0, END)
        for hint in hints:
            self.hints_listbox.insert(END, hint[0])
        self.hints_listbox.configure(height=0)

    def onTab(self, event):
        hint = self.hints_listbox.get(0)
        self.tagsEntry.delete(0, END)
        self.tagsEntry.insert(END, hint)
        self.tagsEntry.focus_set()
        return "break"
    
    def listFilesInFolder(self):
        self.frameResize()
        
        self.the_listbox = Listbox(self.listFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white", selectmode=EXTENDED)
        self.the_listbox.place(relx = 0, rely = 0, relwidth = 0.4, relheight = 1)
        self.the_listbox.bind('<<ListboxSelect>>', self.onItemSelection)
        self.the_listbox.bind('<MouseWheel>', self.onMouseWheel)
        self.the_listbox.bind('<Return>', self.onEnterKey)
        self.the_listbox.bind('<Up>', self.onKeyUpDown)
        self.the_listbox.bind('<Down>', self.onKeyUpDown)
        self.the_listbox.bind('<BackSpace>', self.onBackspace)

        self.tags_listbox = Listbox(self.listFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white", selectmode=EXTENDED)
        self.tags_listbox.place(relx = 0.4, rely = 0, relwidth = 0.6, relheight = 1)
        self.tags_listbox.bind('<<ListboxSelect>>', self.onItemSelection)
        self.tags_listbox.bind('<Return>', self.onEnterKey)
        self.tags_listbox.bind('<MouseWheel>', self.onMouseWheel)
        self.tags_listbox.bind('<Up>', self.onKeyUpDown)
        self.tags_listbox.bind('<Down>', self.onKeyUpDown)
        self.tags_listbox.bind('<BackSpace>', self.onBackspace)
        
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
        return "break"
    
    def onKeyUpDown(self, event):
        index = 0
        selection = None
        if event.keysym == 'Up':
            index = -1
            selection = min(event.widget.curselection()[0], event.widget.curselection()[-1])
        elif event.keysym == 'Down':
            index = 1
            selection = max(event.widget.curselection()[0], event.widget.curselection()[-1])
        self.the_listbox.see(selection + index)
        self.tags_listbox.see(selection + index)
    
    def onBackspace(self, event):
        for index in event.widget.curselection():
            self.dict.deleteTags(self.tags_listbox.get(index))
            db.deleteName(self.the_listbox.get(index))
            self.tags_listbox.delete(index)
            self.tags_listbox.insert(index, '')
            event.widget.selection_set(index)
        db.commit()
        event.widget.activate(self.lastIndex)

if __name__ == '__main__':
    db = DBConnector('database.db')
    window = Window()
    window.window.mainloop()