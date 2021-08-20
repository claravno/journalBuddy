import dbJournalBuddy
import tgGoals
import tgLog
from tgMsgTools import *
from jbHabits import *


# -------------------------------------------------------------------------------

def habits(app, chat_id, event_info):
    """Display habits with completion information for current day"""

    add_to_dic = 'habits'
    text = '<strong>HABITS</strong> 📊\n{}'
    show_buttons = True

    if 'action_data' in event_info and 'cancel' not in event_info:
        message_id = event_info['message_id']
        msg = SappoGramMsg(app, chat_id, message_id, action=request_measure_type, action_data=event_info['action_data'])
        try:
            date = event_info['action_data']['date']
        except:
            date = datetime.datetime.today()

# if the flow is coming from tgLog.activity_log (i.e. add habit to activity log)
        if 'log' in event_info['action_data']:
            text = '<strong>Which habit would you like to complete?</strong>\n\n{}'
            msg.button_add("< Back to log", action=tgLog.activity_log, action_data=event_info['action_data'])
            add_to_dic = 'log'
            # event_info['action_data'].pop('log')
            show_buttons = False

        # if the flow is coming from tgGoals.goals (i.e. add goal to specific week)
        elif 'goals' in event_info['action_data']:
            text = '<strong>Setting GOALS 🎯 choose a habit!</strong>\n\n{}'
            msg.button_add("< Back to goals", action=tgGoals.goals, action_data=event_info['action_data'])
            add_to_dic = 'goals'
            # event_info['action_data'].pop('goals')
            show_buttons = False

        elif 'deactivate' in event_info['action_data']:
            dbJournalBuddy.habit.deactivate(event_info['action_data']['activity_id'])
            event_info['action_data'].pop('deactivate')
            msg = SappoGramMsg(app, chat_id, message_id, action=habit_actions)

        # else:
        #     msg.button_add("➕ Create Habit", action=setup_habits)

    # if the user struck the /habits command
    else:
        message_id = None
        date = datetime.date.today()
        msg = SappoGramMsg(app, chat_id, message_id, action=habit_actions)

    if show_buttons:
        msg.button_add("➕ Create New", action=setup_habits)
        msg.button_add("😴 Deactivated Habits", action=setup_habits, keep_together=True)


    fields = habit.return_all(chat_id)
    print('fields ', fields)
    for field in fields:
        name = field[0]
        activity_id = field[1]
        category_id = field[2]
        category_name = field[3]
        measure_type = field[4]
        display_name = name
        # if category_id is not None:
        #     display_name += ' (<i>' + category_name + '</i>)'
        msg.list_add(display_name,
                     {'activity_id': activity_id,
                      'name': name,
                      'category_id': category_id,
                      'category_name': category_name,
                      'measure_type': measure_type,
                      'date': date,
                      add_to_dic: True}, group=category_name)

    msg.show(text)


def setup_habits(app, chat_id, event_info):
    """Request category names from user --> then create habits and return to all_sheets"""

    message_id = event_info['message_id']

    try:
        date = event_info['action_data']['date']
    except:
        date = datetime.date.today()

    msg = SappoGramMsg(app, chat_id, message_id, action=insert_habits, action_data={'date': date})
    text = 'Type the name of a new habit for every line you send'

    msg.user_input(
        text,
        multiple_entries=True,
        action_cancel=habits,
        action_cancel_data=event_info['action_data']
    )


def insert_habits(app, chat_id, event_info):
    """Insert new habits into the database"""

    for entry in event_info['user_input']:
        for field in entry.split('\n'):
            habit.create(chat_id, field)

    habits(app, chat_id, event_info)


def make_header(name, category_name):
    """Create category header"""

    habit_header = '\n<b>Habit:</b> ' + name
    if category_name is not None:
        habit_header += ' (<i>' + category_name + '</i>)'

    return habit_header


def split_action_data(action_data):
    """Returns event_info's action_data as variables"""

    activity_id = action_data['activity_id']
    name = action_data['name']
    category_id = action_data['category_id']
    category_name = action_data['category_name']

    return activity_id, name, category_id, category_name


