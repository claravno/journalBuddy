from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
#from calendar import *
import calendar
from dbJournalBuddy import *



# -------------------------------------------------------------------------------
class ChatController:

    routes = {}
    user_input_routes = {}
    user_index_routes = {}
    msg_btn_routes = {}
    chat_list = {}

    @staticmethod
    def add_routes(routes):
        ChatController.routes = routes

    @staticmethod
    def index_ini(chat_id, action, prefix=None):
        ChatController.chat_list[chat_id] = {}

        ChatController.chat_list[chat_id]['data_list'] = DataList(action, prefix)
        return ChatController.chat_list[chat_id]['data_list']

    @staticmethod
    def index_click(app, chat_id, text):
        return ChatController.chat_list[chat_id]['data_list'].click(app, chat_id, text)

    @staticmethod
    def user_index_add(app, chat_id, action, user_index):
        ChatController.user_index_routes[chat_id] = {'action': action, 'user_index': user_index}

    @staticmethod
    def user_index_upd(app, chat_id, message_id):
        ChatController.user_index_routes[chat_id]['message_id'] = message_id

    @staticmethod
    def user_index_del(app, chat_id):
        if chat_id in ChatController.user_index_routes:
            del ChatController.user_index_routes[chat_id]

    @staticmethod
    def user_input_add(app, chat_id, action):
        ChatController.user_input_routes[chat_id] = action

    @staticmethod
    def user_input_del(app, chat_id):
        if chat_id in ChatController.user_input_routes:
            del ChatController.user_input_routes[chat_id]

    @staticmethod
    def msg_btn_add(app, chat_id, message_id, action_list):
        print(action_list)
        if chat_id not in ChatController.msg_btn_routes:
            ChatController.msg_btn_routes[chat_id] = {}
        if message_id not in ChatController.msg_btn_routes[chat_id]:
            ChatController.msg_btn_routes[chat_id][message_id] = {}

        ChatController.msg_btn_routes[chat_id][message_id] = action_list
        print(ChatController.msg_btn_routes)


