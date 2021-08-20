import dbJournalBuddy
import tgLog
from jbTasks import *
from tgMsgTools import *


def all_tasks(app, chat_id, event_info):
    """Display task options"""

    today = datetime.date.today()
    today_str = None

    if 'action_data' in event_info:
        message_id = event_info['message_id']
        date = event_info['action_data']['date']
        date_precision = event_info['action_data']['date_precision']
    else:
        message_id = None
        date = today
        date_precision = 'D'
    fields, prev_date, date, next_date = which_sheet4(event_info['user_id'], date_precision, date)

    msg = SappoGramMsg(app, chat_id, message_id, action=task_actions)

    # TOO MANY REPEATED BUTTONS: CAN THEY BE VARIABLES?
    if date_precision == 'D':

        day_name = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

        today_str = get_day_abv(date) + ' ' + str(date.year) + ' - '
        prev_date_str = day_name[prev_date.weekday()] + ' ' + prev_date.strftime("%d")
        next_date_str = day_name[next_date.weekday()] + ' ' + next_date.strftime("%d")

        msg.button_add("<< " + prev_date_str, action=all_tasks,
                       action_data={'date_precision': date_precision, 'date': prev_date})
        if date != today:
            msg.button_add("Today", action=all_tasks, keep_together=True,
                           action_data={'date_precision': date_precision, 'date': today})
        msg.button_add(next_date_str + " >>", action=all_tasks, keep_together=True,
                       action_data={'date_precision': date_precision, 'date': next_date})

        msg.button_add("➕ Create New", action=setup_tasks,
                       action_data={'date_precision': date_precision,
                                    'date': date})

        msg.button_add("Weekly", action=all_tasks,
                       action_data={'date_precision': 'W', 'date': today})
        msg.button_add("Monthly", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'M', 'date': today})
        msg.button_add("Pool", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'T', 'date': today})

    elif date_precision == 'W':
        today_str = date.strftime("%d/%m") + " Weekly Task Sheet - "

        prev_date_str = prev_date.strftime("%d/%m")
        next_date_str = next_date.strftime("%d/%m")
        start_of_week = datetime.date.today() - datetime.timedelta(days=today.weekday())

        msg.button_add("<< " + prev_date_str, action=all_tasks,
                       action_data={'date_precision': date_precision, 'date': prev_date})
        if date != start_of_week:
            msg.button_add("This Week", action=all_tasks, keep_together=True,
                           action_data={'date_precision': date_precision, 'date': today})

        msg.button_add(next_date_str + " >>", action=all_tasks, keep_together=True,
                       action_data={'date_precision': date_precision, 'date': next_date})

        msg.button_add("➕ Create New", action=setup_tasks,
                       action_data={'date_precision': date_precision,
                                    'date':  date})

        msg.button_add("Daily", action=all_tasks,
                       action_data={'date_precision': 'D', 'date': today})
        msg.button_add("Monthly", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'M', 'date': today})
        msg.button_add("Pool", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'T', 'date': today})

    elif date_precision == 'M':

        today_str = calendar.month_name[date.month] + "'s Monthly Task Sheet - "
        prev_date_str = calendar.month_name[prev_date.month]
        next_date_str = calendar.month_name[next_date.month]

        msg.button_add("<< " + prev_date_str, action=all_tasks,
                       action_data={'date_precision': date_precision, 'date': prev_date})
        if date != today.replace(day=1):
            msg.button_add("This Month", action=all_tasks, keep_together=True,
                           action_data={'date_precision': date_precision, 'date': today})

        msg.button_add(next_date_str + " >>", action=all_tasks, keep_together=True,
                       action_data={'date_precision': date_precision, 'date': next_date})

        msg.button_add("➕ Create New", action=setup_tasks,
                       action_data={'date_precision': date_precision,
                                    'date':  date})

        msg.button_add("Daily", action=all_tasks,
                       action_data={'date_precision': 'D', 'date': today})
        msg.button_add("Weekly", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'W', 'date': today})
        msg.button_add("Pool", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'T', 'date': today})

    elif date_precision == 'T':
        today_str = "Task Pool - "

        msg.button_add("➕ Create New", action=setup_tasks,
                       action_data={'date_precision': date_precision,
                                    'date':  date})

        msg.button_add("Daily", action=all_tasks,
                       action_data={'date_precision': 'D', 'date': today})
        msg.button_add("Weekly", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'W', 'date': today})
        msg.button_add("Monthly", action=all_tasks, keep_together=True,
                       action_data={'date_precision': 'M', 'date': today})

    #items = DataList(app, chat_id=chat_id, action=task_actions)

    for field in fields:
        name = field[0]
        display_name = name
        category_name = field[2]
        if field[2] is not None:
            display_name += ' (<b>CAT:</b> <i>' + category_name + '</i>)'
        msg.list_add(display_name,
                     {'activity_id': field[1], 'date_precision': date_precision, 'date': date, 'name': name,
                      'category_name': category_name})

    text = make_header(date_precision=date_precision, date=date) + '\n\n{}'
    msg.show(text)


