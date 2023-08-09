from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import datetime
import random
import json
import pyjokes
import logging
import urllib.request
from googletrans import Translator, LANGUAGES
from database import database


load_dotenv()

# SLACK_BOT_TOKEN is Bot User OAuth Token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
# SLACK_APP_TOKEN is App-Level Tokens (Socket token)
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
app = App(token=SLACK_BOT_TOKEN)


@app.event("app_mention")
def mention_handler(payload):
    user_id = payload['user']
    channel_id = payload['channel']
    texts = f"Hey there ✋! It's TaskBuddy 😽!! In this slack bot 🤖 you can explore 🔎 about your current time + date ⏰, your curious city 🌆, translation your message 💬 to English language 🇺🇸 🤟, telling a joke 🙃 and especially ⛳️ the main mission of TaskBuddy is creating a to-do list app 📒 for you to keep track your tasks and make your work more productively 💓!!! \n Here is list of commands that TaskBuddy can support you:\n ✅ /time : Will display your current date and time \n ✅ /joke : Will tell you a joke \n ✅ /infocity + a_name_of_a_city: Will display information about your requested city \n ✅ /translate + a_message_in_a_lang_not_English : Will translate your message to English \n ✅ /task : Will open an simple task app for you"
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=texts
    )

# ******* Joke command *******


@app.command("/joke")
def jokes_command(ack, body, respond, logger):
    ack()
    logger.info(body)
    joke = pyjokes.get_jokes(language="en", category='all')
    respond(random.choice(joke) + " 🤣 ")

# ******* Time command *******


@app.command("/time")
def time(ack, body, respond, logger):
    ack()
    logger.info(body)
    current_time = datetime.datetime.now()
    texts = f'Today is: {str(current_time.month)}/{str(current_time.day)}/{str(current_time.year)}. \nTime: {str(current_time.hour)}:{str(current_time.minute)}:{str(current_time.second)}'
    respond(texts)

# ******* Info city command *******


@app.command("/infocity")
def info_city(ack, body, respond, logger):
    ack()
    logger.info(body)
    params = body['text'].strip()
    params = params.split()
    params = "+".join(params)
    req = urllib.request.Request(
        f'https://geocoding-api.open-meteo.com/v1/search?name={params}&count=1&language=en&format=json')
    res = urllib.request.urlopen(req)

    data = json.loads(res.read().decode())
    if not 'results' in data:
        respond("Requested city not exist!")
        return
    data_shown = [data['results'][0]['name'], data['results']
                  [0]['country'], data['results'][0]['timezone']]

    # data['results'][0]['name'], data['results'][0]['latitude'], data['results'][0]['longitude'], data['results'][0]['country'], data['results'][0]['timezone'], data['results'][0]['population']

    lat, lon = data['results'][0]['latitude'], data['results'][0]['longitude']

    req = urllib.request.Request(
        f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&current_weather=true&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto')

    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode())
    data_shown.append(data['current_weather']['temperature'])
    data_shown.append(data['current_weather']['windspeed'])
    data_shown.append(datetime.datetime.fromisoformat(
        data['current_weather']['time']).strftime("%B %d, %Y %I:%M %p"))
    data_shown.append(datetime.datetime.fromisoformat(
        data['daily']['sunrise'][0]))
    data_shown.append(datetime.datetime.fromisoformat(
        data['daily']['sunset'][0]))

    with open(os.path.join(os.getcwd(), "format", "message.json"), 'r') as fh:
        blocks = json.load(fh)

    for i, val in enumerate(data_shown):
        blocks['blocks'][1]['fields'][i]['text'] += str(val)

    user_id = body['user_id']
    channel_id = body['channel_id']
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        blocks=blocks['blocks']
    )

# ******* Translate command *******


@app.command("/translate")
def translate(ack, body, respond, logger):
    ack()
    logger.info(body)
    translator = Translator()
    # Auto-detect the source language
    params = body['text'].strip()
    detected_language = translator.detect(params).lang
    texts = (f"Your language is: {LANGUAGES[detected_language].upper()}")
    respond(texts)
    # Translate the message to English
    translated_message = translator.translate(
        params, src=detected_language, dest='en').text
    texts = (
        f'Translated your message "{params}" to English is "{translated_message}"')
    respond(texts)

