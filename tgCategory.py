from tgMsgTools import *
from jbTools import *

def categories(app, chat_id, event_info):
    """Display habits with completion information for current day"""

    if 'action_data' in event_info:
        message_id = event_info['message_id']
    else:
        message_id = None

    fields = category.return_all(chat_id)

    msg = SappoGramMsg(app, chat_id, message_id, action=category_actions)
    msg.button_add("Create New", action=setup_categories)

    for field in fields:
        name = field[0]
        category_id = field[1]
        # if field[2] is not None:
        #     parent_id = field[2]
        msg.list_add(name,
                     {'category_id': category_id, 'name': name})

    text = 'CATEGORIES\n\n{}'
    msg.show(text)


def setup_categories(app, chat_id, event_info):
    """Request category names from user --> then create tasks and return to all_sheets"""

    message_id = event_info['message_id']

    msg = SappoGramMsg(app, chat_id, message_id, action=insert_categories, action_data=event_info['action_data'])
    text = 'Type the name of a new task for every line you send'

    msg.user_input(
        text,
        multiple_entries=True,
        action_cancel=categories,
        action_cancel_data=event_info['action_data']
    )


def insert_categories(app, chat_id, event_info):
    """Insert new tasks into the database"""

    for entry in event_info['user_input']:
        for field in entry.split('\n'):
            category.create(chat_id, field)

    categories(app, chat_id, event_info)


def make_header(name):
    """Create category header"""

    category_header = '<b>Category: </b>' + name

    return category_header


def split_action_data(action_data):
    """Returns event_info's action_data as variables"""

    category_id = action_data['category_id']
    name = action_data['name']

    return category_id, name


def category_actions(app, chat_id, event_info):
    """Individual task manipulation actions | complete, delete, move"""

    message_id = event_info['message_id']
    category_id, name= split_action_data(event_info['action_data'])

    task_header = make_header(name)

    # FOR SOME OF THESE ONLY activity_id WILL BE NECESSARY
    msg = SappoGramMsg(app, chat_id, message_id, action=category_actions)
    msg.button_add("Edit Name", action_data=event_info['action_data'], action=request_name, keep_together=True)
    msg.button_add("Delete", action_data=event_info['action_data'], action=category_delete, keep_together=True)
    msg.button_add("<< Back to Categories", action_data=event_info['action_data'], action=categories)

    msg.show(task_header + '\n\nWhat would you like to do with this category?')



def request_name(app, chat_id, event_info):
    """Edit category categories"""

    message_id = event_info['message_id']
    category_id, name = split_action_data(event_info['action_data'])
    category_header = make_header(name)

    msg = SappoGramMsg(app, chat_id, message_id, action=update_name, action_data=event_info['action_data'])
    text = category_header + '\n\nType the new name of your category!'

    msg.user_input(
        text,
        multiple_entries=True,
        action_cancel=categories,
        action_cancel_data=event_info['action_data']
    )

    msg = SappoGramMsg(app, chat_id, message_id)
    # this button will not work currently, i do not want it here
    msg.button_add('<< Back to task sheets', action=categories, action_data=event_info['action_data'])

    text = category_header + '\n\nSelect the new category name:\n\n{}'
    msg.show(text)


def update_name(app, chat_id, event_info):
    """Update category name in the database"""

    category_id = event_info['action_data']['category_id']
    name = event_info['user_input'][0]
    category.update_name(category_id, name)

    categories(app, chat_id, event_info)


def category_delete(app, chat_id, event_info):
    """Update category name in the database"""

    category_id = event_info['action_data']['category_id']
    category.delete(category_id)

    categories(app, chat_id, event_info)
