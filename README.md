# Telegram Bot for Google Calendar 1.0

## Project Description
This is a Telegram bot written in Python 3.11 using [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) combined with the [Google Calendar API](https://developers.google.com/calendar/api). It let's you create, list and remove events within a Google Calendar using direct messages to the bot or by simply keeping the bot in a Telegram group chat.

This is my final project for [CS50: Introduction to Computer Science](https://pll.harvard.edu/course/cs50-introduction-computer-science?delta=0)


## Using the Bot
You may communicate directly or let the bot join a channel where you posses admin rights.

**Listing all commands**

`!help`

Gives an overview of available bot commands

**Adding and event**

`!add <event name>; <event type>; YYYY-MM-DD`

* Added events are whole-day events ranging from the start date to start date to start date +1 day
* The event type is written into the Google Calendar Event description as well as used to generate an event ID

**Listing events**

`!events <type>`

The event type is an optional argument. If you exclude it, all events will be listed from now on. Output is given in the following format:
```
Event Name
Event Date
Event ID incl. Type
```

**Removing an event**

`!remove <eventID>`

Let's you remove an event using the associated Id.


## Installing and Running
1. Clone this repository
2. Use Telegram Botfather to obtain the Bot API
    * [See guide](https://core.telegram.org/bots/features#creating-a-new-bot)
    * You have to allow the bot into groups via the settings menu talking to @botfather
3. Set the Bot API Token as an environmental variable API_TOKEN
4. Obtain your Google Calendar credentials (as a .JSON File) using Google's developer console
    * [A detailed guide can be found here in Chapter 1 & 2](https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/)
5. Save your credentials.JSON file in a new Folder called "utilities" within the main folder
6. Obtain the Google Calendar ID of the Calendar you want to access and save it into ./utilities/calendar_id.txt
7. Edit the event categories you want to use into "./event_categories.txt" (optional)
8. Run the script calling main.py
9. You can either contact the bot directly via @your_bot_name or you can invite your bot into group's (admin status required)


## Repository Drilldown
The Project consists of the following files:
1. main.py
    * Contains all utilities and functions for interacting with the bot itself as well as its' queries into the Google Calendar
2. cal_setup.py
    * Runs the authentification function for Google Calendar. Produces a token.pickle file for future reference
3. calendar_functions.py
    * Stores all calendar functions such as listing, adding, removing and returning events.
4. event_categories.txt
    * Storage of event categories to differentiate the event types
5. utilities
    * You have to create a folder called utilities by yourself
    * Storage of your Google Calendar credentials.JSON as well as a textfile containing the calendar ID you want to use


## Credits
Big thanks to [Karen](https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/) for their free tutorial on Google Calendar automation that provided most of the scripts used within cal_setup.py and calendar_functions.py.

Also to CS50 for this inspiring course.


## License
MIT License
See LICENSE.md
