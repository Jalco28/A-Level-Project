from datetime import date, timedelta
import json
import requests
from functools import partial
from tkinter import ttk
import tkinter as tk
SCHOOL_MODE = False


if SCHOOL_MODE:
    url = "http://10.50.10.254:4100/wbo"
    payload = {"redirect": "http://140.238.101.107/",
               "helper": "Default-WebBlocker",
               "action": "warn",
               "url": "140.238.101.107"}
    requests.post(url, data=payload, verify=False)

ROOT_WIDTH, ROOT_HEIGHT = int(1920*0.9), int(1080*0.9)


class Row(tk.Frame):
    def __init__(self, root, data, position, top_row=False):
        super().__init__(root)
        self.data = data
        self.frames = [
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self, bg='white', highlightbackground='black',
                     highlightthickness=1),
            tk.Frame(self)
        ]
        self.widgets = [
            tk.Label(self.frames[0], bg='white', text=str(position)),
            tk.Label(self.frames[1], bg='white', text=data['username']),
            tk.Label(self.frames[2], bg='white', text=data['actual_user']),
            tk.Label(self.frames[3], bg='white', text=data['score']),
            tk.Label(self.frames[4], bg='white', text=data['difficulty']),
            tk.Label(self.frames[5], bg='white', text=data['date'])
        ]
        if not top_row:
            self.widgets.append(tk.Button(
                self.frames[6], text='Delete all instances of username', command=partial(delete_name, data['username'])))
        for i in range(7):
            self.columnconfigure(i, minsize=(ROOT_WIDTH-10)/7)
            try:
                self.widgets[i].pack()
            except IndexError:  # Top row
                pass
            self.frames[i].grid(row=0, column=i, sticky='ew')


def delete_name(name):
    data = {'username': name}
    requests.post('http://140.238.101.107/doorsos/delete.php', data=data)
    setup_rows()


def download_data():
    r = requests.get('http://140.238.101.107/doorsos/read.php')
    return json.loads(r.text)


def setup_rows(*args):
    for widget in inner_frame.winfo_children():
        widget.destroy()
    all_data = download_data()
    filtered_data = [data for data in all_data if matches_filters(data)]
    filtered_data.sort(key=lambda x: x['score'], reverse=True)

    rows = [Row(inner_frame, {'username': 'Submitted Username',
                              'actual_user': 'Actual User',
                              'score': 'Score',
                              'difficulty': 'Difficulty',
                              'date': 'Date'}, 'Position', top_row=True)]
    for i, data in enumerate(filtered_data):
        rows.append(Row(inner_frame, data, i+1))
    for row in rows:
        row.pack()


def matches_filters(data):
    difficulty = difficulty_strvar.get()
    time_period = time_strvar.get()

    if data['difficulty'] != difficulty and difficulty != 'All':
        return False
    date_achieved = data['date'].split('-')
    date_achieved = date(int(date_achieved[2]), int(
        date_achieved[1]), int(date_achieved[0]))

    if time_period == 'Past day':
        delta = timedelta(days=1)
    elif time_period == 'Past week':
        delta = timedelta(days=7)
    elif time_period == 'Past month':
        delta = timedelta(days=30)
    elif time_period == 'Past year':
        delta = timedelta(days=365)
    elif time_period == 'All time':
        delta = 'ALL'
    else:
        raise ValueError('Unknown date filter')

    if delta != 'ALL':
        target_date = date.today()-delta
        if date_achieved < target_date:
            return False

    return True


root = tk.Tk()
root.title('DoorsOS Companion App')
root.geometry(f'{ROOT_WIDTH}x{ROOT_HEIGHT}')

top_frame = tk.Frame(root)
for i in range(4):
    top_frame.columnconfigure(i, minsize=ROOT_WIDTH/4)
time_label = tk.Label(top_frame, text='Time Period:')
time_label.grid(row=0, column=0, sticky='E')
time_strvar = tk.StringVar(top_frame)
times = ['Past day',
         'Past week',
         'Past month',
         'Past year',
         'All time']
time_dropdown = ttk.OptionMenu(
    top_frame, time_strvar, times[-1], *times, command=setup_rows)
time_dropdown.grid(row=0, column=1, sticky='W')

difficulty_label = tk.Label(top_frame, text='Time Period:')
difficulty_label.grid(row=0, column=2, sticky='E')
difficulty_strvar = tk.StringVar(top_frame)
difficulties = ['All',
                'GCSE',
                'A-Level']
difficulty_dropdown = ttk.OptionMenu(
    top_frame, difficulty_strvar, difficulties[0], *difficulties, command=setup_rows)
difficulty_dropdown.grid(row=0, column=3, sticky='W')

top_frame.pack(side='top')

bottom_frame = tk.Frame(root, width=ROOT_WIDTH)
leaderboard_canvas = tk.Canvas(bottom_frame)
leaderboard_canvas.pack(side='left', fill='both', expand=1)

scrollbar = tk.Scrollbar(bottom_frame, command=leaderboard_canvas.yview)
scrollbar.pack(side='right', fill='y')

leaderboard_canvas.configure(yscrollcommand=scrollbar.set)
leaderboard_canvas.bind('<Configure>', lambda x: leaderboard_canvas.configure(
    scrollregion=leaderboard_canvas.bbox("all")))

inner_frame = tk.Frame(leaderboard_canvas)
leaderboard_canvas.create_window((0, 0), window=inner_frame, anchor="nw")


setup_rows()

bottom_frame.pack(side='bottom', fill='both', expand=1)
root.mainloop()
