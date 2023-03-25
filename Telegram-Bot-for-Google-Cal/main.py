import telebot
import calendar_functions
import datetime
from os import getenv


API_TOKEN = getenv('TELEGRAM_API')
EVENT_TYPES = []

bot = telebot.TeleBot(API_TOKEN)
print("Starting bot...")

with open ('./utilities/event_categories.txt') as file:
    for line in file.readlines():
        EVENT_TYPES.append(line.rstrip())    

 
@bot.message_handler(regexp="!help")
def commands(message):
    commands = [
            "Here are my commands:",
            telebot.formatting.hbold("!events <type>\n") + "Lists all events from now on (type optional)",
            telebot.formatting.hbold('!add <name>; <type>; <yyyy-mm-dd>\n') + 'Adds new event of particular type',
            telebot.formatting.hbold('!remove <eventID>\n') + 'Removes event of particular ID',
            telebot.formatting.hbold('!update <eventID>; <yyyy-mm-dd>\n') + 'Updates an event date',
            ]

    bot.send_message(message.chat.id, "\n\n".join(commands), parse_mode='html')
    bot.send_message(message.chat.id, telebot.formatting.hbold('Current event types:\n') + '\n'.join(EVENT_TYPES), parse_mode='html')


@bot.message_handler(regexp="!events")
def list_events(message):
    events = calendar_functions.list_events()

    if not events:
        bot.send_message(message.chat.id, 'No upcoming events found')
        return

    event_list = []

    try:
        argument = message.text.split()[1]
        if argument not in EVENT_TYPES:
            bot.reply_to(message, 'Event type no available. Current types:\n\n' + '\n'.join(EVENT_TYPES))
            return
        else:
            for event in events:
                if argument in event['id']:
                    event_list.append(
                            '\n'.join([telebot.formatting.hbold(event['summary']), event['start'].get('date'), event['id']])
                            )

    except IndexError:
        for event in events:
            event_list.append(
                    '\n'.join([telebot.formatting.hbold(event['summary']), event['start'].get('date'), event['id']])
                    )

    sent_message = bot.send_message(message.chat.id, '\n\n'.join(event_list), parse_mode='html')
    bot.unpin_all_chat_messages(message.chat.id)
    bot.pin_chat_message(message.chat.id, sent_message.message_id, True)


@bot.message_handler(regexp="!add")
def add_event(message):
    try:
        event_name = message.text.split('; ')[0][5:]
        event_type = message.text.split('; ')[1]
        event_date = message.text.split('; ')[2]
    except IndexError:
        bot.reply_to(message, text = 'Usage: !add <name>; <type>; <yyyy-mm-dd>')
        return

    if event_type not in EVENT_TYPES:
        bot.reply_to(message, 'Event type no available. Current types:\n\n' + '\n'.join(EVENT_TYPES))
        return
    elif not validate_date(event_date):
        bot.reply_to(message, 'Please enter date in format YYYY-MM-DD.')
        return
    else:
        event_id = create_event_id(event_type, event_date)
        event = calendar_functions.create_event(event_name, event_type, event_date, event_id)
        bot.send_message(message.chat.id, 
                         text = 'Event succesfully created:\n' + '\n'.join(event.values()), 
                         parse_mode='html')
        return


@bot.message_handler(regexp="!remove")
def remove_event(message):
    if len(message.text.split()) != 2:
        bot.reply_to(message, "Usage: !remove <event id>")
        return
    else:
        if not calendar_functions.delete_event(message.text.split()[1]):
            bot.reply_to(message, "Event id does not exist")
            return
        else:
            bot.send_message(message.chat.id, "Event succesfully deleted.")
            return


@bot.message_handler(regexp="!update")
def update_event(message):
    try:
        event_id = message.text.split('; ')[0][8:]
        event_date = message.text.split('; ')[1]
        
        if not validate_date(event_date):
            bot.reply_to(message, 'Please enter date in format YYYY-MM-DD.')
            return
        
    except IndexError:
        bot.reply_to(message, text = 'Usage: !update <event id>; <yyyy-mm-dd>')
        return

    current_event = calendar_functions.get_event(event_id)
    if not current_event:
        bot.reply_to(message, "Event id does not exist")
        return
    else:
        current_name = current_event["summary"]
        current_category = current_event["description"]

    event = calendar_functions.update_event(event_id, event_date, current_name, current_category)
    if not event:
        bot.reply_to(message, "Unknown Error occured")
    else:
        bot.send_message(message.chat.id, 
                            text = 'Event succesfully updated:\n' + 
                            '\n'.join(event.values()), parse_mode='html')
        return


def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def create_event_id(event_category, event_date):
    return f"{event_category}{event_date.replace('-', '')[4:]}"


bot.infinity_polling()
