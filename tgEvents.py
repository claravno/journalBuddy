import dbJournalBuddy
import tgLog
from tgMsgTools import *
from jbTools import *
# from jbEvents import *

def events(app, chat_id, event_info):
    """Display events with completion information for current day"""

    if 'action_data' not in event_info:
        message_id = None
    else:
        message_id = event_info['message_id']
        try:
            if 'status' in event_info['action_data']:
                dbJournalBuddy.event.update_status(event_info['action_data']['activity_id'], event_info['action_data']['status'])
                event_info['action_data'].pop('status')
        except:
            print('ignore')

    msg = SappoGramMsg(app, chat_id, message_id, action=event_actions)
    msg.button_add("➕ Create Event", action=setup_events)
    msg.button_add("🚫 View Cancelled", action=cancelled_events, keep_together=True)

    fields = event.return_all(chat_id, 1)
    print('fields ', fields)
    for field in fields:
        name = field[0]
        activity_id = field[1]
        date = field[2]
        start_time = field[3]
        end_time = field[4]
        category_id = field[5]
        category_name = field[6]
        group = calendar.month_name[date.month]
        display_date = datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%y')
        display_name = name + f' (<i>{display_date}</i>)'
        # if category_id is not None:
        #     display_name +=
        msg.list_add(display_name,
                     {'activity_id': activity_id,
                      'name': name,
                      'date': date,
                      'start_time': start_time,
                      'end_time': end_time,
                      'category_id': category_id,
                      'category_name': category_name}, group=group.upper())

    text = '<strong>EVENTS</strong> 🗓\n{}'
    msg.show(text)


def setup_events(app, chat_id, event_info):
    """Request category names from user --> then create events and return to all_sheets"""

    message_id = event_info['message_id']

    if 'log' not in event_info['action_data']:
        msg = SappoGramMsg(app, chat_id, message_id, action=insert_events, action_data=event_info['action_data'])
    else:
        msg = SappoGramMsg(app, chat_id, message_id, action=request_emotion, action_data=event_info['action_data'])

    text = 'Type the name of a new event for every line you send in the format:\n' \
           'event name, dd/mm/yyyy, hh:mm-hh:mm'

    msg.user_input(
        text,
        multiple_entries=True,
        action_cancel=events,
        action_cancel_data=event_info['action_data']
    )


def insert_events(app, chat_id, event_info):
    """Insert new events into the database"""

    # if event_info['action_data']['status'].exists():

    end_time = None
    for entry in event_info['user_input']:
        for field in entry.split('\n'):
            event_data = field.split(',')
            name = event_data[0]
            # handle date data
            date_str = event_data[1].strip(' ')
            date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            # handle time data
            times = event_data[2].split('-')
            start_time_str = times[0].strip(' ')
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            if len(times) > 1:
                end_time = datetime.datetime.strptime(times[1], "%H:%M")

            activity_id = event.create(chat_id, name)
            event.schedule(activity_id, date, start_time, end_time, 1)


    try:
        if 'log' in event_info['action_data']:
            request_emotion(app, chat_id, event_info)
    except:
        events(app, chat_id, event_info)


def make_header(name, date, start_time, end_time, category_name):
    """Create category header"""

    event_header = '\n<b>Event:</b> ' + name + '  '
    if category_name is not None:
        event_header += '(<i>' + category_name + '</i>)'
    event_header += '\n<b>Date:</b> ' + get_day_abv(date) + '  <b>Time:</b> ' + str(start_time)
    if end_time is not None:
        event_header += ' - ' + str(end_time)

    return event_header


def split_action_data(action_data):
    """Returns event_info's action_data as variables"""

    activity_id = action_data['activity_id']
    name = action_data['name']
    date = action_data['date']
    start_time = action_data['start_time']
    end_time = action_data['end_time']
    try:
        category_id = action_data['category_id']
    except:
        category_id = None
    category_name = action_data['category_name']

    return activity_id, name, date, start_time, end_time, category_id, category_name


def event_actions(app, chat_id, event_info):
    """Individual event manipulation actions | complete, delete, move"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    # FOR SOME OF THESE ONLY activity_id WILL BE NECESSARY
    msg = SappoGramMsg(app, chat_id, message_id, event_actions)
    msg.button_add("✔ Complete", action_data=event_info['action_data'], action=request_emotion)
    msg.button_add("🚫 Cancel", action_data={**event_info['action_data'], 'status': 4}, action=events, keep_together=True)
    msg.button_add("✏ Edit Name", action_data=event_info['action_data'], action=request_name)
    msg.button_add("🔠 Edit Category", action_data=event_info['action_data'], action=edit_category, keep_together=True)
    msg.button_add("🗓 Change Date", action_data=event_info['action_data'], action=request_date)
    msg.button_add("🕒 Change Time", action_data=event_info['action_data'], action=request_time, keep_together=True)
    msg.button_add("<< Back to Events", action_data=event_info['action_data'], action=events)

    msg.show(event_header + '\n\nWhat would you like to do with this event?')


def request_name(app, chat_id, event_info):
    """Edit category categories"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_name, action_data=event_info['action_data'])
    text = event_header + '\n\nType the new name of your event!'

    msg.user_input(
        text,
        action_cancel=events,
        action_cancel_data=event_info['action_data']
    )


