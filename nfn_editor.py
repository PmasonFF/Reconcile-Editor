import os
from os.path import join
import csv
import argparse
import textwrap
import tkinter as tk
from tkinter import *
from datetime import datetime
from PIL import ImageGrab
import pandas as pd
from selenium.common import WebDriverException
from sqlalchemy import create_engine, update, MetaData, select, literal_column
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from panoptes_client import Panoptes, Subject

Panoptes.connect()

VERSION = '0.1.0'


def configure(canvas_):
    canvas_.configure(scrollregion=canvas_.bbox("all"))


def toggle_colour(k_, j_):
    widget = frame.grid_slaves(row=k_ + 1, column=j_ + 1)[0]
    if widget.config()['background'][-1] == "#b3ffb3":
        widget.config(bg="#FDFDF5", text='Select')
    else:
        widget.config(bg="#b3ffb3", text='X')


def confirm_selections():
    number = count_problems(selections)
    confirm = tk.Toplevel()
    confirm.geometry('500x250+' + str(int(.4 * full_width)) + '+' + str(int(.025 * full_width)))
    confirm.configure(bg='#F5F5F5')
    confirm.attributes('-topmost', True)
    text_problems = Text(confirm, height=1, font=('arial', 12, 'bold'), bd=1, bg="#F5F5F5")
    text_problems.tag_configure("center", justify='center')
    text_problems.insert(INSERT, 'The problem selections result in ' + str(number) + ' subjects to review', "center")
    text_problems.pack(pady=20)
    if number == 0:
        change_btn = Button(confirm, text='Change selections', height=2, width=20,
                            font=('arial', 10, 'bold'), bd=1, bg="#b3ffb3", relief='sunken',
                            command=confirm.destroy)
        change_btn.pack(pady=20)
    else:
        yes_btn = Button(confirm, text='Continue', height=2, width=20,
                         font=('arial', 10, 'bold'), bd=1, bg="#b3ffb3", relief='sunken',
                         command=lambda: [confirm.destroy(), choose.destroy()])
        yes_btn.pack(pady=20)
    no_btn = Button(confirm, text='Exit', height=2, width=20,
                    font=('arial', 10, 'bold'), bd=1, bg="#ff0000", relief='sunken',
                    command=lambda: [confirm.destroy(), choose.destroy(), quit()])
    no_btn.pack(pady=15)

def read_selections():
    global selections
    for k_ in range(0, len(match_level)):
        for j_ in range(0, len(columns)):
            widget = frame.grid_slaves(row=k_ + 1, column=j_ + 1)[0]
            if widget.config()['background'][-1] == "#b3ffb3":
                for snippet in match_snippet[k_]:
                    selections.append(stmt1.filter(literal_column(columns[j_] + 'Explanation').like(snippet)))
                    print(columns[j_] + 'Explanation', snippet)


def count_problems(selections_):
    # extract problem subjects based on selections made
    global problems
    problems = set()
    if selections_:
        for selection in selections_:
            with reconciled_engine.connect() as conn:
                for row in conn.execute(selection):
                    problems |= {str(row[0])}
    return len(problems)


def read_ed_mod():
    global modified, flag
    for m in range(2, len(columns) + 2):
        widget = frame_2.grid_slaves(row=1, column=m)[0]
        modified[m] += widget.edit_modified()
        if modified[m] > 1 and flag[m]:
            widget_expl = frame_2.grid_slaves(row=2, column=m)[0]
            widget_expl.config(state='normal')
            widget_expl.delete("1.0", "end")
            widget_expl.insert("1.0", 'Pending Modification by ' + user + ' ' + str(datetime.now())[0:19])
            widget_expl.config(state='disable')
            flag[m] = False
        widget.edit_modified(0)


