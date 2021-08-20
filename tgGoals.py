# from jbGoals import *
import math

import tgHabits
from tgMsgTools import *

def goals(app, chat_id, event_info):
    """Display current goals and progress"""

    start_of_week = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())

    if 'action_data' in event_info:
        message_id = event_info['message_id']
        date = event_info['action_data']['date']
    else:
        message_id = None
        date = start_of_week

    prev_date = date - datetime.timedelta(days=7)
    next_date = date + datetime.timedelta(days=7)

    prev_date_str = prev_date.strftime("%d/%m")
    next_date_str = next_date.strftime("%d/%m")

    msg = SappoGramMsg(app, chat_id, message_id, action=goal_actions)

    msg.button_add("<< " + prev_date_str, action=goals,
                   action_data={'date': prev_date})
    if date != start_of_week:
        msg.button_add("This Week", action=goals, keep_together=True,
                       action_data={'date': start_of_week})

    msg.button_add(next_date_str + " >>", action=goals, keep_together=True,
                   action_data={'date': next_date})

    msg.button_add("➕ Set Goal", action=tgHabits.habits, action_data={'date': date, 'goals': True})

    text = f'<strong> WEEKLY GOALS 🎯</strong> ({date.strftime("%d/%m")})\n'+'{}'

    fields = goal.return_all(chat_id, date)
    # a.name, h.activity_id, c.name, h.measure, h.measure_type
    print('fields ', fields)
    for field in fields:
        activity_id = field[0]
        name = field[1]
        category_id = field[2]
        category_name = field[3]
        measure = field[4]
        measure_type = field[5]
        msr = field[6]
        fqy = field[7]
        if measure_type == 'D' or measure_type == 'Q':
            if msr >= measure:
                display_name = f'<b>{name}</b>'
            else:
                display_name = name
            display_name += f' (<i>{math.trunc(msr)}/{math.trunc(measure)}</i>)'
        else:
            if fqy >= measure:
                display_name = f'<b>{name}</b>'
            else:
                display_name = name
            display_name += f' (<i>{fqy}/{math.trunc(measure)}</i>)'
        msg.list_add(display_name,
                     {'activity_id': activity_id,
                      'name': name,
                      'category_id': category_id,
                      'category_name': category_name,
                      'measure': measure,
                      'measure_type': measure_type,
                      'date': date,
                      'msr': msr,
                      'fqy': fqy}, group=category_name)

    msg.show(text)


def split_action_data(action_data):
    """Retrieve local variables from event_info"""

    activity_id = action_data['activity_id']
    name = action_data['name']
    category_id = action_data['category_id']
    category_name = action_data['category_name']
    measure = action_data['measure']
    measure_type = action_data['measure_type']
    date = action_data['date']

    return activity_id, name, category_id, category_name, measure, measure_type, date


def goal_actions(app, chat_id, event_info):
    """Edit/view goal"""
    message_id = event_info['message_id']
    activity_id, name, category_id, category_name, measure, measure_type, date = split_action_data(event_info['action_data'])
    make_header

    msg = SappoGramMsg(app, chat_id, message_id)
    msg.button_add("Change measure", action_data=event_info['action_data'], action=request_measure)
    msg.button_add("Add completion", action_data=event_info['action_data'], action=request_measure, keep_together=True)
    msg.button_add("<< Back to goals", action_data=event_info['action_data'], action=goals)

    print('time to look at some goals')


def setup_goals(app, chat_id, event_info):
    """Create new goal for the week"""

    measure = event_info['user_input'][0]

    goal.create(activity_id=event_info['action_data']['activity_id'], date=event_info['action_data']['date'], measure=measure, measure_type=event_info['action_data']['measure_type'])
    goals(app, chat_id, event_info)

