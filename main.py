import telebot
import calendar_functions
import datetime
from os import getenv

""" BOT INITIALISATION """

# Don't forget to change for production
# Get API KEY
token_id = './utilities/API_TOKEN_old.txt'
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
    command_list.append(telebot.formatting.hbold('!update <eventID>; <yyyy-mm-dd>\n') + 'Updates an event date')

    commands = "\n\n".join(command_list)

    bot.send_message(message.chat.id, commands, parse_mode='html')
    bot.send_message(message.chat.id, telebot.formatting.hbold('Current event types:\n') + '\n'.join(event_types), parse_mode='html')

""" !events: Lists all upcoming events in the calender """
@bot.message_handler(regexp="!events")
def list_events(message):

    # extracts the argument from user input
    argument = message.text.split()[1:]

    #Extraction and filtering of events from Google API query
    # creates a list of dictionaries including all events in the calendar
    events = calendar_functions.list_events()
    if not events:
        bot.send_message(message.chat.id, 'No upcoming events found')
        return

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
        return
    
    # Output of query results via TeleBot
    output_event = []
    for event in filtered_events:
        output_event.append('\n'.join(event.values()))
    
    output = '\n\n'.join(output_event)

    # Send event message, unpin current pin and set message as new pinned message
    sent_message = bot.send_message(message.chat.id, text = output, parse_mode='html')
    bot.unpin_all_chat_messages(message.chat.id)
    bot.pin_chat_message(message.chat.id, sent_message.message_id, True)
    return


""" !add: adds events into the connected calendar """
@bot.message_handler(regexp="!add")
def add_event(message):
    
    # Store arguments into variables
    try:
        event_name = message.text.split('; ')[0][5:]
        event_type = message.text.split('; ')[1]
        event_date = message.text.split('; ')[2]
    except IndexError:
        bot.reply_to(message, text = 'Usage: !add <name>; <type>; <yyyy-mm-dd>')
        return

    # Validation if events argument is included in types and date format is correct
    if event_type not in event_types:
        bot.reply_to(message, 'Event type no available. Current types:\n\n' + '\n'.join(event_types))
        return
    elif not validate_date(event_date):
        bot.reply_to(message, 'Please enter date in format YYYY-MM-DD.')
        return
    # Call the create event function after everything is valid and return the created event object
    else:
        event = calendar_functions.create_event(event_name, event_type, event_date)
        bot.send_message(message.chat.id, 
        text = 'Event succesfully created:\n' + '\n'.join(event.values()), 
        parse_mode='html')
        return

""" !remove: removes events from the calender based on event id """
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


""" !update: changes date of existing events """
@bot.message_handler(regexp="!update")
def update_event(message):

    # Store arguments into variables and validate the date
    try:
        event_id = message.text.split('; ')[0][8:]
        event_date = message.text.split('; ')[1]
        
        if not validate_date(event_date):
            bot.reply_to(message, 'Please enter date in format YYYY-MM-DD.')
            return
        
    except IndexError:
        bot.reply_to(message, text = 'Usage: !update <event id>; <yyyy-mm-dd>')
        return

    # retrive current event information to include in update function
    current_event = calendar_functions.get_event(event_id)
    if not current_event:
        bot.reply_to(message, "Event id does not exist")
        return
    else:
        current_name = current_event["summary"]
        current_category = current_event["description"]

    # call update_event() to change the date and print new event data
    event = calendar_functions.update_event(event_id, event_date, current_name, current_category)
    if not event:
        bot.reply_to(message, "Unknown Error occured")
    else:
        bot.send_message(message.chat.id, 
                            text = 'Event succesfully updated:\n' + 
                            '\n'.join(event.values()), parse_mode='html')
        return


""" Helper Functions """

# Add a function to validate the correct date format in input
def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

bot.infinity_polling()
