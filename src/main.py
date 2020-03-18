#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime
import json
import os


from telegram import (ReplyKeyboardMarkup,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, CallbackContext)
from database import Database


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)

# initialization of database (same folder)
DB = Database("database.json")
DB.init_json()

# Variables
TIMER_TEST_MODE = True
BOT_HTTP_TOKEN = os.environ.get('schuldestmirbot')

# Range Array for conversation handler
[USER_SELECTION, CATEGORY_SELECTION,
 AMOUNT_SELECTION, CALENDAR_SELECTION,
 CHOOSING_DEBT, ASK_IF_DEBT_IS_PAID,
 CHOOSING_CLAIM, ASK_IF_CLAIM_IS_PAID] = range(8)

UPDATER = Updater(BOT_HTTP_TOKEN, use_context=True)



def start(update, context):
    """handles /start command,
    user registration
    """
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    chat_id = str(update.effective_message.chat_id)

    is_registrated = DB.user_exists(chat_id)

    # sends keyboard to existing users
    if is_registrated:
        update.message.reply_text(
            "Hey " + first_name + "!" + "\nWillkommen zurück!"+"\U0001F609",
            reply_markup=get_start_keyboard())

    # user not registrated
    else:
        # welcome message, new users
        update.message.reply_text(
            "Hey " + first_name + "!" +
            "\nWillkommen bei Deinem lokalen Anbieter für Schuldeneintreibung!" +
            "\U0001F609")

        # Asks user to setup his username
        if username is None:
            update.message.reply_text(
                "Achtung: Um unseren Service nutzen zu können, benötigst du einen Telegram Username.\n"
                "Diesen kannst du unter \"Einstellungen -> Benutzername\" festlegen.\n"
                "Du kannst dich anschließend mit /start registrieren!")

            # Registration

        else:

            # yes / no keyboard
            keyboard_yn = [[InlineKeyboardButton("\U0001F44D", callback_data="yes"),
                            InlineKeyboardButton("\U0001F44E", callback_data="no")]]
            reply_markup = InlineKeyboardMarkup(keyboard_yn)

            update.message.reply_text(
                "Möchtest Du dich registrieren?", reply_markup=reply_markup)

            UPDATER.dispatcher.add_handler(
                CallbackQueryHandler(handle_registration_response))


def start_menu(update, context):
    """Start menu to select what you want to do (enter debts, - settle)
    """

    query = update.callback_query
    bot = context.bot
    # get ChatId
    chat_id = str(query.from_user.id)

    bot.edit_message_text(
        # generate startmenu
        chat_id=chat_id,
        message_id=query.message.message_id,
        text="Bitte wähle dein Anliegen aus:\n")

    context.bot.send_message(
        chat_id, text="Klicke auf \u27A1 /schuld um Schulden einzutragen...\n"
        "Klicke auf \u27A1 /ichSchulde um einzusehen, wem du was schuldest..."
        "\nKlicke auf \u27A1 /ichBekomme um einzusehen, was dir wer schuldet...",
        reply_markup=get_start_keyboard())


def get_start_keyboard():
    """Returns the main menu keyboard
    """

    return ReplyKeyboardMarkup([["/schuld"], ["/ichBekomme"], ["/ichSchulde"]])


def handle_registration_response(update, context):
    """checks wether user wants to be registered or not
    """

    query = update.callback_query

    # user clicks yes and will be registered
    if query.data == "yes":
        start_menu(update, context)
        chat_id = str(query.message.chat_id)
        user_name = str(query.from_user.username)
        DB.add_user(chat_id, user_name)

    # otherwise cancel
    elif query.data == "no":
        cancel(update, context)


def cancel(update, context):  # abbruch in  cancel!!!!!!
    """close the chat
    """
    query = update.callback_query
    bot = context.bot
    # Closing text
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Schade!" +
        "\nFalls Du es dir anders überlegst, kannst du mit /start den Prozess neu starten." +
        "\U0001F47C"
    )
    return ConversationHandler.END


