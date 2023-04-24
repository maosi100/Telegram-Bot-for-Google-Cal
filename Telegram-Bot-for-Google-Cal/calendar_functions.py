import datetime
import googleapiclient
from datetime import timedelta
from os import read
from os import getenv
from cal_setup import get_calendar_service


CALENDAR_ID = getenv('CALENDAR_ID')

def list_calendars():
    service = get_calendar_service()
    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        id = calendar['id']
        primary = "Primary" if calendar.get('primary') else ""
        print("%s\t%s\t%s" % (summary, id, primary))


def list_events():
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC Time
    events_result = service.events().list(
        calendarId=CALENDAR_ID, timeMin=now,
        singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def get_event(event_id):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    return service.events().get(
        calendarId=CALENDAR_ID, eventId=event_id
    ).execute()


def create_event(event_name, event_type, event_start, event_id):
    service = get_calendar_service()
 
    start = datetime.datetime.strptime(event_start, '%Y-%m-%d').date()
    end = start+timedelta(days=1)
    event_end = end.isoformat()

    event_result = service.events().insert(calendarId=CALENDAR_ID,
        body={
            "id": event_id,
            "summary": event_name,
            "description": event_type,
            "start": {"date": event_start},
            "end": {"date": event_end},
        }
    ).execute()

    return {
        'name': event_result['summary'],
        'date': event_result['start']['date'],
        'id': event_result['id']
    }


def delete_event(event_id):
    service = get_calendar_service()
    try:
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id,
        ).execute()
    except googleapiclient.errors.HttpError:
        return False

    return True


def update_event(event_id, event_start, event_name, event_type):
        service = get_calendar_service()

        start = datetime.datetime.strptime(event_start, '%Y-%m-%d').date()
        end = start+timedelta(days=1)
        event_end = end.isoformat()

        event_result = service.events().update(
          calendarId=CALENDAR_ID,
          eventId=event_id,
          body={
            "summary": event_name,
            "description": event_type,
            'start': {'date': event_start},
            'end': {'date': event_end},
           }
        ).execute()

        return {
            'name': event_result['summary'],
            'date': event_result['start']['date'],
            'description': event_result['description'],
            'id': event_result['id']
        }
