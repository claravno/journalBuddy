from jbTools import *


def habit_names(id, message_text):
    """Process habit set up message"""

    list = []

    if (habits.keys()).__contains__(id):
        try:
            list = habits.get(id) + message_text.split('\n')
        except:
            list = habits.get(id) + [message_text]
        habits[id] = list
    else:
        try:
            for x in message_text.split('\n'):
                list.append(x)
        except:
            list.append(message_text)
        habits[id] = list


def complete_habit(message_text, id):
    """Mark habit as complete"""

    list = habit.return_all(id)[0]

    tel_id_string = message_text.strip('/')
    tel_id = int(tel_id_string) - 1

    activity_id = list[tel_id][1]

    habit.complete(activity_id, datetime.date.today(), id)