def _parse_time_(time):
    """
    Conversion of the Deadline string to datetime object
    Params: string time
            Format: "YYYY:MM:DD"
    """
    year = int(time[0] + time[1] + time[2] + time[3])
    month = int(time[5] + time[6])
    day = int(time[8] + time[9])
    due = datetime.datetime(year, month, day)
    return due

# unnötig, wird nicht mehr verwendet
# def _days_left_(deadline):
#    """
#    Calculates the amount of time between now and a given point in time
#    Params: datetime deadline
#    """
#    now = datetime.datetime.now()
#    delta = deadline - now
#    return delta.days


def _callback_alarm(context: CallbackContext):
    """
    Sends a message once the timer is triggered
    Params: CallbackContext context
    """
    cur_debt = context.job.context

    debt_id = cur_debt.debt_id  # todo unused variable
    creditor_cid = cur_debt.creditor
    debtor_cid = cur_debt.debtor
    deadline_time = _parse_time_(cur_debt.deadline)
    debt_text = str(cur_debt.amount) + " " + cur_debt.category

    deadline = deadline_time.strftime("%d.%m.%Y")

    # todo not needed
    # if _days_left_(deadline_time) < 0:      #Checks whether the debts deadline has been reached
    #    context.job.schedule_removal()

    context.bot.send_message(creditor_cid, text=str(DB.get_user_by_chat_id(
        debtor_cid).name) + " schuldet dir noch " + str(debt_text) + " bis zum " + deadline)
    context.bot.send_message(debtor_cid, text="Du schuldest " + str(DB.get_user_by_chat_id(
        creditor_cid).name) + " noch " + str(debt_text) + " bis zum " + deadline)


def start_timer(tele_updater: UPDATER, debt_id):
    """
    Starts the timer with a corresponding debt
    Params: UPDATER tele_updater
            string debt_id
    """

    cur_debt = DB.get_debt_by_debt_id(debt_id)
    # Gets the current job queue of the dispatcher
    queue = tele_updater.dispatcher.job_queue

    time_zone = datetime.datetime.now().astimezone().tzinfo
    time = datetime.time(hour=10, minute=0, second=0, tzinfo=time_zone)

    test_interval = 20  # sets the time for TEST_MODE in seconds

    if TIMER_TEST_MODE:  # TEST_MODUS renamed to TEST_MODE
        queue.run_repeating(_callback_alarm, test_interval,
                            0, context=cur_debt)

    else:
        queue.run_daily(_callback_alarm, time, context=cur_debt)


def stop_timer(tele_updater: UPDATER, debt_id):
    """
    Schedules the removal of a specific timer
    Returns true on success
    Params: UPDATER tele_updater
            string debt_id

    """
    queue = tele_updater.dispatcher.job_queue

    for ajob in queue.jobs():  # Iterates through all available jobs
        jobdebt_id = ajob.context.debt_id
        if jobdebt_id == debt_id:
            ajob.schedule_removal()
            return True
    return False

# endregion

# region settle debts


def i_owe(update, context):
    """Responds to "/ichSchulde" command,
    starts the conversation flow allowing the user to view and cancel pending debts.

    Arguments:
        update, context

    Returns:
        CHOOSING_DEBT {int} -- debts are existent, new state for conversation handler
        ConversationHandler.END -- no debts are pending

    """

    chat_id = update.effective_message.chat.id
    debts = DB.get_open_debts(str(chat_id))

    if not send_debt_list_to_user(update, debts, "Hier siehst du deine Schulden"):
        return ConversationHandler.END

    return CHOOSING_DEBT


def send_debt_list_to_user(update, debts, text):
    """Sends a list of pending debts or displays a message if no debts are pending.

    Arguments:
        update
        debts {list} -- pending debts of user
        text {String} -- display message for inline keyboard

    Returns:
        True -- debt list was sent
        False -- no pending debts exist
    """

    if len(debts) == 0:
        update.effective_message.reply_text(
            "Es sind keine offenen Einträge vorhanden")
        return False

    buttons = []

    for debt in debts:
        date_parts = debt.deadline.split(":")
        deadline = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
        buttons.append(
            [
                InlineKeyboardButton(
                    f'{debt.category} an '
                    f'{DB.get_user_by_chat_id(debt.creditor).name} bis {deadline}',
                    callback_data=debt.debt_id)
            ]
        )

    update.effective_message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(buttons))

    return True