def make_header(name=None, date_precision=None, date=None, category_name=None):
    """Creates task header"""

    if date_precision == 'D':
        result = '<strong>DAILY TASK SHEET</strong>' + ' (' + get_day(date_precision, date) + ')'
    elif date_precision == 'W':
        result = '<strong>WEEKLY TASK SHEET</strong>' + ' (' + get_day(date_precision, date) + ')'
    elif date_precision == 'M':
        result = '<strong>MONTHLY TASK SHEET</strong>' + ' (' + get_day(date_precision, date) + ')'
    else:
        result = '<strong>TASK POOL</strong>'

    if name is not None:
        result += '\n<b>Task:</b> ' + name
    if category_name is not None:
        result += ' (<i>' + category_name + '</i>)'
    # if category_name is not None:
    #     result += '\n<b>Catg:</b> ' + category_name

    return result

    # task_header = '<b>Task:</b> ' + name + '\t\t(<b>' + get_day(date_precision, date) + '</b>)'
    # if category_name is not None:
    #     task_header += '\n<b>(Cat:</b> ' + category_name
    #
    # return task_header


def split_action_data(action_data, get_date=None):
    """Return recurring items from action_data"""

    print(action_data)

    activity_id = action_data['activity_id']
    name = action_data['name']
    category_name = action_data['category_name']
    date_precision = action_data['date_precision']
    if get_date is not False:
        date = action_data['date']
        return activity_id, name, category_name, date, date_precision
    else:
        return activity_id, name, category_name, date_precision


def task_actions(app, chat_id, event_info):
    """Individual task manipulation actions | complete, delete, move"""

    message_id = event_info['message_id']
    activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])

    task_header = make_header(name, date_precision, date, category_name)

    # FOR SOME OF THESE ONLY activity_id WILL BE NECESSARY
    msg = SappoGramMsg(app, chat_id, message_id, action=task_actions)
    msg.button_add("☑ Complete Now", action_data={**event_info['action_data'], 'date': datetime.date.today()},
                   action=request_emotion)
    msg.button_add("✔ Completed", action_data=event_info['action_data'], action=request_emotion, keep_together=True)
    msg.button_add("↪ Move Task", action_data=event_info['action_data'], action=move_task)
    msg.button_add("🔠 Edit Category", action_data=event_info['action_data'], action=edit_category, keep_together=True)
    msg.button_add("<< Back to Sheets", action_data=event_info['action_data'], action=all_tasks)
    msg.button_add("🚫 Delete", action_data=event_info['action_data'], action=task_delete, keep_together=True)

    msg.show(task_header + '\n\nWhat would you like to do with this task?')


def task_delete(app, chat_id, event_info):
    """Delete selected activity and direct the user to the next screen"""

    activity_id = event_info['action_data']['activity_id']
    task.cancel(activity_id)
    all_tasks(app, chat_id, event_info)


