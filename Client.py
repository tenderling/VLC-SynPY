import socket
import threading
import requests
from requests.auth import HTTPBasicAuth
from tkinter import *
import tkinter.simpledialog
import time
import winreg
from PIL import Image, ImageTk


psw = '1234'
stop_thread = False

REG_PATH = 'SOFTWARE\VLCsynPY'
def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False
def get_reg(name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return ''

def plps():
    sock.sendto('plps'.encode('utf-8'), server)

def time_set(h,m,s):
    time = '{}H:{}M:{}s'.format(h,m,s)
    print(time)
    sock.sendto(('seek '+time).encode('utf-8'), server)

def exit():
    stop_thread = True
    window.destroy()
    print(thread.is_alive())


def InfoCheck():
    while not stop_thread:
        time.sleep(1)
        xml = requests.get('http://127.0.0.1:8080/requests/status.xml', auth=HTTPBasicAuth('',psw)).text
        filename = re.findall("<info name='filename'>(.*?)</info>", xml)
        title = re.findall("<info name='title'>(.*?)</info>", xml)
        timeSEC = re.findall("<time>(.*?)</time>", xml)
        
        
        if len(title) == 0 and len(filename) == 0:
            playing.set('')
        elif len(title) == 0:
            playing.set(filename[0][:30]) 
        else:
            playing.set(title[0][:30])
        
        timer.set(time.strftime('%H:%M:%S', time.gmtime(int(timeSEC[0]))))
        



def limitTimeSize(*args):
    H = HValue.get()
    M = MValue.get()
    S = SValue.get()
    if len(H) >= 2: 
        HValue.set(H[:2])
        timeM.focus()
    if len(M) >= 2: 
        MValue.set(M[:2])
        timeS.focus()
    if len(S) > 2: SValue.set(S[:2])


lastClickX = 0
lastClickY = 0
def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + window.winfo_x(), event.y - lastClickY + window.winfo_y()
    if abs((event.x-Trans.coords()[0])) > 10 and abs((event.y-Trans.coords()[1])) > 10:
        window.geometry("+%s+%s" % (x , y))

def do_popup(event):
    try:
        RCmenu.tk_popup(event.x_root, event.y_root)
    finally:
        RCmenu.grab_release()

OnTopCheck = True

ip = get_reg('LastIp')
class MyDialog(tkinter.simpledialog.Dialog):

    def body(self, master):

        Label(master, text="IP:").grid(row=0)

        self.e1 = Entry(master)
        self.e1.insert(0, ip)
        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

    def apply(self):
        global server
        set_reg('LastIp', self.e1.get())
        server = self.e1.get(), 9090



def OnTopRCswitch():
    global OnTopCheck
    if OnTopCheck == True:
        OnTopCheck = False
        window.attributes('-topmost', OnTopCheck)
    elif not OnTopCheck: 
        OnTopCheck = True
        window.attributes('-topmost', OnTopCheck)


def read_sock():
    while 1 :
        data = sock.recv(1024)
        enc=data.decode('utf-8')
        global stop_thread
        if stop_thread:
            break
        if enc == 'plps': requests.get('http://127.0.0.1:8080/requests/status.xml?command=pl_pause', auth=HTTPBasicAuth('',psw))
        elif enc.startswith('seek'): 
            print(enc)
            requests.get('http://127.0.0.1:8080/requests/status.xml?command=seek&val='+enc.replace('seek ', ''), auth=HTTPBasicAuth('',psw))


server = ip, 9090  # Данные сервера

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(('', 0)) # Задаем сокет как клиент

thread = threading.Thread(target=read_sock, daemon = True)
InfoChecker = threading.Thread(target=InfoCheck, daemon = True)
InfoChecker.start()
thread.start()


window = Tk()
window.title("VLC syn.py")
window.geometry('450x200+500+300')
window.overrideredirect(1)
background_image = PhotoImage(file='./Background.png')
background_label = Label(window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


window.attributes('-alpha', 1.0)
window.attributes('-topmost', OnTopCheck)

window.bind('<Button-1>', SaveLastClickPos)
window.bind('<B1-Motion>', Dragging)
window.bind("<Button-3>", do_popup)


PlayImg = PhotoImage(file ='Play.png')
PlayPause = Button(window, text="Play/Pause",borderwidth=0, relief='flat', highlightthickness = 0, bd = -2, bg = '#203b8b',image=PlayImg, command = plps)
PlayPause.place(x=20, y=30)

TimeImg = PhotoImage(file ='Time.png')
Time_set = Button(window, text="Set time",borderwidth=0, relief='flat', highlightthickness = 0, bd = -2, bg = '#203b8b',image=TimeImg, command = lambda:time_set(HValue.get(),MValue.get(),SValue.get()))
Time_set.place(x=20, y=80)

closeimg = PhotoImage(file ='Close.png')
close = Button(window, text = "Close Window",borderwidth=0, relief='flat', highlightthickness = 0, bd = -2, bg = '#203b8b', image=closeimg, command = exit)
close.place(x=20, y=130)

debug = Button(window, text = "debug", command = lambda: print(timer))
# debug.place(x=130, y=190)

HValue = StringVar()
MValue = StringVar() 
SValue = StringVar()
HValue.trace('w', limitTimeSize)
MValue.trace('w', limitTimeSize)
SValue.trace('w', limitTimeSize)
timeH = Entry(width=2, textvariable=HValue)
timeH.place(x=130, y=90)
timeH.select_range(0,'end')
timeM = Entry(width=2, textvariable=MValue)
timeM.place(x=155, y=90)
timeM.select_range(0,'end')
timeS = Entry(width=2, textvariable=SValue)
timeS.place(x=180, y=90)
timeS.select_range(0,'end')

timer = StringVar()
playing = StringVar()
CurTime = Label(window, textvariable=timer, bg = '#203b8b', fg = 'white')
CurTime.place(x=230, y=90)
CurPlaying = Label(window, textvariable=playing, bg = '#203b8b', fg = 'white')
CurPlaying.place(x=230, y=120)


RCmenu = Menu(window, tearoff=0,)
RCmenu.add_command(label="Always on top", command=lambda: OnTopRCswitch())
RCmenu.add_command(label="Enter IP",  command=lambda: MyDialog(window))
RCmenu.add_command(label="Info Checker",  command=lambda: InfoChecker.start())

Trans = Scale(window, from_=0.1, to=1.0,resolution=0.01, orient=HORIZONTAL, borderwidth=0.1, showvalue=0,sliderlength=15,troughcolor='Dark Blue',width=10, command = lambda event: window.attributes('-alpha', Trans.get()))
Trans.set(1.0)
Trans.place(x=300, y=50)

window.mainloop()