def handle_choosing_debt(update, context):
    """Handles debt buttons, calls ask_if_debt_paid(), returns new state for conversation handler

    Arguments:
        update, context

    Returns:
        ASK_IF_DEBT_IS_PAID -- new state for conversation handler
    """

    ask_if_debt_paid(update)
    return ASK_IF_DEBT_IS_PAID


def handle_ask_if_debt_is_paid(update, context):
    '''Allows the user to mark any of his debts as paid.
    The creditor will be asked for his approval.

    Arguments:
        update, context

    Returns:
        ConversationHandler.END -- call to end the conversation handling
    '''

    update_data = json.loads(update.callback_query.data)

    is_paid = update_data['paid']
    debt_id = update_data['id']

    debt = DB.get_debt_by_debt_id(debt_id)
    creditor = DB.get_user_by_chat_id(debt.creditor).name
    debtor = DB.get_user_by_chat_id(debt.debtor).name

    data_yes = json.dumps({'action': 'debt_paid', 'paid': True, 'id': debt_id})
    data_no = json.dumps({'action': 'debt_paid', 'paid': False, 'id': debt_id})

    print(data_yes, data_no)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('\U0001F44D', callback_data=data_yes),
                                      InlineKeyboardButton('\U0001F44E', callback_data=data_no)]])

    if is_paid:
        update.effective_message.edit_text(
            f'{creditor} wird verständigt.')

        date_parts = debt.deadline.split(":")
        deadline = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"

        context.bot.send_message(
            chat_id=debt.creditor,
            text=f'Wurde die Schuld über {debt.category} mit der'
            f' Frist zum {deadline} von {debtor} beglichen?',
            reply_markup=keyboard)

    else:
        update.effective_message.edit_text('Ok')

    return ConversationHandler.END


def ask_if_debt_paid(update):
    '''Sends a message to the user asking if he already paid the chosen debt or not.

    Arguments:
        update

    Returns:

    '''

    data_yes = json.dumps({'paid': True, 'id': update.callback_query.data})
    data_no = json.dumps({'paid': False, 'id': update.callback_query.data})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('\U0001F44D', callback_data=data_yes),
                                      InlineKeyboardButton('\U0001F44E', callback_data=data_no)]])

    update.effective_message.edit_text(
        'Hast du die Schuld bereits beglichen?', reply_markup=keyboard)


def handle_accept_debt_is_paid(update, context):
    '''Handles the 'yes'/'no' buttons on the creditors side.
    On confirmation the debt will be marked as paid,
    otherwise the user gets notified that the creditor declined his request.

    Arguments:
        update, context

    Returns:
        ConversationHandler.END -- call to end the conversation handling

    '''

    update_data = json.loads(update.callback_query.data)

    is_paid = update_data['paid']
    debt_id = update_data['id']

    debt = DB.get_debt_by_debt_id(debt_id)

    DB.set_paid(debt_id, is_paid)

    if is_paid:
        update.effective_message.edit_text(
            'Die Schuld ist nun als beglichen markiert.')

        stop_timer(UPDATER, debt_id)

    else:
        update.effective_message.edit_text(
            'Der Schuldner wurde benachrichtigt. Die Schuld ist noch nicht beglichen.')
        context.bot.send_message(
            chat_id=debt.debtor,
            text=f'{DB.get_user_by_chat_id(debt.creditor).name}'
            f' hat deine Anfrage zum Begleichen von {debt.category} nicht akzeptiert.')

    return ConversationHandler.END