def habit_actions(app, chat_id, event_info):
    """Individual habit manipulation actions | complete, delete, move"""

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)

    # FOR SOME OF THESE ONLY activity_id WILL BE NECESSARY
    msg = SappoGramMsg(app, chat_id, message_id, habit_actions)
    msg.button_add("✔ Complete", action_data=event_info['action_data'], action=request_measure_type)
    msg.button_add("🚫 Deactivate", action_data={**event_info['action_data'], 'deactivate': True}, action=habits, keep_together=True)
    msg.button_add("✏ Edit Name", action_data=event_info['action_data'], action=request_name)
    msg.button_add("🔠 Edit Category", action_data=event_info['action_data'], action=edit_category, keep_together=True)
    msg.button_add("<< Back to Habits", action_data=event_info['action_data'], action=habits)

    msg.show(habit_header + '\n\nWhat would you like to do with this habit?')


def deactivate(app, chat_id, event_info):
    """Update database so the habit is not retrieved in the main page"""



def edit_category(app, chat_id, event_info):
    """Edit habit categories"""

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_category)
    # this button will not work currently, i do not want it here
    msg.button_add('<< Back to habit', action=habit_actions, action_data=event_info['action_data'])

    fields = category.return_all(chat_id)

    for field in fields:
        category_name = field[0]
        category_id = field[1]
        #     parent_id = field[2]
        msg.list_add(category_name,
                     {'category_id': category_id,
                      'category_name': category_name,
                      'activity_id': activity_id,
                      'name': name})

    text = habit_header + '\n\nSelect the new habit category:\n\n{}'
    msg.show(text)


def update_category(app, chat_id, event_info):
    """Update a habit category in the database and take the user to habit_actions"""

    print(event_info)
    category_id = event_info['action_data']['category_id']
    activity_id = event_info['action_data']['activity_id']

    habit.edit_category(activity_id, category_id)
    habit_actions(app, chat_id, event_info)


def request_name(app, chat_id, event_info):
    """Edit category categories"""

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_name, action_data=event_info['action_data'])
    text = habit_header + '\n\nType the new name of your habit!'

    msg.user_input(
        text,
        action_cancel=habit_actions,
        action_cancel_data=event_info['action_data']
    )


def request_measure_type(app, chat_id, event_info):
    """Prompt user to insert measure type --> then direct to request emotions"""

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)
    text = habit_header + '\n\n'


    # If the user has not selected a default measure type for the habit they want to complete...
    if event_info['action_data']['measure_type'] is None:
        # is the action necessary? should it be request_emotion?
        msg = SappoGramMsg(app, chat_id, message_id, action=request_emotion, action_data=event_info['action_data'])

        # ask them which default measure type they want, save their choice
        text += 'How would you like to measure this habit?'

        # display options
        msg.button_add('Quantity', action=enter_measure, action_data={**event_info['action_data'], 'measure_type': 'Q',
                                                                      'measure_type_change': True})
        msg.button_add('Duration', action=enter_measure, action_data={**event_info['action_data'], 'measure_type': 'D',
                                                                      'measure_type_change': True})
        if 'goals' in event_info['action_data']:
            msg.button_add('Frequency', action=enter_measure, action_data={**event_info['action_data'],
                                                                           'measure_type': 'F'})
        else:
            msg.button_add('Done/Not done', action=enter_measure, action_data={**event_info['action_data'],
                                                                           'measure_type': 'N',
                                                                       'measure_type_change': True})
    else:
        if 'goals' in event_info['action_data']:
            msg = SappoGramMsg(app, chat_id, message_id, action=request_emotion, action_data=event_info['action_data'])
            text += 'How would you like to measure this habit?'
            if event_info['action_data']['measure_type'] == 'Q':
                msg.button_add('Quantity', action=enter_measure, action_data=event_info['action_data'])
            elif event_info['action_data']['measure_type'] == 'D':
                msg.button_add('Duration', action=enter_measure, action_data=event_info['action_data'])
            msg.button_add('Frequency', action=enter_measure, action_data={**event_info['action_data'],
                                                                           'measure_type': 'F'})
        else:
            enter_measure(app, chat_id, event_info)

    msg.show(text)