def move_task(app, chat_id, event_info):
    """Change date scheduled for a task"""

    message_id = event_info['message_id']
    activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])

    task_header = make_header(name, date_precision, date, category_name)
    today = datetime.date.today()

    msg = SappoGramMsg(app, chat_id, message_id)
    msg.button_add("Today", action=moved_navigation,
                   action_data={'activity_id': activity_id,
                                'name': name, 'category_name': category_name, 'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'D', 'date': today})
    msg.button_add("Tomorrow", action=moved_navigation, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'D',
                                'date': today + datetime.timedelta(days=1)})
    msg.button_add("Another Day", action=move_other, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'date_precision': date_precision,
                                'date': date, 'new_date_precision': 'D'})
    msg.button_add("This Week", action=moved_navigation,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'W', 'date': today})
    msg.button_add("Next Week", action=moved_navigation, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'W',
                                'date': today + datetime.timedelta(days=7)})
    msg.button_add("Another Week", action=move_other, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'date_precision': date_precision,
                                'date': date, 'new_date_precision': 'W'})
    msg.button_add("This Month", action=moved_navigation,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'M',
                                'date': today})
    msg.button_add("Next Month", action=moved_navigation, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'M',
                                'date': add_months(today, 1)})
    msg.button_add("Another Month", action=move_other, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'date_precision': date_precision,
                                'date': date, 'new_date_precision': 'M'})
    msg.button_add("<< Back to task options", action=task_actions,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'date_precision': date_precision, 'date': date})
    msg.button_add("Task Pool", action=moved_navigation, keep_together=True,
                   action_data={'activity_id': activity_id, 'name': name, 'category_name': category_name,
                                'last_date_precision': date_precision,
                                'last_date': date, 'date_precision': 'T',
                                'date': today})

    msg.show(task_header + '\n\nWhere would you like to pass this task over to?')


def move_other(app, chat_id, event_info):
    """Move tasks to a specific different sheet options"""

    message_id = event_info['message_id']
    activity_id, name, category_name, last_date, last_date_precision = split_action_data(event_info['action_data'])
    date_precision = event_info['action_data']['new_date_precision']

    task_header = make_header(name, last_date_precision, last_date, category_name)
    text = task_header + '\n\n'

    if date_precision == 'D':
        text += 'How many days from today? Type your answer\n' \
                '0 (today)\n' \
                '1 (tomorrow)\n' \
                '2 ...'
    elif date_precision == 'W':
        text += 'How many weeks from today? Type your answer\n' \
                '0 (this week)\n' \
                '1 (next week)\n' \
                '2 ...'

    elif date_precision == 'M':
        text += 'How many months from today?\n' \
                '0 (this month)\n' \
                '1 (next month)\n' \
                '2 ...\n\n' \
                ' Type your answer'

    msg = SappoGramMsg(app, chat_id, message_id, action=moved_navigation, action_data={
            'activity_id': activity_id,
            'name': name,
            'category_name': category_name,
            'last_date_precision': last_date_precision,
            'last_date': last_date,
            'date_precision': date_precision
            }
        )

    msg.user_input(
        text,
        action_cancel=move_task,
        action_cancel_data={
            'activity_id': activity_id,
            'name': name,
            'category_name': category_name,
            'date_precision': last_date_precision,
            'date': last_date
        }
    )