def i_get(update, context):
    '''responds to '/ichBekomme' command,
    starts the conversation flow allows the user to view and cancel pending claims.
    Arguments:
        update, context

    Returns:
        CHOOSING_CLAIM {int} -- claims are existent, new state for conversation handler 
        ConversationHandler.END -- no claims are pending
    '''

    # error CallbackContext has no attribute effective_message
    chat_id = update.effective_chat.id
    claims = DB.get_open_claims(str(chat_id))

    if not send_claim_list_to_user(update, claims, 'Hier siehst du, was dir noch geschuldet wird'):
        return ConversationHandler.END

    return CHOOSING_CLAIM


def handle_choosing_claim(update, context):
    '''Handles claim buttons, calls ask_if_claim_paid(), returns new state for conversation handler

    Arguments:
        update, context

    Returns:
        ASK_IF_CLAIM_IS_PAID -- new state for conversation handler
    '''

    ask_if_claim_paid(update)
    return ASK_IF_CLAIM_IS_PAID


def handle_ask_if_claim_is_paid(update, context):
    '''Allows the user (creditor) to cancel any of his claims (set as paid)

    Arguments:
        update, context

    Returns:
        ConversationHandler.END -- call to end the conversation handling
    '''

    update_data = json.loads(update.callback_query.data)
    is_paid = update_data['paid']

    DB.set_paid(update_data['id'], is_paid)

    if is_paid:
        update.effective_message.edit_text(
            'Die Schuld wurde als beglichen markiert')
        stop_timer(UPDATER, update_data['id'])
    else:
        update.effective_message.edit_text('Ok')

    return ConversationHandler.END


def send_claim_list_to_user(update, claims, text):
    '''Sends a list of pending claims or a message if no claims are pending.

    Arguments:
        update
        claims {list} -- pending claims of user
        text {String} -- display message for inline keyboard

    Returns:
        True -- claim list was sent
        False -- no pending claims exist
    '''

    if len(claims) == 0:
        update.effective_message.reply_text(
            'Es sind keine offenen Einträge vorhanden')
        return False
    buttons = []
    for debt in claims:
        date_parts = debt.deadline.split(":")
        deadline = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"

        buttons.append([InlineKeyboardButton(
            f'{debt.category} von  {(DB.get_user_by_chat_id(debt.debtor)).name} '
            f'bis {deadline}',
            callback_data=debt.debt_id)])

    update.effective_message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(buttons))
    return True


def ask_if_claim_paid(update):
    '''Sends a message to the user (creditor) asking if the claim was already paid.

    Arguments:
        update

    Returns:

    '''

    data_yes = json.dumps({'paid': True, 'id': update.callback_query.data})
    data_no = json.dumps({'paid': False, 'id': update.callback_query.data})

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('\U0001F44D', callback_data=data_yes),
                                      InlineKeyboardButton('\U0001F44E', callback_data=data_no)]])

    update.effective_message.edit_text(
        'Wurde die Schuld bereits beglichen?', reply_markup=keyboard)
# endregion

# region define debt

### helper methods ###


def cancel_define_debt(update, context):
    """
    deletes user data
    ends conversation handler thread
    """
    context.user_data.clear()
    update.message.reply_text(
        "Breche ab....", reply_markup=get_start_keyboard())
    return ConversationHandler.END


def is_user(user):
    """
    returns True if "user" is part of registered user list
    """
    for _, listobject in enumerate(get_user_list()):
        if listobject[1] == user:
            return True
    return False


def get_chat_id(user):
    """
    returns the chat id of "user" by accessing user list array
    """
    for _, listobject in enumerate(get_user_list()):
        if listobject[1] == user:
            return listobject[0]
    return ""


def get_user_list():
    """
    returns array of user tuples with chat id and username
    """
    users = []
    for user in DB.users:
        users.append([user.chat_id, user.name])
    return users


### conversation handler methods ###

def new_debt(update, context):
    """
    called with /schuld command
    sends keyboard with registered users to choose from
    """
    context.user_data.clear()
    reply_keyboard = [["Abbrechen ✖"]]
    for _, user in enumerate(get_user_list()):  # adds every user to array
        # makes sure active user does not get listed
        if update.effective_chat.id != int(user[0]):
            reply_keyboard.append(["👤 " + user[1]])
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Bitte wähle einen Benutzer aus:", reply_markup=markup)
    return USER_SELECTION