def update_name(app, chat_id, event_info):
    """Update category name in the database"""

    activity_id = event_info['action_data']['activity_id']
    name = event_info['user_input'][0]
    event.update_name(activity_id, name)

    event_actions(app, chat_id, event_info)


def edit_category(app, chat_id, event_info):
    """Edit event categories"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_category)
    # this button will not work currently, i do not want it here
    msg.button_add('<< Back to event', action=event_actions, action_data=event_info['action_data'])

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

    text = event_header + '\n\nSelect the new event category:\n\n{}'
    msg.show(text)


def update_category(app, chat_id, event_info):
    """Update a event category in the database and take the user to event_actions"""

    print(event_info)
    category_id = event_info['action_data']['category_id']
    activity_id = event_info['action_data']['activity_id']

    event.edit_category(activity_id, category_id)
    event_actions(app, chat_id, event_info)


def request_emotion(app, chat_id, event_info):
    """Request intensity (1-10) of selected emotion"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(
        event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

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

    text = event_header + '\n\nSelect how you felt upon completing this event'
    msg.show(text)


def insert_emotion(app, chat_id, event_info):
    """Insert emotion into the database"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(
        event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)
    emotion_id = event_info['action_data']['emotion_id']

    event.complete_with_emotion(activity_id, emotion_id=emotion_id)

    msg = SappoGramMsg(app, chat_id, message_id)
    # GO TO DAILY LOG
    msg.button_add('Activity log >>', action=tgLog.activity_log, action_data={'date': event_info['action_data']['date']})
    msg.button_add('<< Scheduled Events', action=events)

    text = event_header + '\n\nEvent completed! Where would you like to go now?'
    msg.show(text)


def request_date(app, chat_id, event_info):
    """Edit category categories"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    try:
        if 'remove_completion' in event_info['action_data']:
            activity.remove_completion(activity_id, date)
    except:
        print('error in tgEvents.request_date')

    msg = SappoGramMsg(app, chat_id, message_id, action=update_date, action_data=event_info['action_data'])
    text = event_header + '\n\nType the new date of your event! (dd/mm/yyyy)'

    msg.user_input(
        text,
        action_cancel=events,
        action_cancel_data=event_info['action_data']
    )


def update_date(app, chat_id, event_info):
    """Update category name in the database"""

    activity_id = event_info['action_data']['activity_id']
    date_str = event_info['user_input'][0]
    date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
    event.update_date(activity_id, date)

    try:
        if 'remove_completion' in event_actions['action_data']:
            tgLog.activity_log(app, chat_id, event_info)
    except:
        event_actions(app, chat_id, event_info)


def request_time(app, chat_id, event_info):
    """Edit category categories"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_time, action_data=event_info['action_data'])
    text = event_header + '\n\nType the new time of your event! hh:mm-hh:mm (start time - end time)'

    msg.user_input(
        text,
        action_cancel=events,
        action_cancel_data=event_info['action_data']
    )


def update_time(app, chat_id, event_info):
    """Update category name in the database"""

    activity_id = event_info['action_data']['activity_id']
    end_time = None

    times = event_info['user_input'][0].split('-')
    start_time_str = times[0].strip(' ')
    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
    if len(times) > 1:
        end_time = datetime.datetime.strptime(times[1], "%H:%M")

    event.update_time(activity_id, start_time, end_time)
    event_actions(app, chat_id, event_info)


def cancelled_events(app, chat_id, event_info):
    """Display events with completion information for current day"""

    if 'action_data' not in event_info:
        message_id = None
    else:
        message_id = event_info['message_id']

    msg = SappoGramMsg(app, chat_id, message_id, action=cancelled_event_actions)
    msg.button_add("<< Scheduled Events", action=events)

    fields = event.return_all(chat_id, 4)
    for field in fields:
        name = field[0]
        activity_id = field[1]
        date = field[2]
        start_time = field[3]
        end_time = field[4]
        category_id = field[5]
        category_name = field[6]
        group = calendar.month_name[date.month]
        display_date = datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%y')
        display_name = name + f' (<i>{display_date}</i>)'
        # if category_id is not None:
        #     display_name +=
        msg.list_add(display_name,
                     {'activity_id': activity_id,
                      'name': name,
                      'date': date,
                      'start_time': start_time,
                      'end_time': end_time,
                      'category_id': category_id,
                      'category_name': category_name}, group=group.upper())

    text = '<strong>CANCELLED EVENTS</strong> 🚫\n{}'
    msg.show(text)


def cancelled_event_actions(app, chat_id, event_info):
    """Individual event manipulation actions | complete, delete, move"""

    message_id = event_info['message_id']
    activity_id, name, date, start_time, end_time, category_id, category_name = split_action_data(event_info['action_data'])
    event_header = make_header(name, date, start_time, end_time, category_name)

    # FOR SOME OF THESE ONLY activity_id WILL BE NECESSARY
    msg = SappoGramMsg(app, chat_id, message_id, event_actions)
    msg.button_add("🗓 Reactivate", action=events, action_data={**event_info['action_data'], 'status': 1})
    msg.button_add("🚫 Delete Permanently", action_data={**event_info['action_data'], 'cancel': True}, action=events, keep_together=True)
    msg.button_add("<< Cancelled Events", action_data=event_info['action_data'], action=cancelled_events)

    msg.show(event_header + '\n\nWhat would you like to do with this event?')


