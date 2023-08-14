import os, glob, shutil
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from video import VideoPlayer
from database import DBConnector
from dictionary import Dict
import clipboard
from PIL import Image, ImageTk

SHIFT = 16
SHIFT_MODE = 0

class Window:

    #WINDOW MANAGEMENT================================================================

    def close(self):
        db.deleteEmptyTable()
        db.close()
        exit()

    #INIT================================================================

    def __init__(self) -> None:
        self.lastSelected = 0
        self.history = []
        self.dir = None
        self.leftIndex = None
        self.lastIndex = None
        self.window = Tk()
        self.window.title('Tagger')
        self.window.geometry("1000x500")
        self.window.config(background = "white")
        menu_bar = ttk.Frame(self.window, width=1000)
        menu_bar.place(x = 0, y = 0, relwidth = 1, relheight = 0.05)
        self.button_explore = ttk.Button(menu_bar, text = "Browse Files", command = self.openFolder)
        self.button_explore.grid(column = 1, row = 1)  
        button_exit = ttk.Button(menu_bar, text = "Exit", command = self.close)
        button_exit.grid(column = 2, row = 1)
        button_copy = ttk.Button(menu_bar, text = "Copy", command = self.copyFiles)
        button_copy.grid(column = 4, row = 1)  
        button_move = ttk.Button(menu_bar, text = "Move to", command = self.moveFiles)
        button_move.grid(column = 5, row = 1)
        button_del = ttk.Button(menu_bar, text = "Delete files", command = self.deleteFiles)
        button_del.grid(column = 6, row = 1)
        button_tag = ttk.Button(menu_bar, text = "Change tag to", command = self.changeTag)
        button_tag.grid(column = 7, row = 1)
        button_stat = ttk.Button(menu_bar, text = "Tags stat", command = self.showStat)
        button_stat.grid(column = 8, row = 1)
        self.listFrame = ttk.Frame(self.window, width = 500, height = self.window.winfo_height() - self.button_explore.winfo_height())
        self.listFrame.place(x = 0, rely = 0.05, relwidth=0.5, relheight=0.95)
        self.thumbFrame = ttk.Frame(self.window, width = 500, height = self.window.winfo_height() - self.button_explore.winfo_height())
        self.thumbFrame.place(relx=0.5, rely = 0.05, relheight=0.95, relwidth=0.5)
        self.window.bind('<Control-c>', self.onCopy)
        self.searchEntry = ttk.Entry(menu_bar, background='#cccccc')
        self.searchEntry.grid(row = 1, column = 3)
        self.searchEntry.bind('<KeyRelease>', self.getSearchEntry)

        columns = ("#1", "#2")
        self.treeview = ttk.Treeview(self.listFrame, show="headings", columns=columns, selectmode=EXTENDED)

        self.treeview.heading("#1", text="Имя файла")
        self.treeview.heading("#2", text="Тэги")
        ysb = ttk.Scrollbar(self.listFrame, orient=VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=ysb.set)
        ysb.pack(fill=Y, side=RIGHT)
        self.treeview.pack(fill=BOTH, expand=True)
        self.treeview.bind('<<TreeviewSelect>>', self.onItemSelection)
        self.treeview.bind('<Return>', self.onEnterKey)
        self.treeview.bind('<BackSpace>', self.onBackspace)
        self.treeview.bind('<Up>', self.onKeyUpDown)
        self.treeview.bind('<Down>', self.onKeyUpDown)
        self.treeview.bind('<KeyPress>', self.keyPressed)
        self.treeview.bind('<KeyRelease>', self.keyReleased)

    #TAGS STAT================================================================

    def showStat(self):
        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))
        self.topFrame.bind('<Escape>', self.destroyTop)

        listbox = Listbox(self.topFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white")
        listbox.pack()
        listbox.configure(height=20)

        stat = self.dict.getStat()
        for i in stat:
            listbox.insert(END, str(i[0]) + ': ' + str(i[1]))

    #FILES MANAGEMENT================================================================

    def openFolder(self):
        self.dir = filedialog.askdirectory(title = "Select folder to open")
        db.createTable(self.dir)
        self.dict = Dict(db)
        self.listFilesInFolder()
    
    def onCopy(self, event):
        try:
            clipboard.send_image(self.dir + '/' + self.the_listbox.get(self.lastIndex))
        except:
            pass

    def copyFiles(self):
        dest = filedialog.askdirectory(title = "Select folder to open")
        db.createTable(dest)
        for index in self.treeview.selection()[::-1]:
            try:
                name, tags = self.treeview.item(index)["values"][0:2]
                shutil.copy2(self.dir + '/' + name, dest)
                db.setTag(name, tags)
            except:
                pass
        db.commit()
        db.createTable(self.dir)
    
    def moveFiles(self):
        dest = filedialog.askdirectory(title = "Select folder to open")
        db.createTable(dest)
        for index in self.treeview.selection()[::-1]:
            try:
                name, tags = self.treeview.item(index)["values"][0:2]
                db.setTag(name, tags)
                shutil.move(self.dir + '/' + name, dest)
                self.dict.deleteTags(tags)
            except:
                pass
        db.commit()
        db.createTable(self.dir)
        for index in self.treeview.selection()[::-1]:
            db.deleteName(name)
        db.commit()
        self.listFilesInFolder()

    def deleteFiles(self):
        for index in self.treeview.selection()[::-1]:
            try:
                name, tags = self.treeview.item(index)["values"][0:2]
                db.deleteName(name)
                self.dict.deleteTags(tags)
            except:
                pass
            os.remove(self.dir + '/' + name)
        db.commit()
        self.listFilesInFolder()

    #SEARCH ================================================================

    def getSearchEntry(self, event = None):
        searchFilter = self.searchEntry.get()
        search_mode = 0
        if '|' in searchFilter:
            search_mode = 1 if searchFilter[0:2] == '||' else 2
        self.treeview.delete(*self.treeview.get_children())

        for file in self.files:
            tags = db.getTags(file)
            match search_mode:
                case 0:
                    if searchFilter.lower() in file:
                        self.treeview.insert("", END, values=(file, tags))
                case 1:
                    if tags == '':
                        continue
                    fit, size, tags_size = 0, 0, 0
                    for search in searchFilter.lower().split('|'):
                        if search == '':
                            continue
                        size += 1
                        tags_size = 0
                        for tag in tags.split('|'):
                            if tag == '':
                                continue
                            tags_size += 1
                            for item in search.split('~'):
                                if item != '' and item in tag[:len(item)]:
                                    fit += 1
                                    break
                    if fit == size == tags_size:
                        self.treeview.insert("", END, values=(file, tags))
                case 2:
                    if tags == '':
                        continue
                    fit = 0
                    tags_lst = [x for x in tags.split('|') if x != '']
                    search_lst = [x for x in searchFilter.lower().split('|') if x != '']
                    size = len(search_lst)
                    for search in search_lst:
                        item_lst = [x for x in search.split('~') if x != '']
                        full_neg = False
                        for item in item_lst:
                            full_neg = True
                            if item[0] != '!':
                                full_neg = False
                                break
                        if full_neg:
                            size -= 1
                    for search in search_lst:
                        valid = False
                        for tag in tags_lst:
                            item_lst = [x for x in search.split('~') if x != '']
                            for item in item_lst:
                                exclude = 0
                                if item[0] == '!':
                                    exclude = 1
                                if item[exclude:] in tag[:len(item) - exclude]:
                                    if exclude == 0:
                                        valid = True
                                    else:
                                        fit = -1
                                        break
                            if fit == -1:
                                break
                        if valid:
                            fit += 1
                        if fit == -1:
                            break
                    if fit == size:
                        self.treeview.insert("", END, values=(file, tags))
        
        self.treeview.insert("", END, values=("", ""))
        self.treeview.insert("", END, values=("Total Files: " + str(len(self.treeview.get_children()) - 1), ''))

    #TAG CHANGE================================================================

    def changeTag(self):
        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))

        fromLabel = ttk.Label(self.topFrame, font=("Calibri", "10"), text="From:")
        fromLabel.grid(row=1, column=1)

        toLabel = ttk.Label(self.topFrame, font=("Calibri", "10"), text="To:")
        toLabel.grid(row=1, column=2)

        self.tagsEntry = ttk.Entry(self.topFrame)
        self.tagsEntry.grid(column=1, row=2)
        self.tagsEntry.bind('<KeyRelease>', self.onTagsEntryKeyRelease)
        self.tagsEntry.bind('<Tab>', self.onTab)
        self.tagsEntry.bind('<Down>', self.onEntryDown)
        self.tagsEntry.bind('<Right>', self.onRight)

        self.newTagEntry = ttk.Entry(self.topFrame)
        self.newTagEntry.grid(column=2, row=2)
        self.newTagEntry.bind('<Return>', self.onTagRenameSubmit)
        self.newTagEntry.bind('<Left>', self.onLeft)

        self.topFrame.bind('<Escape>', self.destroyTop)
        self.hints_listbox = Listbox(self.topFrame, selectbackground="#F24FBF", font=("Calibri", "10"), background="white")
        self.hints_listbox.grid(row=3, column=1)
        self.hints_listbox.bind('<Return>', self.onHintSelection)
        self.hints_listbox.configure(height=0)
        self.tagsEntry.focus_set()

    def onTagRenameSubmit(self, event = None):
        tag = self.tagsEntry.get().lower()
        newTag = self.newTagEntry.get().lower()
        db.rename(tag, newTag)
        db.commit()
        self.dict.rename(tag, newTag)
        self.tagsEntry.delete(0, END)
        self.newTagEntry.delete(0, END)
        for item in self.treeview.get_children():
            name = self.treeview.item(item)["values"][0]
            self.treeview.set(item, '#2', db.getTags(name))

    def onRight(self, event):
        self.newTagEntry.focus_set()

    def onLeft(self, event):
        self.tagsEntry.focus_set()

    #TAGS WINDOW================================================================

    def onEnterKey(self, event = None):
        self.curselect_list = self.treeview.selection()

        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))
        self.tagsEntry = ttk.Entry(self.topFrame)
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
        self.treeview.selection_set(self.lastIndex)

    def onEntrySubmit(self, event = None):
        tag = self.tagsEntry.get()
        for index in self.curselect_list:
            name, tags = self.treeview.item(index)["values"][0:2]
            db.setTag(name, tag)
            self.treeview.set(index, '#2', db.getTags(name))
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
    
    #FILES LIST================================================================

    def onItemSelection(self, event = None):
        
        if SHIFT in self.history and SHIFT_MODE in self.history:
            index = self.treeview.index(self.treeview.selection()[0]) if len(self.treeview.selection()) == 1 else self.lastSelected
            hex_str = hex(index + 1)[2:].upper()
            self.lastIndex = 'I' + '0' * max(0, 3 - len(hex_str)) + hex_str
        else:
            if self.leftIndex == event.widget.selection()[0]:
                self.lastIndex = event.widget.selection()[-1]
            else:
                self.lastIndex = event.widget.selection()[0]
            self.leftIndex = event.widget.selection()[0]
        name, tags = self.treeview.item(self.lastIndex)["values"][0:2]
        w, h = (self.window.winfo_width() - self.listFrame.winfo_width(), self.listFrame.winfo_height())
        try:
            if name.split('.')[-1] == 'gif':
                assert(0)
            thumb = Image.open(self.dir + '/' + name)
            if thumb.height > thumb.width:
                w /= thumb.height / thumb.width
            else:
                h /= thumb.width / thumb.height
            thumb = thumb.resize((int(w), int(h)))
            tk_thumb = ImageTk.PhotoImage(thumb)
            for widgets in self.thumbFrame.winfo_children():
                widgets.destroy()
            label = ttk.Label(self.thumbFrame, image=tk_thumb)
            label.image = tk_thumb
            label.place(relx=0.5, rely=0.5, anchor=CENTER)
        except:
            for widgets in self.thumbFrame.winfo_children():
                widgets.destroy()
            video = VideoPlayer(self.thumbFrame, self.dir + '/' + name, w, h)

    def listFilesInFolder(self):
        self.treeview.delete(*self.treeview.get_children())
        files = list(filter(os.path.isfile, glob.glob(self.dir + "\*")))
        files.sort(key=os.path.getctime)
        files.reverse()
        self.files = [file.split("\\")[-1] for file in files]
        for file in self.files:
            self.treeview.insert("", END, values=(file, db.getTags(file)))
        self.treeview.insert("", END, values=("", ""))
        self.treeview.insert("", END, values=("Total Files: " + str(len(files)), ''))
    
    def keyReleased(self, event):
        if event.keycode in self.history:
            self.history.pop(self.history.index(event.keycode))

    def keyPressed(self, event):
        if not event.keycode in self.history:
            self.history.append(event.keycode)

    def onKeyUpDown(self, event):
        if SHIFT in self.history:
            self.history.append(SHIFT_MODE)
            index = 0
            selection =  self.treeview.index(self.treeview.selection()[0]) if len(self.treeview.selection()) == 1 else self.lastSelected
            if event.keysym == 'Up':
                index = -1
            elif event.keysym == 'Down':
                index = 1
            try:
                hex_str = hex(selection + index + 1)[2:].upper()
                hex_str = 'I' + '0' * max(0, 3 - len(hex_str)) + hex_str
                if(hex_str in self.treeview.selection()):
                    hex_old = hex(selection + 1)[2:].upper()
                    self.treeview.selection_remove('I' + '0' * max(0, 3 - len(hex_old)) + hex_old)
                self.treeview.selection_add(hex_str)
                self.treeview.see(hex_str)
                self.treeview.focus(hex_str)
                self.lastSelected = selection + index

            except:
                pass
            return "break"
        else:
            try:
                self.history.pop(self.history.index(SHIFT_MODE))
            except:
                pass
    
    def onBackspace(self, event):
        for index in event.widget.selection():
            name, tags = self.treeview.item(index)["values"][0:2]
            self.dict.deleteTags(tags)
            db.deleteName(name)
            self.treeview.set(index, '#2', '')
        db.commit()

if __name__ == '__main__':
    db = DBConnector('database.db')
    window = Window()
    window.window.mainloop()