# region user

def user_selection(update, context):
    """
    called when user has been chosen
    --> checks if user is valid
    --> sends category keyboard
    """
    text = str(update.message.text).replace("👤 ", "")

    if is_user(text) and int(get_chat_id(text)) != update.effective_chat.id:
        context.user_data["debtor"] = text

        reply_keyboard = [
            ["Getränke 🍻", "Essen 🍕", "Mobilität 🚗"],
            ["Gefallen 🧞", "Haushalt 🏘", "Geld 💸"],
            ["Zurück ↩‍", "Sonstiges 🧳", "Abbrechen ✖"]
        ]

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            f"In welcher Kategorie schuldet dir '{context.user_data['debtor']}' etwas?",
            reply_markup=markup)

        return CATEGORY_SELECTION

    update.message.reply_text(
        f"Tut uns leid, aber wir konnten '{text}' leider nicht in unserer Datenbank finden."
        "\nDu kannst es aber gerne erneut versuchen.")

    return USER_SELECTION


# endregion

# region category

def category_selection_back(update, context):
    """
    removes debtor from userdata
    goes back to user selection (far back to type selection)
    """

    if "debtor" in context.user_data:
        del context.user_data["debtor"]

    new_debt(update, context)

    return USER_SELECTION


def category_type_manual(update, context):
    """
    called when manual category selection has been chosen
    --> sends manual category selection message
    """
    update.message.reply_text("Bitte gebe eine Kategorie ein:")
    return CATEGORY_SELECTION


def category_type_one(update, context):
    """
    called when category from type one has been chosen
    --> sends amount keyboard with € values
    """

    context.user_data["debt"] = update.message.text.replace(
        " 🍻", "").replace(" 🍕", "").replace(" 🧞", "").replace(
            " 🏘", "").replace(" 💸", "")

    reply_keyboard = [["1€", "2€", "3€"],
                      ["5€", "7.5€", "10€"],
                      ["Zurück ↩‍", "Sonstiges 📝", "Abbrechen ✖"]]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Welchen Wert schuldet dir {context.user_data['debtor']} "
                              f"in Kategorie {context.user_data['debt']}?", reply_markup=markup)

    return AMOUNT_SELECTION


