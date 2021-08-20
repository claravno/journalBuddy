# ------------------------------------------------------------
import calendar

from pyrogram import Client
import tgHabits
import tgTasks

from tgCategory import *
from tgGoals import goals
from tgLog import activity_log
from tgTasks import *
from tgHabits import *
from tgEvents import *
from jbTasks import *
from jbHabits import *


# ------------------------------------------------------------

# ----------------------------------------------------------------------------

# event.create(4, "almoçosddd")
# task.delete(10)
# task.locate("meditar")
# task.create(3, "get deleted")

# activity.get_person_id(15)
# task.schedule(17, date.today(), "D", 3)
# date = datetime.datetime(2021, 5, 3)
# activity.reschedule(date, 'M', 5)

# task.schedule(17, datetime.date.today(), "D", activity.get_person_id(17))
# activity.get_person_id(14)
# emotion.locate('happy', 7)


# emotion.register_activity_log(1, event.locate("piscina"))

# emotion.register_daily_notes(1, 1)
# category.create('Exercise', 1, 0)

app = Client(
    "my_bot",
    api_id=4199434,
    api_hash="e5231be682657435783c43f7fed839ed",
    bot_token="1776679098:AAHYHaahgT3V7DskFL5QbReko5KImVzhlv4"
)

ChatController.add_routes(
    {
        "/tasks": all_tasks,
        "/habits": habits,
        "/events": events,
        "/categories": categories,
        "/log": activity_log,
        "/goals": goals
    }
)

my_routes = {
    "/tasks":  all_tasks,
    "/categories": categories,
    "/habits": habits,
    "move": move_task
}

@app.on_message()
def my_handler(client, message):

    chat_id = message["chat"]["id"]
    # print('text',  message["text"], 'message_id', message["message_id"])

    event_info = {
        'user_id': message["from_user"]["id"],
        'message_id': message["message_id"],
        'message_text': message["text"]
    }
    rote_to_go = (message["text"]).lower()

    app.send_chat_action(chat_id, "typing")

    # Identify the command and calls the right function
    if rote_to_go in ChatController.routes:
        ChatController.routes[rote_to_go](
            app=app,
            chat_id=chat_id,
            event_info=event_info
        )
    elif chat_id in ChatController.user_input_routes:
        ChatController.user_input_routes[chat_id](
            app=app,
            chat_id=chat_id,
            event_info=event_info
        )
        app.delete_messages(chat_id, message["message_id"])
    elif chat_id in ChatController.user_index_routes:
        if message["text"] in ChatController.user_index_routes[chat_id]['user_index']:
            event_info['action_data'] = ChatController.user_index_routes[chat_id]['user_index'][message["text"]]
            event_info['message_id'] = ChatController.user_index_routes[chat_id]['message_id']
            ChatController.user_index_routes[chat_id]['action'](
                app=app,
                chat_id=chat_id,
                event_info=event_info
            )
            app.delete_messages(chat_id, message["message_id"])
    else:
        app.send_message(chat_id, 'Olá ' + message["chat"]["first_name"] + '! Eu recebi sua mensagem. Breve vcê poderá se conectar com sua escola.')
        app.send_message(chat_id, 'Mas tenha um pouco de paciência comigo que ainda estou aprendendo a responder')


# -------------------------------------------------------------------------------
@app.on_callback_query()
def my_callback_handler(client, callback):

    chat_id = callback['message']['chat']['id']
    message_id = callback["message"]["message_id"]
    event_info = {
        'message_id': callback["message"]["message_id"],
        'callback_data': callback["data"],
        'user_id': callback["message"]["chat"]["id"]
    }
    rote_to_go = callback["data"].split('|')[0]

    app.send_chat_action(chat_id, "typing")

    if chat_id in ChatController.msg_btn_routes:

        if message_id in ChatController.msg_btn_routes[chat_id]:
            if rote_to_go in ChatController.msg_btn_routes[chat_id][message_id]:
                event_info['action_data'] = ChatController.msg_btn_routes[chat_id][message_id][rote_to_go][
                    'action_data']
                ChatController.msg_btn_routes[chat_id][message_id][rote_to_go]['action'](
                    app=app,
                    chat_id=chat_id,
                    event_info=event_info
                )
    else:

        if rote_to_go in InlineBt.routes:
            InlineBt.routes[rote_to_go](
                app=app,
                chat_id=chat_id,
                event_info=event_info
            )