# -------------------------------------------------------------------------------
class SappoGramMsg:

    def __init__(self, app, chat_id, message_id=None, action=None, action_data=None):
        self.app = app
        self.chat_id = chat_id
        self.message_id = message_id
        self.inline_bt_list = None
        self.action_list = {}
        self.list_text = []
        self.list_group = []
        self.list_action_data = []
        self.action = action
        self.action_data = action_data
        self.list_prefix = None
        self.input_result = []
        self.button_prt = 0

        self.text = None
        self.confirmation_text = None
        self.multiple_entries = None
        self.action_cancel = None
        self.action_cancel_data = None

    def button_add(
            self,
            caption,
            action=None,
            action_data=None,
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            keep_together=False
    ):
        """
        Include an inline button to the message
        :param caption: button's caption
        :param action: function/method that will be executed by the button
        :param action_data: data that will be sent to the action function/method
        :param url: Telegram standard
        :param switch_inline_query: Telegram standard
        :param switch_inline_query_current_chat: Telegram standard
        :param keep_together: Makes the button at the same line as the last one
        """

        self.button_prt += 1
        # Initialize the variable 'inline_bt_list' at the first button
        if self.inline_bt_list is None:
            self.inline_bt_list = []
            #self.inline_bt_list.append([])
        # If this button should not be kept together
        # than creates a new button line
        if keep_together is False or self.button_prt == 1:
            self.inline_bt_list.append([])

        # If exists action for the button, includes the function to the route collection
        # and includes the function's name at the callback_data
        callback_data = None
        if action is not None:
            callback_data = action.__qualname__ + '_' + str(self.button_prt)
            self.action_list[callback_data] = {'action': action, 'action_data': action_data}
            print('>>>>', callback_data)

        if callback_data is None:
            callback_data = 'nodata'

        # Include the new button at the last button line
        ptr = len(self.inline_bt_list) - 1
        self.inline_bt_list[ptr].append(
            InlineKeyboardButton(
                caption,
                callback_data=callback_data,
                url=url,
                switch_inline_query=switch_inline_query,
                switch_inline_query_current_chat=switch_inline_query_current_chat
            )
        )

    def list_add(self, text, action_data, group=None):
        """
        Includes a user list item in the message
        :param text: The text that will be in the list for the item
        :param action_data: the action_data that will be sent to the function/method in the 'action'
        """
        self.list_text.append(text)
        self.list_group.append(group)
        self.list_action_data.append(action_data)

    def __list_get(self):
        """
        Loop the user list items and create a text with the whole list
        :return: the text with the list ready to be presented
        """
        result = ''
        ptr = 0
        size = len(self.list_text)
        list_index = {}
        last_group = None

        for item in self.list_text:
            ptr += 1

            index = '/'
            if self.list_prefix is not None:
                index += self.list_prefix

            if size > 9 and ptr < 10:
                index += '0'

            index += str(ptr)

            if self.list_group[ptr - 1] != last_group:
                last_group = self.list_group[ptr - 1]
                if last_group is None:
                    result += f'\n<u><b>OTHERS</b></u>\n'
                else:
                    group_name = self.list_group[ptr - 1].upper()
                    result += f'\n<u><b>{group_name}</b></u>\n'

            result += f'{index}  {item}\n'

            list_index[index] = self.list_action_data[ptr - 1]

        ChatController.user_index_add(self.app, self.chat_id, self.action, list_index)
        # del self.list_text
        # del self.list_action_data

        return result

    def user_input(
            self,
            text,
            action_cancel=None,
            action_cancel_data=None,
            confirmation_text=None,
            multiple_entries=False
    ):

        self.text = text
        self.confirmation_text = confirmation_text
        self.multiple_entries = multiple_entries
        self.action_cancel = action_cancel
        self.action_cancel_data = action_cancel_data

        ChatController.user_input_add(self.app, self.chat_id, self.__input_read)
        self.__input_read(self.app, self.chat_id)

    def __input_read(self, app, chat_id, event_info=None):
        """Method called every time the user send a message expected from the input"""

        text = self.text

        if event_info is not None:
            self.input_result.append(event_info['message_text'])

        if len(self.input_result) > 0:
            text += '\n\n<b>YOUR ANSWER:</b>\n\n'
            for line in self.input_result:
                text += line + '\n'

            if self.confirmation_text is None:
                text += '\n<b>Do you confirm this answer?</b>'
            else:
                text += '\n<b>'+self.confirmation_text+'</b>'

            if self.multiple_entries:
                text += '\n\n<i>You can send another message to add to this answer before confirming</i>'
            else:
                ChatController.user_input_del(app, chat_id)

        if len(self.input_result) == 0:
            self.button_add('Cancel', action=self.__input_canceled, keep_together=True)
        if len(self.input_result) == 1:
            self.button_add('Confirm', action=self.__input_confirmed)

        self.show(text)

    def __input_confirmed(self, app, chat_id, event_info):
        """Method called by the 'CONFIRM' button of the confirmation screen'"""

        # Desativa o input do usuário
        ChatController.user_input_del(app, chat_id)

        event_info['user_input'] = self.input_result
        event_info['user_input_confirmed'] = True
        event_info['action_data'] = self.action_data
        self.action(app, chat_id, event_info)


    def __input_canceled(self, app, chat_id, event_info):
        """Method called by the 'CANCEL' button of the confirmation screen'"""

        # Desativa o input do usuário
        ChatController.user_input_del(app, chat_id)

        event_info['user_input'] = None
        event_info['user_input_confirmed'] = False

        if self.action_cancel is None:
            event_info['action_data'] = self.action_data
            self.action(app, chat_id, event_info)
        else:
            event_info['action_data'] = self.action_cancel_data
            self.action_cancel(app, chat_id, event_info)

    def show(self, text):
        """
        Show the message on telegram.
        The parameter text must include {} to be replaced for the user index list if it is the case
        :param text: The text that is to be shown in the Telegram message.
        """

        # If exists 'text' and user list,
        # insert the user list in the text replacing {}
        if text is not None and len(self.list_text) > 0:
            text = text.format(self.__list_get())
        else:
            if text.find('{}') >= 0:
                text = text.format('\n<i>This list is empty</i>')

        # If exists inline buttons, create the buttons' object
        if self.inline_bt_list is None:
            buttons = None
        else:
            buttons = InlineKeyboardMarkup(self.inline_bt_list)

        print(self.chat_id, text, self.inline_bt_list, buttons)

        if self.message_id is None:
            result = \
                self.app.send_message(
                    self.chat_id,
                    text,
                    parse_mode="html",
                    reply_markup=buttons
                )
        else:
            result = \
                self.app.edit_message_text(
                    self.chat_id,
                    self.message_id,
                    text,
                    parse_mode="html",
                    reply_markup=buttons
                )

        ChatController.msg_btn_add(self.app, self.chat_id, result['message_id'], self.action_list)
        if len(self.list_text) > 0:
            print('passou aqui')
            ChatController.user_index_upd(self.app, self.chat_id, result['message_id'])



