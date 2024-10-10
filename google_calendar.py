# manejar calendario google

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime


class GoogleCalendar:

    def __init__(self, credentials, idcalendar):
        self.credentials = credentials
        self.idcalendar = 'ferxisabee@gmail.com'
        self.service = build('calendar', 'v3', 
                             credentials=service_account.Credentials.from_service_account_info(
                                 self.credentials, scopes=["https://www.googleapis.com/auth/calendar"]
))

    def create_event(self, name_event, start_time, end_time, timezone, attendes=None):

  

        event = {
            'summary': name_event,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }
        if attendes:
            event['attendes'] = [{'email': email} for email in attendes]

        try:
            created_event = self.service.events().insert(calendarId = self.idcalendar, body=event).execute()

        except HttpError as error:
            raise Exception(f"An arror as ocurred: {error}")

        return created_event

    def get_events(self, date=None):
        if not date:
            events = self.service.events().list(calendarId=self.idcalendar).execute()
        else:
            start_date = f"{date}T00:00:00Z"
            end_date = f"{date}T23:59:00Z"
            events = self.service.events().list(calendarId=self.idcalendar,timeMin=start_date, timeMax=end_date).execute()

        return events.get("items", [])

    def get_events_start_time(self, date):
        events = self.get_events(date)
        start_times = []

        for event in events:
            start_time = event['start']['dateTime']
            parsed_start_time = datetime.fromisoformat(start_time[:-6])
            hora_minutos = parsed_start_time.strftime("%H:%M")
            start_times.append(hora_minutos)

        return start_times