def category_type_two(update, context):
    """
    called when category from type two has been chosen
    --> sends amount keyboard with km values
    """
    context.user_data["debt"] = update.message.text.replace(" 🚗", "")
    reply_keyboard = [["1km", "2km", "5km"],
                      ["10km", "20km", "50km"],
                      ["Zurück ↩‍", "Sonstiges", "Abbrechen ✖"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Welchen Wert schuldet dir {context.user_data['debtor']} "
                              f"in Kategorie {context.user_data['debt']}?", reply_markup=markup)
    return AMOUNT_SELECTION


# endregion

# region amount

def amount_selection_back(update, context):
    """
    deletes debt from userdata
    goes back to category selection
    """
    if "debt" in context.user_data:
        del context.user_data["debt"]

    reply_keyboard = [
        ["Getränke 🍻 ", "Essen 🍕", "Mobilität 🚗"],
        ["Gefallen 🧞", "Haushalt 🏘", "Geld 💸"],
        ["Zurück ↩‍", "Sonstiges 🧳", "Abbrechen ✖"]
    ]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(
        f"In welcher Kategorie schuldet dir **{context.user_data['debtor']}** etwas?",
        reply_markup=markup)

    return CATEGORY_SELECTION


def amount_selection_manual(update, context):
    """
    called when manual amount selection has been chosen
    --> sends manual amount selection message
    """
    update.message.reply_text("Bitte gebe eine Anzahl ein:")
    return AMOUNT_SELECTION


def amount_selection(update, context):
    """
    called when amount has been selected
    --> sends calendar keyboard
    """
    amount = update.message.text
    context.user_data["amount"] = amount
    reply_keyboard = [["Heute", "Morgen"],
                      ["Eine Woche", "Zwei Wochen"],
                      ["Ein Monat", "3 Monate"],
                      ["Sonstiges 🗓"],
                      ["Zurück ↩‍", "Abbrechen ✖"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        f"Bis wann soll {context.user_data['debtor']} die Schuld beglichen haben?",
        reply_markup=markup)
    return CALENDAR_SELECTION


# endregion

# region calendar

def calendar_selection_back(update, context):
    """
    removes amount from userdata
    goes back to amount selection (type one!)
    """
    if "amount" in context.user_data:
        del context.user_data["amount"]
    reply_keyboard = [["1€", "2€", "3€"],
                      ["5€", "7.5€", "10€"],
                      ["Zurück  ↩", "Sonstiges 📝", "Abbrechen ✖"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Welchen Wert Schuldet dir {context.user_data['debtor']} "
                              f"in Kategorie {context.user_data['debt']}?", reply_markup=markup)
    return AMOUNT_SELECTION


def calendar_selection_manual(update, context):
    """
    called when manual calendar selection has been chosen
    --> sends manual calendar selection message
    """
    update.message.reply_text(
        "Bitte gebe ein gültiges Datum ein (dd.mm.yyyy):")
    return CALENDAR_SELECTION


def calendar_selection(update, context):
    """
    called when date has been selected
    --> saves schuld
    --> sends accept message
    --> ends conversation handler thread
    """
    deadline = update.message.text

    # checks if date is correct
    date = date_handler(deadline)
    if date is None:
        update.message.reply_text(
            f"Fehler: Konnte '{deadline}' nicht als Datum einordnen."
            "\nGebe 'Abbrechen' ein, um den Vorgang zu beenden."
            "\nBitte gebe ein gültiges Datum ein (dd.mm.yyyy):")
        return CALENDAR_SELECTION

    if date == "wrong_timeframe":
        update.message.reply_text(
            f"Fehler: '{deadline}' liegt nicht innerhalb des gültigen Zeitraums."
            "\nBitte Wähle einen Zeitpunkt innerhalb des nächsten Jahres aus.")
        return CALENDAR_SELECTION

    # sends overview of the debt
    creditor_id = str(update.message.from_user.id)
    debtor_id = get_chat_id(context.user_data["debtor"])
    debt = [context.user_data["debt"], context.user_data["amount"]]
    update.message.reply_text(f"Folgende Schuld "
                              f"wurde in Auftrag gegeben:\n"
                              f"Schuldner: {context.user_data['debtor']}\n"
                              f"Schuld: {debt[0]} - {debt[1]}\n"
                              f"Deadline: {date[1]}", reply_markup=get_start_keyboard())

    # Save debt to json file
    print(date)
    schuld_obj = DB.add_debt(creditor_id, debt[0], debt[1], date[0], debtor_id)

    # Send message to prospective debtor
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text="\U0001F44D", callback_data=f"1,{schuld_obj.debt_id}"),

             InlineKeyboardButton(
                 text="\U0001F44E", callback_data=f"0,{schuld_obj.debt_id}")]
        ]
    )

    context.bot.send_message(chat_id=debtor_id, text=f"Willst Du folgende Schuld annehmen?\n"
                             f"Gläubiger: {DB.get_user_by_chat_id(creditor_id).name}\n"
                             f"Schuld {debt[0]} - {debt[1]}\n"
                             f"Deadline: {date[1]}",
                             reply_markup=keyboard)

    context.user_data.clear()
    return ConversationHandler.END


