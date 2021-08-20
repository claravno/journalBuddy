# from jbLog import *
import math

import tgEvents
import tgHabits
import tgNotes
import tgTasks
from tgMsgTools import *

def activity_log(app, chat_id, event_info):
    """Display log"""

    today = datetime.date.today()

    if 'action_data' in event_info:
        message_id = event_info['message_id']
        date = event_info['action_data']['date']
    else:
        message_id = None
        date = today

    prev_date = date - datetime.timedelta(days=1)
    next_date = date + datetime.timedelta(days=1)
    fields = activity.get_log(chat_id, date)

    msg = SappoGramMsg(app, chat_id, message_id, action=activity_actions)

    day_name = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    today_str = get_day_abv(date) + ' ' + str(date.year)
    prev_date_str = day_name[prev_date.weekday()] + ' ' + prev_date.strftime("%d")
    next_date_str = day_name[next_date.weekday()] + ' ' + next_date.strftime("%d")

    msg.button_add("<< " + prev_date_str, action=activity_log, action_data={'date': prev_date})
    if date != today:
        msg.button_add("Today", action=activity_log, keep_together=True, action_data={'date': today})
    msg.button_add(next_date_str + " >>", action=activity_log, keep_together=True, action_data={'date': next_date})
    msg.button_add("➕ Create New", action=setup_log_entry, action_data={'date': date})

    for field in fields:
        name = field[0]
        display_name = name
        category_name = field[2]
        duration = field[4]
        quantity = field[5]
        start_time = field[6]
        end_time = field[7]
        if field[3] == 'E':
            type_name = 'Events'
        elif field[3] == 'T':
            type_name = 'Tasks'
        elif field[3] == 'H':
            type_name = 'Habits'
        if duration is not None:
            display_name += f' (<b>{str(math.trunc(duration))}m</b>)'
        if quantity is not None:
            display_name += f' (<b>{str(math.trunc(quantity))}</b>)'
        msg.list_add(display_name,
                     {'activity_id': field[1], 'date': date, 'name': name, 'category_name': category_name,
                      'type': type_name, 'duration': duration, 'quantity': quantity, 'start_time': start_time,
                      'end_time': end_time}, group=type_name)

    text = f'<strong>ACTIVITY LOG</strong> 🕔 ({today_str})'+'\n{}'
    msg.show(text)


def setup_log_entry(app, chat_id, event_info):
    """Setting up completed activities directly into log or create notes"""

    message_id = event_info['message_id']
    date = event_info['action_data']['date']

    msg = SappoGramMsg(app, chat_id, message_id, action=activity_actions)
    msg.button_add("📊 Habit", action=tgHabits.habits, action_data={'date': date, 'log': True})
    # msg.button_add("☑ Task", action=tgTasks.setup_tasks, keep_together=True, action_data={'date': date, 'date_precision': 'D', 'log': True})
    # msg.button_add("🗓 Event", action=tgEvents.setup_events, action_data={'date': date, 'log': True})
    # msg.button_add("📝 Note", action=tgNotes.setup_notes, keep_together=True, action_data={'date': date})
    msg.button_add("<< Back to log", action=activity_log, action_data={'date': date})

    # add header
    text = 'What would you like to add to your activity log?'
    msg.show(text)


def split_action_data(action_data):
    """extract variables from action data"""

    activity_id = action_data['activity_id']
    date = action_data['date']
    name = action_data['name']
    category_name = action_data['category_name']
    type_name = action_data['type'].strip('s')
    duration = action_data['duration']
    quantity = action_data['quantity']


    return activity_id, date, name, category_name, type_name, duration, quantity


def make_header(type_name, name, category_name, date, duration, quantity):
    """Activity header"""

    activity_header = f'\n<b>{type_name}:</b> ' + name + '  '
    if category_name is not None:
        activity_header += '(<i>' + category_name + '</i>)'
    activity_header += '\n<b>Date:</b> ' + get_day_abv(date)
    if quantity is not None:
        activity_header += f'\n<b>Quantity:</b> {quantity}'
    if duration is not None:
        activity_header += f'\n<b>Duration:</b> {duration}'

    return activity_header


def activity_actions(app, chat_id, event_info):
    """Individual activity manipulation actions | TBC"""

    message_id = event_info['message_id']
    activity_id, date, name, category_name, type_name, duration, quantity = split_action_data(event_info['action_data'])
    if type_name == 'Event':
        start_time = event_info['action_data']['start_time']
        end_time = event_info['action_data']['end_time']
        activity_header = tgEvents.make_header(name, date, start_time, end_time, category_name)
    else:
        activity_header = make_header(type_name, name, category_name, date, duration, quantity)

    msg = SappoGramMsg(app, chat_id, message_id, activity_actions)
    msg.button_add("🚫 Remove Completion", action_data=event_info['action_data'], action=remove_completion)
    if type_name == 'Habit':
        msg.button_add("📏 Change Measure", action_data=event_info['action_data'], action=request_measure, keep_together=True)
    msg.button_add("<< Back to Activity Log", action_data=event_info['action_data'], action=activity_log)

    msg.show(activity_header + '\n\nWhat would you like to do with this activity?')

def remove_completion(app, chat_id, event_info):
    """Remove completion from the habit"""

    message_id = event_info['message_id']
    activity_id, date, name, category_name, type_name, duration, quantity = split_action_data(event_info['action_data'])
    msg = SappoGramMsg(app, chat_id, message_id)

    if type_name == 'Event':
        start_time = event_info['action_data']['start_time']
        end_time = event_info['action_data']['end_time']
        event_header = tgEvents.make_header(name, date, start_time, end_time, category_name)
        text = event_header + '\n\nWhat would you like to do instead?'
        msg.button_add('🚫 Cancel event', action=cancel_event, action_data=event_info['action_data'])
        msg.button_add('🗓 Reschedule', action=tgEvents.request_date, action_data={**event_info['action_data'], 'remove_completion': True}, keep_together=True)
        msg.button_add('<< Keep completion', action=activity_actions, action_data=event_info['action_data'])

    elif type_name == 'Task':
        activity.remove_completion(activity_id)
        text = 'Where would you like to go?'
        msg.button_add(get_day('D', date) + ' Task Sheet >>', action=tgTasks.all_tasks,
                       action_data={**event_info['action_data'], 'date_precision': 'D'})
        msg.button_add('<< Return to Activity Log', action=activity_log, action_data=event_info['action_data'])
    elif type_name == 'Habits':
        habit.remove_completion(activity_id, date)
        activity_log(app, chat_id, event_info)

    msg.show(text)



def request_measure(app, chat_id, event_info):
    """Ask user for new measure of habit"""



def cancel_event(app, chat_id, event_info):
    """Cancel event and return to activity_log"""

    event.cancel(event_info['action_data']['activity_id'])
    activity_log(app, chat_id, event_info)