import telebot
import calendar_functions
import datetime
from os import getenv

""" BOT INITIALISATION """

# Get API KEY
token_id = './utilities/API_TOKEN.txt'
with open(token_id, 'r') as file:
    API_TOKEN = file.read()

# API_TOKEN = getenv('TELEGRAM_API')

bot = telebot.TeleBot(API_TOKEN)

print("Starting bot...")

""" VARIABLES """
event_types = []
with open ('./event_categories.txt') as file:
    for line in file.readlines():
        line_new = line.rstrip()
        event_types.append(line_new)

 
""" TELEGRAM BOT FUNCTIONALITIES """

""" !help: Lists all the Commands available to the bot and their usage """
@bot.message_handler(regexp="!help")
def commands(message):

    command_list = []
    
    command_list.append("Here are my commands:")
    command_list.append(telebot.formatting.hbold('!events <type>\n') + 'Lists all events from now on (type optional)')
    command_list.append(telebot.formatting.hbold('!add <name>; <type>; <yyyy-mm-dd>\n') + 'Adds new event of particular type')
    command_list.append(telebot.formatting.hbold('!remove <eventID>\n') + 'Removes event of particular ID')


    # command_text = "Here are my commands:"
    # command_event = telebot.formatting.hbold('!events <type>\n') + 'Lists all events from now on (type optional)'
    # command_add = telebot.formatting.hbold('!add <name>; <type>; <yyyy-mm-dd>\n') + 'Adds new event of particular type'
    # command_remove = telebot.formatting.hbold('!remove <eventID>\n') + 'Removes event of particular ID'

    commands = "\n\n".join(command_list)
    # commands = 'Here are my commands:\n\n' + command_event + '\n\n' + command_add + '\n\n' + command_remove

    bot.send_message(message.chat.id, commands, parse_mode='html')
    bot.send_message(message.chat.id, telebot.formatting.hbold('Current event types:\n') + '\n'.join(event_types), parse_mode='html')

""" !events: Lists all upcoming events in the calender """
@bot.message_handler(regexp="!events")
def list_events(message):

    # extracts the argument from user input
    argument = message.text.split()[1:]

    """ Extraction and filtering of events from Google API query """
    # creates a list of dictionaries including all events in the calendar
    events = calendar_functions.list_events()
    if not events:
        bot.send_message(message.chat.id, 'No upcoming events found')

    # creates a sub-list of dictonaries including only the relevant information
    filtered_events = []

    # if no argumnet was given, all events are indexed
    if not argument:
        for event in events:
            # using exceptions if description (optinal field) is empty
            try:
                temp_events = {
                    "name": telebot.formatting.hbold(event['summary']),
                    "date": event['start'].get('date'),
                    "type": event['description'],
                    "id": event['id']
                }
                filtered_events.append(temp_events)

            except(KeyError, TypeError, ValueError):
                temp_events = {
                    "name": telebot.formatting.hbold(event['summary']),
                    "date": event['start'].get('date'),
                    "id": event['id']
                }
                filtered_events.append(temp_events)

    # if an argument was given, only events with this argument in the description are indexed
    elif argument[0].lower() in event_types:
        for event in events:
            temp_events = {
                "name": telebot.formatting.hbold(event['summary']),
                "date": event['start'].get('date'),
                "type": event['description'],
                "id": event['id']
            }
            if temp_events['type'] == argument[0].lower():
                filtered_events.append(temp_events)
    
    # if an unknown argument was given
    else:
        bot.reply_to(message, 'Event type no available. Current types:\n\n' + '\n'.join(event_types))

    """ Output of query results via TeleBot """
    for event in filtered_events:
        bot.send_message(message.chat.id, text = '\n'.join(event.values()), parse_mode='html')


""" !add: adds events into the connected calendar """
@bot.message_handler(regexp="!add")
def add_event(message):

    # Add a function to validate the correct date format in input
    def validate_date(date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    # Store arguments into variables
    try:
        event_name = message.text.split('; ')[0][5:]
        event_type = message.text.split('; ')[1]
        event_date = message.text.split('; ')[2]
    except IndexError:
        bot.reply_to(message, text = 'Usage: !add <name>; <type>; <yyyy-mm-dd>')

    # Validation if events argument is included in types and date format is correct
    if event_type not in event_types:
        bot.reply_to(message, 'Event type no available. Current types:\n\n' + '\n'.join(event_types))
    elif not validate_date(event_date):
        bot.reply_to(message, 'Please enter date in format YYYY-MM-DD.')
    # Call the create event function after everything is valid and return the created event object
    else:
        event = calendar_functions.create_event(event_name, event_type, event_date)
        bot.send_message(message.chat.id, 
        text = 'Event succesfully created:\n' + '\n'.join(event.values()), 
        parse_mode='html')


""" !remove: removes events from the calender based on event id """
@bot.message_handler(regexp="!remove")
def remove_event(message):

    if len(message.text.split()) != 2:
        bot.reply_to(message, 'Usage: !remove <event id>')
    else:
        if not calendar_functions.delete_event(message.text.split()[1]):
            bot.reply_to(message, 'Event id does not exist')
        else:
            bot.send_message(message.chat.id, 'Event succesfully deleted.')

bot.infinity_polling()