def insert_in_row1(k_, j_):
    if df_flattened[main_header[j_]].iloc[k_]:
        new_text = df_flattened[main_header[j_]].iloc[k_]
    else:
        new_text = ''
    widget = frame_2.grid_slaves(row=1, column=j_)[0]
    widget.delete("1.0", "end")
    widget.insert("1.0", new_text)
    widget_expl = frame_2.grid_slaves(row=2, column=j_)[0]
    widget_expl.config(state='normal')
    widget_expl.delete("1.0", "end")
    widget_expl.insert("1.0", 'Pending Modification by ' + user + ' ' + str(datetime.now())[0:19])
    widget_expl.config(state='disable')


def restore():
    for j_ in range(2, len(columns) + 2):
        widget = frame_2.grid_slaves(row=1, column=j_)[0]
        widget.delete("1.0", "end")
        widget.insert(INSERT, row1txt[j_])
        widget.edit_modified(0)
        widget_expl = frame_2.grid_slaves(row=2, column=j_)[0]
        widget_expl.config(state='normal')
        widget_expl.delete("1.0", "end")
        widget_expl.insert("1.0", row2txt[main_header[j_]])
        widget_expl.config(state='disable')
        widget_expl.edit_modified(0)


def update_db():
    update_dict = {}
    for j_ in range(2, len(columns) + 2):
        widget = frame_2.grid_slaves(row=1, column=j_)[0]
        widget_expl = frame_2.grid_slaves(row=2, column=j_)[0]
        if widget.get(1.0, "end-1c") != str(row1txt[j_]) or widget_expl.get(1.0, "end-1c") != row2txt[main_header[j_]]:
            update_dict[main_header[j_]] = widget.get(1.0, "end-1c")
            update_dict[main_header[j_] + 'Explanation'] = 'Modified by ' + user + ' ' + str(datetime.now())[0:19]
    if update_dict:
        # print(update_dict)
        stmt = (update(reconciled_table).where(reconciled_table.c.subject_id == subject)
                .values(update_dict))
        connection.execute(stmt)


def quit_flag():
    global exit_flag
    edit.destroy()
    exit_flag = True


def get_image(zoo_id):
    subject_ = Subject(zoo_id)
    url = subject_.locations[0]['image/jpeg']
    return url


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    fromfile_prefix_chars='@',
    description=textwrap.dedent(""" 
        This script takes as inputs the reconciled-with-explanations and the flattened 
        unreconciled .csv files as produced by Notes from Nature's reconcile.py.

        In lieu of the unreconciled Notes from Nature file generated using the -u parameter, this 
        script can use any flattened .csv file with columns for subject_id, classification_id,
        and user_name plus additional columns that has been reconciled using reconcile.py
        (ie using the -f csv parameter with the reconciled columns defined using the -c parameters.)

        For both NfN and .csv files the unreconciled and reconciled with explanations 
        must be match - ie the reconciled file was generated from the unreconciled data.

        The script builds a Sqlite database which can then be edited by selecting various 
        problem types as normally presented in the Summary html format from reconcile.py.

        The first step is to define the input files using these parameters, along with 
        the browser that will be used to show the original subject.  At this time Chrome,
        and Firefox for Mac or Windows, and Edge for Windows are supported. 

        The script builds or locates the SQL database that is being or will be modified in 
        the current working directory (where the script is being run from).  

        Next a GUI is presented where the problem types for each reconciled field can be
        selected. Currently the problem types are limited to "No match, "One transcript",
        "Tie matches" (ie no clear majority), and 'Fuzzy" matches. Currently Exact unanimous
        and Exact or Normalized majority matches are not selectable in the GUI.

        However it is possible to define a problem listing in the parameters that overrides
        the GUI.  This listing can be any .csv formatted file with a column "subject_id"  
        (note no "s") which holds a list of subjects to edit. It is important all the subjects
        listed appear in both the reconciled and unreconciled input files and still exist in 
        zooniverse.

        The script opens a browser (independent of any other open browser on the system).
        To do this it needs a compatible browser installed on the system and a compatible 
        webdriver installed in the current working directory.  There is a utility script
        update_drivers.py which will obtain and install up-to-date webdrivers for the supported 
        browser types. This should be run once before using this script and again if updates
        to your browser cause it to throw an error when attempting to open the browser.

        The subjects to be edited are retrieved from Zooniverse using the panoptes client, 
        and shown in the browser under the editing GUI.

        The editing GUI itself is patterned after the NfN Summary html template - except the
        reconciled result is fully editable using cut paste and copy keyboard commands from 
        any field shown in the editor, direct character entry, deletion or replacement in the
        reconciled text block, or by simply selecting the best version of the actual
        transcriptions entered by the volunteers.

        There is a button to Restore the reconciled results back to the what they were the 
        last time they were modified and submitted (which may be their original version if no 
        changes have be Submitted).  There is another button to Submit the changes made and move
        on to the next subject, and finally a button to Submit the changes for the current subject
        and exit.  The Submit button makes the pending changes permanently in the database.  Changes 
        in the database carry a "Modified" flag and a date, time and the id of the reviewer that 
        made the change in place of the reconciled explanation.

        A number of Python packages must be installed for this script.  These are
        all common and well supported packages:
        tkinter - a very common GUI package fpr Python
        pandas - the same database package as used by reconcile.py
        selenium - interfaces with the web browser and webdrivers  
        sqlalchemy - provides SQL searching, selection, and database management
        panoptes_client - to interact with zooinverse to obtain the subject images

        NOTE: You may use a file to hold the
        command-line arguments like: @/path/to/args.txt."""))