# ************************************************************
# **********************  TO-DO LIST APP *********************
# ************************************************************


def display_current_tasks(user_id, channel_id):
    currentTaskList = json.loads(database("read", user_id)[3])
    with open(os.path.join(os.getcwd(), "format", "updatetask.json"), 'r') as fh:
        blocks = json.load(fh)

    if len(currentTaskList) == 0:
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="No task now 🥳"
        )

    else:
        newOpitionList = []
        for i in range(len(currentTaskList)):
            with open(os.path.join(os.getcwd(), "format", "option.json"), 'r') as fh:
                option = json.load(fh)
                option["text"]["text"] = option["value"] = currentTaskList[i] + " 👈"
                newOpitionList.append(option)
        blocks["blocks"][4]['elements'][0]['options'] = newOpitionList

    # welcome back {username}
    blocks['blocks'][0]['text']['text'] += ", " + \
        database("read", user_id)[1] + "👋"
    # number of current tasks
    blocks['blocks'][1]['text']['text'] += str(len(currentTaskList)) + " ✅"
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        blocks=blocks['blocks']
    )

# ******* task app command *******


@app.command("/task")
def taskApp(ack, body, logger, user_id=None, channel_id=None):
    ack()
    logger.info(body)
    if user_id == None and channel_id == None:
        user_id = body['user_id']
        channel_id = body['channel_id']
    userData = database("read", user_id)
    if userData:
        isActive = userData[4]
        if not isActive:
            with open(os.path.join(os.getcwd(), "format", "signin.json"), 'r') as fh:
                blocks = json.load(fh)
                app.client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    blocks=blocks['blocks']
                )
        else:
            display_current_tasks(user_id, channel_id)
    else:  # no account yet
        with open(os.path.join(os.getcwd(), "format", "signup.json"), 'r') as fh:
            blocks = json.load(fh)
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                blocks=blocks['blocks']
            )


# ################# SIGN UP #################
usernameSignUp, passwordSignUp = "", ""


@app.action("username-signup")
def handle_username_signup(ack, body):
    ack()
    global usernameSignUp
    usernameSignUp = body['actions'][0]['value']


@app.action("password-signup")
def handle_password_signup(ack, body):
    ack()
    global passwordSignUp
    passwordSignUp = body['actions'][0]['value']


@app.action("submit-signup-button")
def handle_submit_signup_button(ack, body):
    ack()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    database("create", user_id, usernameSignUp, passwordSignUp, [], True)
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text="You successfully signed up 🎉"
    )
    database("update", userId=user_id, isActive=True)
    display_current_tasks(user_id, channel_id)


@app.action("sign-in-exist-account-button")
def handle_sign_in_exist_account_button(ack, body, logger):
    ack()
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        with open(os.path.join(os.getcwd(), "format", "signin.json"), 'r') as fh:
            blocks = json.load(fh)
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=blocks['blocks']
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)


# ################# SIGN IN #################
usernameSignIn, passwordSignIn = "", ""


@app.action("username-signin")
def handle_username_signin(ack, body):
    ack()
    global usernameSignIn
    usernameSignIn = body['actions'][0]['value'].strip()


@app.action("password-signin")
def handle_password_signin(ack, body):
    ack()
    global passwordSignIn
    passwordSignIn = body['actions'][0]['value'].strip()


@app.action("submit-signin-button")
def handle_submit_signin_button(ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    userData = database("read", user_id)
    if userData:  
        userData = database("read", userId=user_id)
        if not userData:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Your account doesn't exist. Please sign up ✅"
            )
            return
        sysUsername, sysPassword = userData[1], userData[2]
        if sysUsername == usernameSignIn and sysPassword == passwordSignIn:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="You successfully signed in 🎉"
            )

            database("update", userId=user_id, isActive=True)
            display_current_tasks(user_id, channel_id)
        else:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Your username or password is not correct ❌ Please try again!"
            )
    else:
        taskApp(ack, body, logger, user_id, channel_id)

