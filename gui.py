#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vkaudio import *
from Tkinter import *
import tkFileDialog

class Global:
    dirname = 'nothing'

glob = Global()

def confirm_userdata(event):
    accountInfo.configure(text='sending data', fg='yellow')
    root.update_idletasks()    
    try:                      
        glob.account = Account(email.get(), password.get())
    except:                
        glob.account = None
    if glob.account.isvalid:
        accountInfo.configure(text='authentication is successful', fg='blue')       
    else:  
        accountInfo.configure(text='Not authorized', foreground='red')      
        print('Error')        
        glob.account =  None
    return account

def make_request(event):
    queryInfo.configure(text='Request status:\n search for \''+search.get() +'\'', fg='yellow')
    root.update_idletasks()
    folders = Folders('temp/', 'saved/')
    if glob.dirname != 'nothing':
        folders.save_to = glob.dirname + "/"
    print folders.save_to     
    track = Track(glob.account, search.get().encode('utf8'), folders)    
    if track.link and len(track.link) != 0:
        queryInfo.configure(text='Request status:\n download '+track.link, fg='yellow')
        root.update_idletasks()
        track.further()
        queryInfo.configure(text='Request status:\n File \'' + folders.save_to + track.filename + '\' has been saved', fg='blue')
        root.update_idletasks()
    else:    
        queryInfo.configure(text='Request status:\n \''+search.get()+ '\' not found', fg='red')
        root.update_idletasks() 
        
def choose_directory(event):
    invisible = Tk()
    invisible.withdraw()    
    glob.dirname = tkFileDialog.askdirectory(parent=invisible, initialdir="~",title='Pick a directory')
    invisible.destroy()
    
root = Tk()
root.wm_title(string='VKAudio')
root.wm_minsize(width=350, height=300)
root.geometry("+300+300")

email = StringVar()
password = StringVar()
search = StringVar()


accountFrame = Frame(root)
accountSign = Frame(accountFrame)
accountEmailLabel = Label(accountSign, text='Enter e-mail')
accountEmail = Entry(accountSign, width=30, bd=2, textvariable=email, justify=CENTER)
accountPasswordLabel = Label(accountSign, text='Enter password')
accountPassword = Entry(accountSign, width=30, bd=2, textvariable=password, justify=CENTER)
accountConfirm = Button(accountFrame, text='Login', width=20)
accountInfo = Label(accountFrame, text='Not authorized', foreground='red')

accountFrame.pack()
accountSign.pack()
accountEmailLabel.pack()
accountEmail.pack()
accountPasswordLabel.pack()
accountPassword.pack()
accountInfo.pack()
accountConfirm.pack()

space = Frame(root, height=10)
space.pack()

queryFrame = Frame(root)
queryStringLabel = Label(queryFrame, text='Enter your search')
queryString = Entry(queryFrame, width=30, bd=2, textvariable=search, justify=CENTER)
queryConfirm = Button(queryFrame, text='Request', width=20)
queryInfo = Label(queryFrame, text='Request status:\n nothing requested', foreground='red')

queryFrame.pack()
queryStringLabel.pack()
queryString.pack()
queryInfo.pack()
queryConfirm.pack()

folderFrame = Frame(root)
folderSelect = Button(folderFrame, text='Сhoose a folder to save files')
folderSelectLabel = Label(folderFrame, text='By default is saved in \'./saved/\'', fg='grey')

folderFrame.pack()
folderSelect.pack()
folderSelectLabel.pack()

dirname = folderSelect.bind('<1>', choose_directory)
account = accountConfirm.bind('<1>', confirm_userdata)
track = queryConfirm.bind('<1>', make_request)

root.mainloop()