def date_handler(deadline):
    """
    making sure that the date has the correct format
    converts button input to correct date
    returns none if input is wrong
    returns "wrong_timeframe" if the date isn"t within the next year
    returns array with two date types [yyyy:mm:dd, dd.mm.yy] if correct
    """

    if deadline == "Heute":
        date = datetime.date.today()
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if deadline == "Morgen":
        date = datetime.date.today() + datetime.timedelta(days=1)
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if deadline == "Eine Woche":
        date = datetime.date.today() + datetime.timedelta(days=7)
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if deadline == "Zwei Wochen":
        date = datetime.date.today() + datetime.timedelta(days=14)
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if deadline == "Ein Monat":
        date = datetime.date.today() + datetime.timedelta(days=30)
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if deadline == "3 Monate":
        date = datetime.date.today() + datetime.timedelta(days=90)
        return [date.strftime("%Y:%m:%d"), date.strftime("%d.%m.%Y")]

    if "." in deadline:

        parts = deadline.split(".")

        # makes sure input is a valid date format
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            date = datetime.datetime.strptime(
                f"{parts[0]}.{parts[1]}.{parts[2]}", "%d.%m.%Y").date()

            # makes sure date is within the next year
            if (datetime.date.today()
                    <= date <= (datetime.date.today() + datetime.timedelta(days=365))):
                return [
                    (parts[2]+":"+parts[1]+":"+parts[0] +
                     ""), (parts[0]+"."+parts[1]+"."+parts[2]+"")
                ]

            return "wrong_timeframe"
    return None


# endregion calendar


def handle_accept_debt(update, context):
    """
    handles user input from acccept/deny debt
    if accept --> start timer
    if deny -> message creditor

    """

    query = (update.callback_query.data).split(",")
    print(query)
    debt = DB.get_debt_by_debt_id(query[1])

    if query[0] == "1":
        update.effective_message.edit_text("Du hast die Schuld angenommen.")
        DB.set_accepted(query[1], True)
        start_timer(UPDATER, query[1])

    else:
        update.effective_message.edit_text("Du hast die Schuld abgelehnt.")
        DB.set_accepted(query[1], False)
        context.bot.send_message(
            chat_id=debt.creditor, text=f"{DB.get_user_by_chat_id(debt.debtor).name}"
            f" hat die Schuld über {debt.category} abgelehnt.")


def done(update, context):
    """
    fallback method of conversation handler
    clears user data
    """
    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END
# endregion