@app.action("sign-up-lost-button")
def handle_signup_lost_button(ack, body, logger):
    ack()
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        userData = database("read", userId=user_id)
        if userData:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Your account already existed with this slack bot. Please stay in sign-in form ✅"
            )
            return
        with open(os.path.join(os.getcwd(), "format", "signup.json"), 'r') as fh:
            blocks = json.load(fh)
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=blocks['blocks']
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)

# ################# SIGN OUT #################


@app.action("signout-button")
def handle_signout_button(ack, body, logger):
    ack()
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )

            taskApp(ack, body, logger, user_id, channel_id)
            return

        database("update", userId=user_id, isActive=False)
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="You successfully signed out ✅"
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)


# ################# UPDATE TASK #################


@app.action("new-task-action")
def handle_new_task_action(ack, body, logger):
    ack()
    logger.info(body)
    new_task = body['actions'][0]['value'].strip()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    currentTaskList = json.loads(database("read", user_id)[3])

    # check if there is duplicate tasks
    if new_task in currentTaskList:
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="New task already exists ✋"
        )
        return
    # *****  update database  ******
    currentTaskList.append(new_task)
    database("update", user_id, updateTaskList=currentTaskList)

    # *****  update UI  ******
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text="Your task(s) has been updated ✅"
    )
    display_current_tasks(user_id, channel_id)


@app.action("new-task-button")
def handle_new_task_button(ack, body, logger):
    ack()
    logger.info(body)
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )
            taskApp(ack, body, logger, user_id, channel_id)
            return

        currentTaskList = json.loads(database("read", user_id)[3])
        # check if over 10 tasks
        if len(currentTaskList) == 10:
            texts = ("I'm sorry because the max adding tasks allow is 10. Also it's not a good idea to have so many tasks. Try to complete one of them before moving foward ✅")
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=texts
            )
            return
        with open(os.path.join(os.getcwd(), "format", "newtask.json"), 'r') as fh:
            task = json.load(fh)
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=task['blocks']
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)

# ################# EDIT AND DELETE TASK #################
targetList = []  # contain values of selected tasks
selectedList = []  # for check number of selected tasks


@app.action("checkbox-action")
def handle_checkbox_action(ack, body, logger):
    ack()
    logger.info(body)
    # check length of selected_options
    global selectedList
    selectedList = body['actions'][0]['selected_options']
    # get values what to remove or edit
    global targetList
    targetList = []
    for i in range(len(selectedList)):
        selectedValue = selectedList[i]['value'].replace("👈", "")
        targetList.append(selectedValue.strip())

# ********** EDIT TASKS *************


@app.action("edit-task-action")
def handle_edit_task_action(ack, body, logger):
    ack()
    logger.info(body)
    user_id = body["user"]["id"]
    currentTaskList = json.loads(database("read", user_id)[3])
    update_task = body['actions'][0]['value'].strip()
    channel_id = body['channel']['id']
    if update_task in currentTaskList:
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="New task already existed ✋"
        )
        return
    global targetList
    for target in targetList:
        index = currentTaskList.index(target)
        currentTaskList[index] = update_task
    # update database
    database("update", userId=user_id, updateTaskList=currentTaskList)
    # update UI
    app.client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text="Your task(s) has been updated ✅"
    )

    targetList = []
    display_current_tasks(user_id, channel_id)


@app.action("edit-button")
def handel_edit_button(ack, body, logger):
    ack()
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )

            taskApp(ack, body, logger, user_id, channel_id)
            return

        if len(targetList) == 0:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please select one task to edit ✅"
            )
            return
        if len(targetList) > 1:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Sorry! I can only support editing one task at a time ✅"
            )
            return
        for target in targetList:
            with open(os.path.join(os.getcwd(), "format", "edittask.json"), 'r') as fh:
                task = json.load(fh)
            task['blocks'][0]["label"]["text"] += ': "' + target + '"'
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                blocks=task['blocks']
            )
    else:
        taskApp(ack, body, logger, user_id, channel_id)


