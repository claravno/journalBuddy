from dbJournalBuddy import *
from jbTools import *



# def get_reply(chat_id, sheet, date):
#     """Get's the list of tasks for the sheet stated in users[id]["last"]"""
#
#     if sheet == 'daily':
#         items = task.get_daily(chat_id, date)
#
#     elif sheet == 'weekly':
#         date = task.correct_date(date, 'W')
#         items = task.get_weekly(chat_id, date)
#
#     elif sheet == 'monthly':
#         date = task.correct_date(date, 'M')
#         items = id, task.get_monthly(chat_id, date)
#
#     elif sheet == "pool":
#         items = task.get_pool(chat_id, date)
#
#     # using command number to calculate task index in list by id
#     index = int(users[id]["activity"]["command"].strip('/')) - 1
#
#     # activity id saved
#     users[id]["activity"]["id"] = items[index][0]
#
#     # Name of task clicked
#     reply = task.locate_by_id(items[index])[0][0]
#
#     return reply


def task_names(id, message_text):
    """Process task set up message"""

    items = []

    if (tasks.keys()).__contains__(id):
        items = tasks.get(id) + [message_text]
        tasks[id] = items
    else:
        items.append(message_text)
        tasks[id] = items


def new_tasks1(id):
    """Temporary to create new tasks"""

    date_precision = get_date_precision(users[id]["sheet"])
    date = datetime.datetime.strptime(users[id]["date"], "%Y-%m-%d").date()

    # using task dictionary to be replaced by universal
    for x in tasks.get(id):
        task_id = task.create(id, x)
        task.schedule(task_id, 1, date, date_precision)
    tasks.pop(id)


# def new_tasks(id):
#     """Add new tasks to a specific task sheet"""
#
#     date = datetime.date.today()
#
#     if users[id]["sheet"] == 'daily':
#         date_precision = 'D'
#     elif users[id]["sheet"] == 'weekly':
#         date_precision = 'W'
#     elif users[id]["sheet"] == 'monthly':
#         date_precision = 'M'
#     elif users[id]["sheet"] == 'pool':
#         date_precision = 'T'
#
#     for x in tasks.get(id):
#         task_id = task.create(id, x)
#         task.schedule(task_id, 1, date, date_precision, id)
#     tasks.pop(id)
#     users[id]["last"] = "tasks_added"


def get_date_precision(sheet):

    if sheet == 'daily':
        date_precision = 'D'
    elif sheet == 'weekly':
        date_precision = 'W'
    elif sheet == 'monthly':
        date_precision = 'M'
    elif sheet == 'pool':
        date_precision = 'T'

    return date_precision


def update_tasks(app, id):
    """Removes unecessary messages and updates task sheet"""

    for x in garbage:
        app.delete_messages(id, x)