parser.add_argument(
    '-u', '--username',
    help=textwrap.dedent("""An identifier for the reviewer making the changes. 
    It will be recorded with the modifications made. At this time there is no 
    verification or testing of credentials. """))

parser.add_argument(
    '-d', '--directory', default='',
    help=textwrap.dedent("""The path and directory where the unreconciled file,
    the reconciled file are located.  The databases will also be built there.
    example -d C:\py_scripts\Scripts_Reconcile . """))

parser.add_argument(
    '-f', '--flattened',
    help=textwrap.dedent("""The source file for the flattened unreconciled
    classifications """))

parser.add_argument(
    '-r', '--reconciled',
    help=textwrap.dedent("""The source file for the reconciled classifications
    with explanations as produced by reconcile.py --explanations."""))

parser.add_argument(
    '-p', '--problem_list', default=None,
    help=textwrap.dedent("""A optional csv file with a column "subject_id" 
    containing a list of zooniverse subject numbers to edit."""))

parser.add_argument(
    '-b', '--browser',
    help=textwrap.dedent("""Specify the browser to be used to show the subjects.
    This script supports Chrome, Edge, Safari and Firefox on recent Windows and
     Mac operating systems. Other browsers can be used with a slight modification
     """))

args = parser.parse_args()
user = args.username
directory = args.directory
prob_list = args.problem_list
flattened_file = args.flattened
browser_name = args.browser
flattened_database = flattened_file.partition('.')[0] + '.db'

flattened_engine = create_engine('sqlite:///' + join(directory, flattened_database))
if os.path.isfile(join(directory, flattened_database)):
    print('Found existing flattened database')
    pass
else:
    chunksize = 100000
    i = 1
    for df in pd.read_csv(join(directory, flattened_file), chunksize=chunksize, low_memory=False, iterator=True):
        df = df.rename(columns={c: c.replace(' ', '').replace('(', '').replace(')', '') for c in df.columns})
        df.index += i
        df.to_sql('flattened', flattened_engine, if_exists='append')
        i = df.index[-1] + 1
    print('Built flattened database')

reconciled_file = args.reconciled
reconciled_database = reconciled_file.partition('.')[0] + '.db'
reconciled_engine = create_engine('sqlite:///' + join(directory, reconciled_database))
if os.path.isfile(join(directory, reconciled_database)):
    print('Found existing reconciled database')
    pass