# ********** DELETE TASKS *************
@app.action("delete-button")
def handel_delete_button(ack, body, logger):
    ack()
    channel_id = body['channel']['id']
    user_id = body["user"]["id"]
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )

            taskApp(ack, body, logger, user_id, channel_id)
            return

        currentTaskList = json.loads(database("read", user_id)[3])

        with open(os.path.join(os.getcwd(), "format", "updatetask.json"), 'r') as fh:
            blocks = json.load(fh)

        # welcome command
        blocks['blocks'][0]['text']['text'] += ", " + \
            database("read", user_id)[1] + "👋"

        global targetList
        if len(targetList) == 0:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please select at least task to be done✅"
            )
            return
        elif len(currentTaskList) == 0:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Task is empty now 🥳"
            )
            blocks['blocks'][1]['text']['text'] += "0 ✅"
        else:
            updateUI = True
            # not allow to delete all items so can not update UI
            if len(selectedList) == len(currentTaskList):
                app.client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text="Yayy. You got everything. Good job!🎉🎉🎉"
                )
                updateUI = False
            for target in targetList:
                try:
                    currentTaskList.remove(target)
                except ValueError:
                    app.client.chat_postEphemeral(
                        channel=channel_id,
                        user=user_id,
                        text="Your selected item(s)s no longer exist!"
                    )
                    return

            targetList = []

            # ***** update database ******
            database("update", user_id, updateTaskList=currentTaskList)

            if updateUI:
                # *****  update UI  ******
                newOpitionList = []
                for i in range(len(currentTaskList)):
                    with open(os.path.join(os.getcwd(), "format", "option.json"), 'r') as fh:
                        option = json.load(fh)
                        option["text"]["text"] = option["value"] = currentTaskList[i] + " 👈"
                        newOpitionList.append(option)
                blocks["blocks"][4]['elements'][0]['options'] = newOpitionList

            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Your task(s) has been updated ✅"
            )
        # # of current task
        blocks['blocks'][1]['text']['text'] += str(len(currentTaskList)) + " ✅"
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=blocks['blocks']
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)


# ********** CHANGE USERNAME OR/AND PASSWORD *************
usernameChange, passwordChange = "", ""


@app.action("home-button")
def handle_home_button(ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )
            taskApp(ack, body, logger, user_id, channel_id)
            return

        display_current_tasks(user_id, channel_id)
    else:
        taskApp(ack, body, logger, user_id, channel_id)


@app.action("update-un-pw-button")
def handle_update_username_password_button(ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )

            taskApp(ack, body, logger, user_id, channel_id)
            return

        userData = database("read", userId=user_id)
        sysUsername, sysPassword = userData[1], userData[2]

        if usernameChange != "" and usernameChange != sysUsername:
            sysUsername = usernameChange
            database("update", userId=user_id, username=sysUsername)
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Successfully update your new username ✅"
            )

        if passwordChange != "" and passwordChange != sysPassword:
            sysPassword = passwordChange
            database("update", userId=user_id, password=passwordChange)
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Successfully update your new password ✅"
            )

        display_current_tasks(user_id, channel_id)
    else:
        taskApp(ack, body, logger, user_id, channel_id)


@app.action("change-button")
def handle_change_username_password_button(ack, body, logger):
    ack()
    user_id = body["user"]["id"]
    channel_id = body['channel']['id']
    userData = database("read", user_id)
    if userData:
        isActive = database("read", user_id)[4]
        if not isActive:
            app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Please sign in to continue ✅ ✅ ✅ ✅"
            )
            taskApp(ack, body, logger, user_id, channel_id)
            return
        with open(os.path.join(os.getcwd(), "format", "changeusernamepassword.json"), 'r') as fh:
            blocks = json.load(fh)

        userData = database("read", userId=user_id)
        sysUsername, sysPassword = userData[1], userData[2]
        blocks["blocks"][0]["label"]["text"] += '"'+sysUsername+'"'
        blocks["blocks"][1]["label"]["text"] += '"'+sysPassword+'"'
        app.client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            blocks=blocks['blocks']
        )
    else:
        taskApp(ack, body, logger, user_id, channel_id)


@app.action("change-username")
def handle_change_username(ack, body):
    ack()
    global usernameChange
    usernameChange = body['actions'][0]['value'].strip()


@app.action("change-password")
def handle_change_password(ack, body):
    ack()
    global passwordChange
    passwordChange = body['actions'][0]['value'].strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