#@app.on_message()
def __my_handler(client, message):
    """When the bot receives a message"""

    message_text = message["text"]
    id = message["chat"]["id"]
    name = message["chat"]["first_name"]
    msg_id["received"] = message["message_id"]

    who(id, client, name)

    # habits and categories
    # if message_text == '/habits':
    #     users[id]["last"] = "habits"
    #     reply = display_entries(id)
    #     result = tgHabits.habits(app, id, reply)
    #     msg_id["id"] = result["message_id"]
    #     # clean up the users dictionary for uneccessary info
    #     if 'sheet' in users[id]:
    #         users[id].pop("sheet")
    #     if 'activity' in users[id]:
    #         users[id]["activity"] = {}
    # elif message_text == '/categories':
    #     users[id]["last"] = "categories"
    #     reply = display_entries(id)
    #     result = tgHabits.categories(app, id, reply)
    #     msg_id["id"] = result["message_id"]


    # stage 4: display all sheets (DAY) - simplified menu
    # elif message_text == '/tasks':
    #     users[id]["last"] = "sheet"
        # users[id]["sheet"] = "daily"
        # users[id]["date"] = datetime.date.today()
        # # users[id]["activity"] = {}
        # fields = which_sheet3(id)
        # result = tgTasks.all_tasks(app, id, fields[0], fields[1], sheet='daily')
        # msg_id["id"] = result["message_id"]
    if message_text == 'Add all tasks':
        users[id]["last"] = users[id]["sheet"]
        # create_entry(id)
        new_tasks1(id)
        app.delete_messages(id, msg_id["received"])
        update_tasks(id)
        fields = which_sheet3(id)
        result = tgHabits.all_tasks(app, id, fields[0], fields[1], msg_id["id"], users[id]["sheet"])
        msg_id["id"] = result["message_id"]
    elif users[id]["last"] == 'requested':
        garbage.append(message["message_id"])
        if new_entry[id]["type"] in ('habits', 'categories'):
            entry_names(id, message_text)
        else:
            task_names(id, message_text)

    # stage 5: Manipulating tasks in /tasks
    elif users[id]["last"] == "sheet":
        users[id]["activity"] = {}
        users[id]["activity"]["command"] = message_text
        reply = get_reply(id)
        users[id]["activity"]["data"] = tgHabits.task_buttons(app, id, users[id]["sheet"], users[id]["date"], reply, msg_id["id"])
        app.delete_messages(id, msg_id["received"])
    elif users[id]["last"] == "move":
        print(users[id]["sheet"])
        app.delete_messages(id, msg_id["received"])

    # skip
    else:
        message.reply_text('Hello ' + name + '! I got your message! Try using the commands',
                           disable_web_page_preview=True)



#@app.on_callback_query()
def __my_callback_handler(client, callback):
    """Dealing with bot button replies"""

    id = callback["message"]["chat"]["id"]
    data = callback["data"]
    message_id = callback["message"]["message_id"]

    data_split = data.split('_')


    # stage #
    if data == 'new_task':
        result = tgHabits.setup_tasks(app, id)
        msg_id["id"] = result["message_id"]
        users[id]["last"] = 'tasks_requested'

    # stage #
    elif data == 'edit_tasks':
        tgHabits.which_edit(app, id)
        users[id]["last"] = 'edit_tasks'
    elif data == 'create_tasks':
        users[id] = users[id], tgHabits.setup(app, id, 'task')
    elif data == 'tasks_received':
        for x in tasks.get(id):
            task_id = task.create(id, x)
            task.schedule(task_id, 1, users[id][0][0], users[id][0][1], id)
        tasks.pop(id)
        users[id] = 'tasks_added'

    # experimenting with universal add activity (habits + tasks)
    elif data == 'received':
        if new_entry[id]["type"] == 'habits':
            users[id]["last"] = 'habits'
            create_entry(id)
            update_tasks(id)
            reply = display_entries(id)
            tgHabits.habits(app, id, reply, msg_id["id"])
        elif new_entry[id]["type"] == 'categories':
            users[id]["last"] = 'categories'
            create_entry(id)
            update_tasks(id)
            reply = display_entries(id)
            tgHabits.categories(app, id, reply, msg_id["id"])

    # stage 4
    elif data_split[0] in ('daily', 'weekly', 'monthly', 'pool'):
        users[id]["sheet"] = data_split[0]
        if len(data_split) > 1:
            users[id]["date"] = str_to_date(data_split[1])
        else:
            users[id]["date"] = datetime.date.today()
        fields = which_sheet3(id)
        # reply, task
        tgHabits.all_tasks(app, id, fields[0], fields[1], msg_id["id"], data_split[0])
        print(users[id])
    elif data_split[0] == 'request':
        new_entry[id] = {id: {"type":[]}}
        new_entry[id]["type"] = data_split[1]
        if new_entry[id]["type"] == 'tasks':
            users[id]["sheet"] = data_split[2]
            users[id]["date"] = data_split[3]
            result = tgTasks.setup_tasks(app, id)
        # experimenting universal new_entry instead of tasks or habits
        elif new_entry[id]["type"] == 'habits':
            result = tgHabits.setup_habits(app, id)
        elif new_entry[id]["type"] == 'categories':
            # experimenting with universal setup_entries instead of setup_tasks/habits
            result = tgHabits.setup_entries(app, id, new_entry[id]["type"])
        garbage.append(result["message_id"])
        users[id]["last"] = 'requested'

    #stage 5: manipulating task
    elif data == 'complete_today':
        task.complete(users[id]["activity"]["id"])
        tgHabits.add_emotions(app, id, msg_id["id"], users[id]["sheet"])
    elif data == 'move':
        task_name = task.locate_by_id(users[id]["activity"]["id"])[0][0]
        tgTasks.move_task(app, id, msg_id["id"], task_name)
    elif data_split[0] == 'move':
        # # storing original task date
        # users[id]["last_sheet"] = users[id]["sheet"]
        # users[id]["last_date"] = users[id]["date"]
        #calling function to offer more sheet options
        if data_split[2] == "other":
            users[id]["last"] = "move"
            users[id]["sheet"] = data_split[1]
            tgTasks.move_other(app, id, users[id]["sheet"], msg_id["id"])
        # moving task and saving new task date
        else:
            move_task(id, data)
            tgHabits.moved_navigation(app, id, users[id]["last_sheet"], users[id]["last_date"], users[id]["sheet"], users[id]["date"], msg_id["id"])
    elif data == 'task_options':
        reply = get_reply(id)
        tgTasks.task_actions(app, id, users[id]["sheet"], users[id]["date"], reply, msg_id["id"])
    elif data == 'edit_cat':
        result = tgHabits.edit_cat(app, id, users[id]["activity"]["data"])
        garbage.append(result[0]["message_id"])
        msg_id["id"] = result[1]

    # manipulating categories
    elif data == 'create_cat':
        print('time to create some categories!')








app.run()


