""" Functions are based on this tutorial: """
""" https://karenapp.io/articles/how-to-automate-google-calendar-with-python-using-the-calendar-api/ """

import datetime
import googleapiclient
from datetime import timedelta
from os import read
from os import getenv
from cal_setup import get_calendar_service


""" Setting up the calender id """
cal_id = './utilities/calendar_id.txt'
with open(cal_id, 'r') as file:
    CALENDAR_ID = file.read()

# CALENDAR_ID = getenv('CALENDARID')

""" Lists all currently connected celdendar with the associated account """
def list_calendars():
    service = get_calendar_service()
    # Call the Calendar API
    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        id = calendar['id']
        primary = "Primary" if calendar.get('primary') else ""
        print("%s\t%s\t%s" % (summary, id, primary))



""" Lists all the events in the CALENDAR_ID calendar """
def list_events():
    service = get_calendar_service()
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC Time
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


""" Creates an event in the CALENDAR_ID calender """
def create_event(event_name, event_type, event_start):
 
    service = get_calendar_service()
 
    # Calculate the end time by converting into datetime object and back into str
    start = datetime.datetime.strptime(event_start, '%Y-%m-%d').date()
    end = start+timedelta(days=1)
    event_end = end.isoformat()

    # Call the insert function using the bot arguments and store the created event object    
    event_result = service.events().insert(calendarId=CALENDAR_ID,
        body={
            "summary": event_name,
            "description": event_type,
            "start": {"date": event_start},
            "end": {"date": event_end},
        }
    ).execute()

    # Return relevant data from the stored event object to the bot
    return {
        'name': event_result['summary'],
        'date': event_result['start']['date'],
        'description': event_result['description'],
        'id': event_result['id']
    }


""" Deletes an event in the CALENDAR_ID calender """
def delete_event(event_id):
    # Delete the event
    service = get_calendar_service()
    try:
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id,
        ).execute()
    except googleapiclient.errors.HttpError:
        return False

    return True


""" Updates an event in the primary calender """
""" Not for prototype functionality """
# def update_event():
#         # update the event to tomorrow 9 AM IST
#         service = get_calendar_service()

#         d = datetime.now().date()
#         tomorrow = datetime(d.year, d.month, d.day, 9)+timedelta(days=1)
#         start = tomorrow.isoformat()
#         end = (tomorrow + timedelta(hours=2)).isoformat()

#         event_result = service.events().update(
#           calendarId='primary',
#           eventId='<place your event ID here>',
#           body={
#            "summary": 'Updated Automating calendar',
#            "description": 'This is a tutorial example of automating google calendar with python, updated time.',
#            "start": {"dateTime": start, "timeZone": 'Asia/Kolkata'},
#            "end": {"dateTime": end, "timeZone": 'Asia/Kolkata'},
#            },
#         ).execute()

#         print("updated event")
#         print("id: ", event_result['id'])
#         print("summary: ", event_result['summary'])
#         print("starts at: ", event_result['start']['dateTime'])
#         print("ends at: ", event_result['end']['dateTime'])