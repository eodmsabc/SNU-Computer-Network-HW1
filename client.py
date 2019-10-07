import socket
import threading
import tkinter
import tkinter.font
from mysocket import *

# Connection Information
HOST = '127.0.0.1'
PORT = 20395
window = tkinter.Tk()
server = None
userid = None
role = None
board = None
myTurn = False
second_select = False
cheat = 0
cheat_exist = False
bingobutton = [[None for i in range(5)] for j in range(5)]
winnerlabel = [None for i in range(5)]
culprit = 0
copartner = 1

# Multithread gameplay class
class GP(threading.Thread):
    def __init__(self, tkwindow):
        self.root = tkwindow
        threading.Thread.__init__(self)

    def run(self):
        global window, server, role, userid
        global bingobutton, board, cheat, winnerlabel
        global myTurn, second_select, cheat_exist
        global culprit, copartner

        while True:
            read = read_from(server)
            header = read["type"]
            data = read["data"]

            if header == 'S':
                statuslabel.config(text="Status: In Game")
                board = parse_board(data)
                board_render()

            # Finished with winner
            elif header == 'W':
                winner = data
                for i in range(5):
                    for j in range(5):
                        bingobutton[i][j].destroy()
                statuslabel.config(text="Status: Finished")
                winnum = len(winner)
                for i in range(winnum):
                    winnerlabel[i].config(text=('Winner: ' + winner[i]))
                    winnerlabel[i].place(x=100,y=100+i*30)
                print('Finished')
                break   # Thread terminate
            
            # Update Board
            elif header == 'U':
                board = parse_board(data)
                board_render()

            # My Turn
            elif header == 'T':
                myTurnlabel.config(text="My Turn! Select Number")
                myTurnlabel.place(x=150, y=400)

                if role == culprit:
                    board = parse_board(data)
                else:
                    cheat = int(data[0])
                    check_cheat_exist()
                    cheatlabel.config(text=("Cheat: " + data[0]))
                    cheatlabel.place(x=50, y=400)
                    board = parse_board(data[1:])                    
                myTurn = True
                board_render()

            # Wrong behavior of copartner, Rejected from server
            elif header == 'R':
                myTurn = True

            else:
                print('Server Disconnected')
                break   # Thread terminate

gp = GP(window)

def parse_board(ins):
    return [[int(ins[i * 5 + j]) for j in range(5)] for i in range(5)]

def check_cheat_exist():
    global board, cheat, cheat_exist
    cheat_exist = False
    if cheat == 0:
        return
    for i in range(5):
        for j in range(5):
            if board[i][j] == cheat:
                cheat_exist = True
                break
        if cheat_exist:
            break

def buttonstate(i, j):
    global window, server, role, userid
    global bingobutton, board, cheat
    global myTurn, second_select, cheat_exist
    global culprit, copartner
    if not myTurn:
        return 'disabled'
    if role == culprit:
        if board[i][j] > 0:
            return 'normal'
        else:
            return 'disabled'
    else:
        if not cheat_exist:
            if board[i][j] > 0:
                return 'normal'
            else:
                return 'disabled'
        if board[i][j] == cheat:
            return 'normal'
        else:
            return 'disabled'

def board_render():
    global window, server, role, userid
    global bingobutton, board, cheat
    global myTurn, second_select, cheat_exist
    global culprit, copartner

    for i in range(5):
        for j in range(5):
            st = buttonstate(i, j)
            color = color = 'SystemButtonFace' if board[i][j] > 0 else 'red'
            bingobutton[i][j].config(text=board[i][j] if board[i][j] > 0 else -board[i][j])
            bingobutton[i][j].config(bg=color)
            bingobutton[i][j].config(state=st)
            bingobutton[i][j].place(x=50 + j * 60, y=60 + i * 60)

def after_login(event):
    global window, server, role, userid
    global bingobutton, board, cheat
    global myTurn, second_select, cheat_exist
    global culprit, copartner
    uid = login_entry.get()
    if not uid:
        return
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
    send_to(server, 'I', uid)
    read = read_from(server)
    if read["type"] == 'P':
        role = int(read["data"][0])
        userid = uid
        login_title.destroy()
        login_entry.destroy()
        login_info.destroy()
        usernamelabel.config(text=("Username: " + userid))
        usernamelabel.place(x=0,y=0)
        rolelabel.config(text=("Role: " + ("Main Culprit" if role == 0 else "Copartner")))
        rolelabel.place(x=250,y=0)
        statuslabel.config(text="Status: Waiting...")
        statuslabel.place(x=0, y=20)

        # GP thread start
        gp.start()

    else:
        login_info.config(text="Duplicate ID exists. Rejected from server.")
        login_info.place(x=100,y=180)
        server.close()

def bingobutton_handler(i, j):
    global window, server, role, userid
    global bingobutton, board, cheat
    global myTurn, second_select
    global culprit, copartner
    if not myTurn:
        print('Not My Turn')
        return

    if role == culprit:
        # Select Number
        if not second_select:
            sel = str(board[i][j])
            send_to(server, 'N', sel)
            myTurnlabel.config(text="My Turn! Select Cheat Number")
            myTurnlabel.place(x=150, y=400)
            second_select = True
        # Select Cheat
        else:
            sel = str(board[i][j])
            send_to(server, 'C', sel)
            myTurnlabel.place_forget()
            myTurn = False
            second_select = False
    else:
        sel = str(board[i][j])
        send_to(server, 'N', sel)
        myTurnlabel.place_forget()
        cheatlabel.place_forget()
        myTurn = False

def button_handler_gen(i, j):
    return lambda:bingobutton_handler(i,j)

window.title("Bingo Client")
window.geometry("400x450")
window.resizable(False, False)
bold=tkinter.font.Font(size=15, weight="bold")
    
login_title = tkinter.Label(window, text="Enter Username", font=bold)
login_title.place(x=100, y=120)
login_validation = window.register(lambda x: x!=' ')
login_entry = tkinter.Entry(window, validate="key", validatecommand=(login_validation, '%S'))
login_entry.bind("<Return>", after_login)
login_entry.place(x=100, y=150)
login_info = tkinter.Label(window, text="")

usernamelabel = tkinter.Label(window, text="")
rolelabel = tkinter.Label(window, text="")
statuslabel = tkinter.Label(window, text="")
cheatlabel = tkinter.Label(window, text="")
myTurnlabel = tkinter.Label(window, text="")

for i in range(5):
    winnerlabel[i] = tkinter.Label(window, text="")
    for j in range(5):
        bingobutton[i][j] = tkinter.Button(window, overrelief="solid", width=6, height=3, command=button_handler_gen(i, j))

window.mainloop()