else:
    chunksize = 100000
    i = 1
    for df in pd.read_csv(join(directory, reconciled_file), chunksize=chunksize, low_memory=False, iterator=True):
        df = df.rename(columns={c: c.replace(' ', '').replace('(', '').replace(')', '') for c in df.columns})
        df.index += i
        df.to_sql('reconciled', reconciled_engine, if_exists='append')
        i = df.index[-1] + 1
    print('Built reconciled database')
connection = reconciled_engine.connect()
meta = MetaData(bind=reconciled_engine)
MetaData.reflect(meta)
reconciled_table = meta.tables['reconciled']

stmt1 = select(literal_column('subject_id FROM reconciled'))
subject = str(connection.execute(stmt1).fetchone()[0])

# get headers
df_flattened = pd.read_sql_query('SELECT * FROM "flattened" where subject_id = ' + subject,
                                 flattened_engine)
df_reconciled = pd.read_sql_query('SELECT * FROM "reconciled" where subject_id =  ' + subject,
                                  reconciled_engine)

columns = []
for field in df_flattened.keys():
    if field in df_reconciled.keys() and field + 'Explanation' in df_reconciled.keys():
        columns.append(field)

main_header = ['subject_id', 'user_name']
main_header.extend(columns)
existing_columns = main_header[:]
existing_columns.extend(['index', 'classification_id'])
for column in df_flattened.keys():
    if column in existing_columns:
        continue
    main_header.append(column)

match_snippet = {0: ['%No text%', '%No select%'], 1: ['%Only 1%', '%was 1 number%'], 2: ['%tie%'], 3: ['%ratio%']}

# messy but cross-platform/monitor set-up  means of getting the current display width
img = ImageGrab.grab()
full_width = img.size[0]
img.close()

if prob_list:  # use file with a list of subjects to determine subjects to edit
    if os.path.isfile(join(directory, prob_list)):
        with open(join(directory, prob_list)) as lists_file:
            lists = csv.DictReader(lists_file)
            problems = []
            for list_line in lists:
                problems.append(list_line['subject_id'])
    else:
        print('Problem file indicated but not found. Verify file exists in working directory with this script.')
        quit()

else:  # build gui to get the selections here
    selections = []
    match_level = ['No_match', 'One_transcript', 'Majority_ties', 'Fuzzy_match']
    choose = tk.Tk()
    choose.geometry(str(int(.95 * full_width)) + 'x' + str(int(full_width / 4)) + '+'
                    + str(int(.025 * full_width)) + '+' + str(int(.025 * full_width)))
    choose.title('Select Problems to choose')
    canvas = Canvas(choose, borderwidth=0)
    frame = Frame(canvas)
    hsb = Scrollbar(choose, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=hsb.set)
    hsb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    frame.bind("<Configure>", lambda event, canvas_=canvas: configure(canvas))

    # row 1
    for j in range(0, len(columns)):
        Label(frame, text=columns[j], width=20, wraplength=int(full_width / 12), font=('arial', 10, 'bold')) \
            .grid(row=0, column=j + 1, sticky='w')
        frame.grid_columnconfigure(j, weight=1)

    # column 1
    Label(frame, text='Match_level', width=15, font=('arial', 10, 'bold')).grid(row=0, column=0, sticky='nw')
    for j in range(0, len(match_level)):
        match_label = Label(frame, text=match_level[j], width=15, height=2, font=('arial', 10, 'bold'))
        match_label.grid(row=j + 1, column=0, padx=1, pady=5, sticky='new')
        match_label.grid_columnconfigure(0, weight=1)

    # add Submit button
    submit_btn = Button(canvas, text='Submit', height=5, width=20, justify=CENTER,
                        font=('arial', 10, 'bold'), bd=1, bg="#b3ffb3", relief='sunken',
                        command=lambda: [read_selections(), confirm_selections()])
    submit_btn.place(relx=.4, rely=.75)

    # arrange grid of buttons
    btn = [[0 for k in range(0, len(match_level))] for j in range(0, len(columns))]
    for k in range(0, len(match_level)):
        for j in range(0, len(columns)):
            btn[j][k] = Button(frame, text='Select', height=2, width=20, justify=CENTER, font='TkFixedFont',
                               bd=1, bg='#FDFDF5', relief='sunken',
                               command=lambda k1=k, j1=j: toggle_colour(k1, j1)) \
                .grid(row=k + 1, column=j + 1, sticky='new', padx=1, pady=5)

    frame.bind("<Configure>", lambda event, canvas_=canvas: configure(canvas))

    # choose.attributes('-topmost', True)
    choose.mainloop()