# -------------------------------------------------------------------------------
class DataList:

    # chat_list = {}

    def __init__(self, app, chat_id, action, prefix=None):
        self.app = app
        self.chat_id = chat_id
        self.action = action
        self.prefix = prefix
        self.text = []
        self.data = []
        self.message_id = None

    def add(self, text, data):
        self.text.append(text)
        self.data.append(data)

    def get(self):
        result = ''
        ptr = 0
        size = len(self.text)
        list_index = {}

        for item in self.text:
            ptr += 1

            index = '/'
            if self.prefix is not None:
                index += self.prefix

            if size > 9 and ptr < 10:
                index += '0'

            index += str(ptr)
            result += index + '  ' + item + '\n'

            list_index[index] = self.data[ptr-1]

        ChatController.user_index_add(self.app, self.chat_id, self.action, list_index)
        del self.text
        del self.data

        return result

    def show(self, text, message_id=None, reply_markup=None):
        if message_id is None:
            result = \
                self.app.send_message(
                    self.chat_id,
                    text,
                    parse_mode="html",
                    reply_markup=reply_markup
                )
        else:
            result = \
                self.app.edit_message_text(
                    self.chat_id,
                    message_id,
                    text,
                    parse_mode="html",
                    reply_markup=reply_markup
                )

        ChatController.user_index_upd(self.app, self.chat_id, result['message_id'])


# -------------------------------------------------------------------------------
class InlineBt:

    # This class property keeps all the button actions as the routes for the buttons
    # It is the route collection
    routes = {}

    def __init__(self):
        self.inline_bt_list = []

    def add(self,
            caption,
            callback_data=None,
            action=None,
            url=None,
            switch_inline_query=None,
            switch_inline_query_current_chat=None,
            keep_together=False
            ):

        # If exists action for the button, includes the function to the route collection
        # and includes the function's name at the callback_data
        if action is not None:
            InlineBt.routes[action.__qualname__] = action

            if callback_data is None:
                callback_data = action.__qualname__
            else:
                callback_data = action.__qualname__ + '|' + callback_data

        # If this is the first button or this button should not be kept together
        # than creates a new button line
        if len(self.inline_bt_list) == 0 or keep_together is False:
            self.inline_bt_list.append([])

        if callback_data is None:
            callback_data = 'nodata'

        # Include the new button at the last button line
        ptr = len(self.inline_bt_list) - 1
        self.inline_bt_list[ptr].append(
            InlineKeyboardButton(
                caption,
                callback_data=callback_data,
                url=url,
                switch_inline_query=switch_inline_query,
                switch_inline_query_current_chat=switch_inline_query_current_chat
            )
        )

    def get(self):
        return InlineKeyboardMarkup(self.inline_bt_list)


# -------------------------------------------------------------------------------
def get_day_abv(date):
    """Get abbreviated day (daily - showing specific tasks)"""

    day_name = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    today_str = day_name[date.weekday()] + ' ' +\
        str(date.day) + ' ' + \
        calendar.month_name[date.month]

    return today_str


def get_day(date_precision, date):
    """Returns the string version of date"""

    today_str = None

    if date_precision in ('D'):
        today_str = get_day_abv(date) + ' ' + str(date.year)

    elif date_precision in ('W'):
        today_str = date.strftime("%d/%m") #+ " Weekly Task Sheet"

    elif date_precision in ('M'):
        today_str = calendar.month_name[date.month] #+ "'s Monthly Task Sheet"

    elif date_precision == 'T':
        today_str = "Task Pool"

    return today_str


# def setup_entries(app, chat_id, event_info):
#     """Set up new categories, ...habits, tasks"""

    # message_id = event_info['message_id']
    # entry_type = event_info['action_data']['entry_type']
    # action = event_info['action_data']['action_cancel']
    # event_info['action_data']['action'] = create_entry
    #
    # msg = SappoGramMsg(app, chat_id, message_id, action=action, action_data=event_info['action_data'])
    # text = 'Type the name of a new ' + entry_type + ' for every line you send'
    #
    # msg.user_input(text)


def create_entry(app, chat_id, event_info):
    """Add new tasks to a specific task sheet"""

    print(event_info)
    # CHECK ENTRIES
    try:
        entry_type = event_info['entry_type']
        entries = event_info['user_input'][0].split('\n')
    except:
        entries = event_info['user_input'][0].split('\n')
        entry_type = event_info['action_data']['entry_type']

    # if entry_type == 'task':
    #     for field in entries:
    #         task_id = task.create(chat_id, field)
    #         task.schedule(task_id, 1, event_info['action_data']['date'], event_info['action_data']['date_precision'])

    if entry_type == 'habits':
        for field in entries:
            habit.create(id, field)

    elif entry_type == 'categories':
        for field in entries:
            category.create(field, chat_id)


# def setup(app, chat_id, activity):
#
#     if activity == 'habit':
#         result = setup_habits(app, chat_id)
#         return 'setup_habits'
#     elif activity == 'task':
#         result = setup_tasks(app, chat_id)
#         return 'setup_tasks'

def display_activities2(chat_id, fields, action, sheet=None, date=None):
    """Process reply to allow users to complete habits"""

    items = DataList(chat_id=chat_id, action=action)

    for field in fields:
        name = field[0]
        display_name = name
        category_name = field[2]
        if field[2] is not None:
            display_name += '  ( <i>' + category_name +'</i>)'
        items.add(display_name, {'id': field[1], 'sheet': sheet, 'date': date, 'name': name, 'category_name': category_name})

    reply = items.get()

    return reply