def request_emotion(app, chat_id, event_info):
    """Request intensity (1-10) of selected emotion"""

    message_id = event_info['message_id']
    activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])
    task_header = make_header(name, date_precision, date, category_name)

    # DO I WANT CANCEL BUTTON? SKIP STRENGTH?
    msg = SappoGramMsg(app, chat_id, message_id)
    msg.button_add('😵', action=insert_emotion,
                   action_data={**event_info['action_data'], 'emotion_id': -3})
    msg.button_add('😣', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': -2})
    msg.button_add('☹', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': -1})
    msg.button_add('😐', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': 0})
    msg.button_add('😊', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': 1})
    msg.button_add('😀', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': 2})
    msg.button_add('🤩', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'], 'emotion_id': 3})

    text = task_header + '\n\nSelect how you felt upon completing this task'
    msg.show(text)


def insert_emotion(app, chat_id, event_info):
    """Insert emotion into the database"""

    message_id = event_info['message_id']
    activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])
    task_header = make_header(name, date_precision, date, category_name)
    emotion_id = event_info['action_data']['emotion_id']

    if 'now' in event_info['action_data'] and date != datetime.date.today():
        task.pass_over(activity_id, date, date_precision)

    task.complete_with_emotion(activity_id=activity_id, emotion_id=emotion_id)

    msg = SappoGramMsg(app, chat_id, message_id)
    # GO TO DAILY LOG
    msg.button_add('See daily log >>', action=tgLog.activity_log,
                   action_data={'date': date})
    msg.button_add('<< Back to task sheets', action=all_tasks,
                   action_data={'date': date,
                                'date_precision': date_precision})

    text = task_header + '\n\nTask completed! Where would you like to go now?'
    msg.show(text)


def moved_navigation(app, chat_id, event_info):
    """Show navigation options after moving a task"""

    message_id = event_info['message_id']
    last_date_precision = event_info['action_data']['last_date_precision']
    last_date = event_info['action_data']['last_date']
    date = datetime.date.today()

    if 'user_input' in event_info:
        activity_id, name, category_name, date_precision = split_action_data(event_info['action_data'], get_date=False)
        user_input = int(event_info['user_input'][0])
        if date_precision == 'D':
            date = date + datetime.timedelta(days=user_input)
        elif date_precision == 'W':
            date = date + datetime.timedelta(days=user_input*7)
        elif date_precision == 'M':
            date = add_months(date, user_input)
        event_info['action_data']['date'] = date
    else:
        activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])

    date = task.correct_date(date, date_precision)
    task.pass_over(activity_id, date, date_precision)

    prev_date = get_day(last_date_precision, last_date)
    new_date = get_day(date_precision, date)

    event_info['action_data'].pop('last_date_precision')
    event_info['action_data'].pop('last_date')

    msg = SappoGramMsg(app, chat_id, message_id)
    msg.button_add('<< Return to ' + prev_date, action=all_tasks, action_data=event_info['action_data'])
    msg.button_add('Go to ' + new_date + ' >>', action=all_tasks, action_data=event_info['action_data'])
    msg.button_add("Continue editing task ...", action=task_actions, action_data=event_info['action_data'])

    msg.show('You have moved the task <i>' + name + '</i> from ' + prev_date + ' to ' + new_date)


def edit_category(app, chat_id, event_info):
    """Edit task categories"""

    message_id = event_info['message_id']
    activity_id, name, category_name, date, date_precision = split_action_data(event_info['action_data'])
    task_header = make_header(name, date_precision, date, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_category)
    # this button will not work currently, i do not want it here
    msg.button_add('<< Back to task sheets', action=task_actions, action_data=event_info['action_data'])

    fields = category.return_all(chat_id)

    for field in fields:
        category_name = field[0]
        category_id = field[1]
        # if field[2] is not None:
        #     parent_id = field[2]
        msg.list_add(category_name,
                  {'category_id': category_id,
                   'category_name': category_name,
                   'activity_id': activity_id,
                   'name': name,
                   'date': date,
                   'date_precision': date_precision})

    text = task_header + '\n\nSelect the new task category:\n\n{}'
    msg.show(text)


def update_category(app, chat_id, event_info):
    """Update a task category in the database and take the user to task_actions"""

    category_id = event_info['action_data']['category_id']
    activity_id = event_info['action_data']['activity_id']

    task.edit_category(activity_id, category_id)
    task_actions(app, chat_id, event_info)


def which_sheet4(chat_id, date_precision, date):
    """Decided which task sheet should be displayed"""

    date_prev = None
    date_next = None
    reply = None

    # assigns date for prev and next buttons
    if date_precision == 'D':
        date_prev = date - datetime.timedelta(days=1)
        date_next = date + datetime.timedelta(days=1)
        reply = task.get_daily(chat_id, date)

    elif date_precision == 'W':
        date = task.correct_date(date, date_precision)
        date_prev = date - datetime.timedelta(days=7)
        date_next = date + datetime.timedelta(days=7)
        reply = task.get_weekly(chat_id, date)

    elif date_precision == 'M':
        date = task.correct_date(date, date_precision)
        date_prev = add_months(date, -1)
        date_next = add_months(date, 1)
        reply = task.get_monthly(chat_id, date)

    elif date_precision == "T":
        reply = task.get_pool(chat_id, date)

    return reply, date_prev, date, date_next


def setup_tasks(app, chat_id, event_info):
    """Request task names from user --> then create tasks and return to all_sheets"""

    message_id = event_info['message_id']

    msg = SappoGramMsg(app, chat_id, message_id, action=insert_task, action_data=event_info['action_data'])
    text = 'Type the name of a new task for every line you send'

    msg.user_input(
        text,
        multiple_entries=True,
        action_cancel=all_tasks,
        action_cancel_data=event_info['action_data']
    )


def insert_task(app, chat_id, event_info):
    """Insert new tasks into the database"""

    # if event_info['action_data']['status'].exists():
    if 'log' in event_info['action_data']:
        status = 2
    else:
        status = 1

    for entry in event_info['user_input']:
        for field in entry.split('\n'):
            task_id = task.create(chat_id, field)
            task.schedule(task_id, status, event_info['action_data']['date'], event_info['action_data']['date_precision'])

    # if task has been created from the log, go back to log
    if status == 2:
        tgLog.activity_log(app, chat_id, event_info)
    else:
        all_tasks(app, chat_id, event_info)