def callback_general(update, context):
    # todo missing docstring
    """
    #todo missing docstring
    """

    callback_data = update.callback_query.data
    print(callback_data)
    action = None
    if "action" in callback_data:
        print(action)
        action = callback_data["action"]

    print(json.dumps(callback_data))

    if action == "debt_paid":

        handle_accept_debt_is_paid(update, context)

    if "yes" in callback_data or "no" in callback_data:  # in json ändern

        print(callback_data)
        handle_registration_response(update, context)

    elif callback_data[1] == ",":  # in json ändern
        # identify schulden begleichen // handle_accept_debt
        handle_accept_debt(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


# todo main docstring
def main():
    """
    todo main docstring

    """

    se_conv_handler = ConversationHandler(

        # conversation handler thread --> /schuld to initiate

        # type of user_selection
        # -> user selection
        # -> category selection
        # -> anzahl selection
        # -> calendar selection

        # every state has high priority cancel and back functions

        entry_points=[CommandHandler("schuld", new_debt)],

        states={
            USER_SELECTION: [MessageHandler(Filters.regex("^Abbrechen ✖$"),
                                            cancel_define_debt),
                             MessageHandler(Filters.regex("^Abbrechen"),
                                            cancel_define_debt),
                             MessageHandler(Filters.regex("^/schuld"),
                                            new_debt),
                             MessageHandler(Filters.regex("^/ichSchulde"),
                                            i_owe),
                             MessageHandler(Filters.regex("^/ichBekomme"),
                                            i_get),
                             MessageHandler(Filters.regex("^/start"),
                                            start),
                             MessageHandler(Filters.text,
                                            user_selection),
                             ],
            CATEGORY_SELECTION: [
                MessageHandler(Filters.regex("^(Getränke 🍻|Essen 🍕|Gefallen 🧞|Haushalt 🏘|Geld 💸)$"),
                               category_type_one),
                MessageHandler(Filters.regex("^Mobilität 🚗$"),
                               category_type_two),
                MessageHandler(Filters.regex("^Sonstiges 🧳$"),
                               category_type_manual),
                MessageHandler(Filters.regex("^Abbrechen ✖$"),
                               cancel_define_debt),
                MessageHandler(Filters.regex("^Abbrechen"),
                               cancel_define_debt),
                MessageHandler(Filters.regex("^Zurück ↩‍$"),
                               category_selection_back),
                MessageHandler(Filters.regex("^/schuld"),
                               new_debt),
                MessageHandler(Filters.regex("^/ichSchulde"),
                               i_owe),
                MessageHandler(Filters.regex("^/ichBekomme"),
                               i_get),
                MessageHandler(Filters.regex("^/start"),
                               start),
                MessageHandler(Filters.text,
                               category_type_one)
            ],
            AMOUNT_SELECTION: [MessageHandler(Filters.regex("^Abbrechen ✖$"),
                                              cancel_define_debt),
                               MessageHandler(Filters.regex("^Abbrechen"),
                                              cancel_define_debt),
                               MessageHandler(Filters.regex("^Sonstiges 📝$"),
                                              amount_selection_manual),
                               MessageHandler(Filters.regex("^Zurück ↩‍$"),
                                              amount_selection_back),
                               MessageHandler(Filters.regex("^/schuld"),
                                              new_debt),
                               MessageHandler(Filters.regex("^/ichSchulde"),
                                              i_owe),
                               MessageHandler(Filters.regex("^/ichBekomme"),
                                              i_get),
                               MessageHandler(Filters.regex("^/start"),
                                              start),
                               MessageHandler(Filters.text,
                                              amount_selection)
                               ],
            CALENDAR_SELECTION: [MessageHandler(Filters.regex("^Abbrechen ✖$"),
                                                cancel_define_debt),
                                 MessageHandler(Filters.regex("^Abbrechen"),
                                                cancel_define_debt),
                                 MessageHandler(Filters.regex("^Sonstiges 🗓$"),
                                                calendar_selection_manual),
                                 MessageHandler(Filters.regex("^Zurück ↩‍$"),
                                                calendar_selection_back),
                                 MessageHandler(Filters.regex("^/schuld"),
                                                new_debt),
                                 MessageHandler(Filters.regex("^/ichSchulde"),
                                                i_owe),
                                 MessageHandler(Filters.regex("^/ichBekomme"),
                                                i_get),
                                 MessageHandler(Filters.regex("^/start"),
                                                start),
                                 MessageHandler(Filters.text,
                                                calendar_selection),
                                 ],
        },

        fallbacks=[MessageHandler(Filters.regex("^Done$"), done)]
    )
    # endregion

    # Handler /ichSchulde
    i_owe_handler = ConversationHandler(
        entry_points=[CommandHandler("ichSchulde", i_owe)],
        states={
            CHOOSING_DEBT: [CallbackQueryHandler(handle_choosing_debt)],
            ASK_IF_DEBT_IS_PAID: [
                CallbackQueryHandler(handle_ask_if_debt_is_paid)]
        },
        fallbacks=[CommandHandler("ichSchulde", i_owe)]
    )
    # Handler /ichBekomme
    i_get_handler = ConversationHandler(
        entry_points=[CommandHandler("ichBekomme", i_get)],
        states={
            CHOOSING_CLAIM: [CallbackQueryHandler(handle_choosing_claim)],
            ASK_IF_CLAIM_IS_PAID: [
                CallbackQueryHandler(handle_ask_if_claim_is_paid)]
        },
        fallbacks=[CommandHandler("ichBekomme", i_get)]
    )

    # endregion

    UPDATER.dispatcher.add_handler(CommandHandler("start", start))

    UPDATER.dispatcher.add_handler(se_conv_handler)

    UPDATER.dispatcher.add_handler(i_owe_handler)
    UPDATER.dispatcher.add_handler(i_get_handler)

    # log all errors
    UPDATER.dispatcher.add_error_handler(error)

    UPDATER.dispatcher.add_handler(CallbackQueryHandler(callback_general))

    # Start the Bot
    UPDATER.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    UPDATER.idle()


if __name__ == "__main__":
    main()