# select and open browser
browser = ''
try:
    if browser_name.lower() == 'chrome':
        browser = webdriver.Chrome()
    elif browser_name.lower() == 'edge':
        browser = webdriver.Edge()
    elif browser_name.lower() == 'firefox':
        opts = Options()
        opts.log.level = "fatal"
        browser = webdriver.Firefox(options=opts)
        # browser.maximize_window()
    else:
        print('The browser specified in the parameters ', browser_name, 'is not in the list of supported browsers:')
        print('Supported browsers: Chrome, Edge, Firefox')
except WebDriverException:
    print('Drivers for you browser version were not found. Ensure your browser is up to date, and ')
    print('try running update_drivers.py to update your webdriver. If you see permission denied')
    print('errors, you may have to sign out and back in to before running update_drivers.py ')
    quit()

# loop through problems
exit_flag = False
for subject in sorted(list(problems)):
    if exit_flag:
        break
    max_str_row1 = 8
    row1txt = [subject, '']
    row2txt = {}
    try:
        browser.get(get_image(subject))
        df_flattened = pd.read_sql_query('SELECT * FROM "flattened" where subject_id = ' + subject,
                                         flattened_engine)
        df_reconciled = pd.read_sql_query('SELECT * FROM "reconciled" where subject_id =  ' + subject,
                                          reconciled_engine)
        modified = [0 for a in main_header]
        flag = [True for a in main_header]
        for i in range(2, len(columns) + 2):
            row2txt[main_header[i]] = df_reconciled[main_header[i] + 'Explanation'].iloc[0]
            try:
                txt1 = df_reconciled[main_header[i]].iloc[0]
                if txt1:
                    max_str_row1 = max(max_str_row1, len(str(txt1)))
                else:
                    txt1 = ''
            except KeyError:
                txt1 = ''
            row1txt.append(txt1)

    except KeyError:
        print('An error occurred while processing subject ', subject,
              'Verify this subject exits in zooniverse and the input files.')
        print('If working from a problem listing, this subject and below '
              'in that listing will not have been processed.')
        #  browser.quit()
        quit()

    # build GUI for editor
    height = int(max_str_row1 / 20) + 1
    edit = tk.Tk()
    edit.focus()
    edit.geometry(str(int(.95 * full_width)) + 'x' + str(int(full_width / 3)) + '+'
                  + str(int(.025 * full_width)) + '+' + str(int(.025 * full_width)))
    canvas_2 = Canvas(edit, borderwidth=0)
    frame_2 = Frame(canvas_2)
    vsb_2 = Scrollbar(edit, orient="vertical", command=canvas_2.yview)
    hsb_2 = Scrollbar(edit, orient="horizontal", command=canvas_2.xview)
    canvas_2.configure(yscrollcommand=vsb_2.set)
    canvas_2.configure(xscrollcommand=hsb_2.set)
    vsb_2.pack(side="right", fill="y")
    hsb_2.pack(side="bottom", fill="x")
    canvas_2.pack(side="left", fill="both", expand=True)
    canvas_2.create_window((0, 0), window=frame_2, anchor="nw")

    frame_2.bind("<Configure>", lambda event, canvas_=canvas_2: configure(canvas_2))

    # row 0
    for j in range(0, len(main_header)):
        Label(frame_2, text=main_header[j], wraplength=int(full_width / 12),
              font=('arial', 10, 'bold')).grid(row=0, column=j, sticky='w')
        frame_2.grid_columnconfigure(j, weight=1)

    # row 1
    Label(frame_2, text=row1txt[0], font=('arial', 12, 'bold')).grid(row=1, sticky='nw')
    for j in range(2, len(columns) + 2):
        if row2txt[main_header[j]].find('No text match') >= 0 or row2txt[main_header[j]].find('Only 1') >= 0:
            bg = 'light pink'
        else:
            bg = 'white'
        text_enter = Text(frame_2, wrap='word', width=20, height=height, bg=bg)
        text_enter.insert(INSERT, row1txt[j])
        text_enter.grid(row=1, column=j, padx=1, pady=1, sticky='new')
        text_enter.grid_columnconfigure(j, weight=1)
        text_enter.bind('<<Modified>>', lambda event: read_ed_mod())

    # row 2
    for j in range(2, len(columns) + 2):
        text_expl = Text(frame_2, wrap='word', width=20, height=3, bg="light grey")
        text_expl.insert(INSERT, row2txt[main_header[j]])
        text_expl.config(state='disable')
        text_expl.grid(row=2, column=j, padx=1, pady=1, sticky='new')
        text_expl.grid_columnconfigure(j, weight=1)

    # row 3+ for unreconciled rows
    btn = [[0 for k in range(0, len(df_flattened.index))] for j in range(0, len(main_header))]
    for k in range(0, len(df_flattened.index)):
        for j in range(1, len(main_header)):
            text_flattened = Text(frame_2, wrap='word', width=20, height=height, state='normal', bg="#b3ffb3")
            if df_flattened[main_header[j]].iloc[k]:
                text_flattened.insert(INSERT, df_flattened[main_header[j]].iloc[k])
            else:
                text_flattened.insert(INSERT, '')
            text_flattened.config(state='disable')
            text_flattened.grid(row=3 + 3 * k, column=j, pady=1, sticky='new')
            if j > 1:
                btn[j][k] = Button(frame_2, text='Select', height=1, width=20, justify=CENTER, font='TkFixedFont',
                                   bd=1, bg='white', relief='sunken',
                                   command=lambda k1=k, j1=j: insert_in_row1(k1, j1)) \
                    .grid(row=4 + 3 * k, column=j, sticky='new', padx=1)

            Label(frame_2, text='     ', height=1).grid(column=j, row=5 + 3 * k)
        Label(frame_2, text='     ', height=1).grid(column=0, row=26 + 3 * k)
    # add restore button
    restore_btn = Button(canvas_2, text='Restore original', height=3, width=20,
                         justify=CENTER, font=('arial', 10, 'bold'),
                         bd=1, bg='#FDFDF5', relief='sunken', command=restore)
    restore_btn.place(relx=.2, rely=.90)

    # add load next button
    next_btn = Button(canvas_2, text='Submit and Load next', height=3, width=20, justify=CENTER,
                      font=('arial', 10, 'bold'), bd=1, bg='#FFFFEB', relief='sunken',
                      command=lambda: [update_db(), edit.destroy()])
    next_btn.place(relx=.4, rely=.90)

    # add quit button
    quit_btn = Button(canvas_2, text='Submit and Exit', height=3, width=20, justify=CENTER, font=('arial', 10, 'bold'),
                      bd=1, bg='#FFFFC0', relief='sunken',
                      command=lambda: [update_db(), quit_flag()])
    quit_btn.place(relx=.6, rely=.90)

    edit.mainloop()

browser.quit()

if os.path.isfile('geckodriver.log'):
    os.remove('geckodriver.log')
quit()