def enter_measure(app, chat_id, event_info):

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)
    text = habit_header + '\n\n'

    if 'measure_type_change' in event_info['action_data']:
        habit.change_measure_type(event_info['action_data']['activity_id'], event_info['action_data']['measure_type'])

    if event_info['action_data']['measure_type'] == 'Q':
        measure_name = 'QUANTITY'
    elif event_info['action_data']['measure_type'] == 'D':
        measure_name = 'DURATION'
    # elif event_info['action_data']['measure_type'] == 'SE':
    #     measure_name = 'START/END TIME (as hh:mm-hh:mm)'
    elif event_info['action_data']['measure_type'] == 'F':
        measure_name = 'FREQUENCY'
    elif event_info['action_data']['measure_type'] == 'N':
        request_emotion(app, chat_id, event_info)

    if 'goals' in event_info['action_data']:
        text += f'Enter the {measure_name} you are aiming for *this week*'
        msg = SappoGramMsg(app, chat_id, message_id, action=tgGoals.setup_goals, action_data=event_info['action_data'])
    else:
        text += f'Enter the {measure_name} of completions'
        msg = SappoGramMsg(app, chat_id, message_id, action=request_emotion, action_data=event_info['action_data'])

    msg.user_input(
        text,
        action_cancel=habit_actions,
        action_cancel_data=event_info['action_data']
    )


def update_name(app, chat_id, event_info):
    """Update category name in the database"""

    activity_id = event_info['action_data']['activity_id']
    name = event_info['user_input'][0]
    habit.update_name(activity_id, name)

    habit_actions(app, chat_id, event_info)


def request_emotion(app, chat_id, event_info):
    """Request intensity (1-10) of selected emotion"""

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)
    try:
        measure = int(event_info['user_input'][0])
    except:
        measure = None

    # DO I WANT CANCEL BUTTON? SKIP STRENGTH?
    msg = SappoGramMsg(app, chat_id, message_id)
    msg.button_add('😵', action=insert_emotion,
                   action_data={**event_info['action_data'],
                                'emotion_id': -3,
                                'measure': measure})
    msg.button_add('😣', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': -2,
                                'measure': measure})
    msg.button_add('☹', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': -1,
                                'measure': measure})
    msg.button_add('😐', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': 0,
                                'measure': measure})
    msg.button_add('😊', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': 1,
                                'measure': measure})
    msg.button_add('😀', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': 2,
                                'measure': measure})
    msg.button_add('🤩', action=insert_emotion, keep_together=True,
                   action_data={**event_info['action_data'],
                                'emotion_id': 3,
                                'measure': measure})

    text = habit_header + '\n\nSelect how you felt upon completing this habit'
    msg.show(text)


def insert_emotion(app, chat_id, event_info):
    """Insert emotion into the database"""

    if 'log' in event_info['action_data']:
        date = event_info['action_data']['date']
    else:
        date = datetime.date.today()

    message_id = event_info['message_id']
    activity_id, name, category_id, category_name = split_action_data(event_info['action_data'])
    habit_header = make_header(name, category_name)

    emotion_id = event_info['action_data']['emotion_id']
    measure_type = event_info['action_data']['measure_type']
    measure = event_info['action_data']['measure']

    habit.complete(activity_id, date, measure=measure, measure_type=measure_type, emotion_id=emotion_id)

    msg = SappoGramMsg(app, chat_id, message_id)
    # GO TO ACTIVITY LOG
    msg.button_add('🔘 Activity Log >>', action=tgLog.activity_log, action_data=event_info['action_data'])
    msg.button_add('<< 📊 Habits', action=habits)

    text = habit_header + '\n\nHabit completed! Where would you like to go now?'
    msg.show(text)
