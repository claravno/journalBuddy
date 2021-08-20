import calendar

from dbJournalBuddy import *
from tgMsgTools import DataList

global users, habits, tasks, msg_id, garbage, new_entry
users = {}
# habits = {}
tasks = {}
msg_id = {}
garbage = []



def who(id, client, name):
    """Register and welcome a new user"""
    exists = person.locate(id)

    if not exists:
        person.create(id, name)
        client.send_message(id, 'Hello ' + name + '''!
I am your Journal Buddy :) My purpose is to help you manage your productivity!

You can:
    - Set up habits
    - Schedule events
    - Create a task pool
    - Set reminders
    - Add notes - tell me things you don’t want to forget! May it be a quote, or a movie you liked

Every month we can choose which tasks you would like to complete in the month ahead!
Every week I will help you set goals in terms of tasks and habits for the week ahead!

The more we get to know each other the more I will be able to help! Providing weekly analytics and suggestions for future performance. Tell me how you feel throughout your tasks, habits and events and I will share with you what I think will work best.

Type /setup to begin!''')

        users[id] = {"last": "new user"}
    elif not (users.keys().__contains__(id)):
        users[id] = {"last": "welcome back"}



def display_entries(chat_id, entry_type):
    """Process reply to allow users to complete habits"""

    reply = ''
    count = 0

    if entry_type == "habits":
        items = habit.return_all(chat_id)[0]
    elif entry_type == "categories":
        items = category.return_all(chat_id)

    # print(items)
    #
    # try:
    #     for x in items:
    #         name = items[count][0]
    #         reply += '/' + str(count + 1) + ' ' + name + '\n'
    #         count = count + 1
    # except:
    #     reply = 'You have no entries'

    return items


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def entry_names(id, message_text):
    """Process task set up message"""

    items = []

    if (new_entry.keys()).__contains__(id):
        items = new_entry[id].get(id) + [message_text]
        print(items)
        new_entry[id]["names"] = items
    else:
        items.append(message_text)
        new_entry[id]["names"] = items

    print("items >> ", items)


def str_to_date(date_str):
    """Converts string date to date date"""

    if date_str == 'today':
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    return date


