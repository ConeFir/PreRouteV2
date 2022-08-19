# AIMS FOR THIS DRAFT
# We are aiming to download the entirety of the user's data from Calendar.
# MEANS:
# We will do this via several steps, with the checklist at left.

# WARNINGS:
#(1) I am skipping pagetoken stuff for now. I've noted where I'm doing this in the code by commenting out token refs.


# [x] STEP 0.0: We define the following *classes*: ClientCalendarList, ClientEventsList, ClientEvent.
    # [x] STEP 0.1: All classes have (at least) two init methods: name and json. Name, in many cases, is just summary.
    # [x] STEP 0.2: ClientCalendarList has a method to create a list of id numbers for calendars.
    # [x] STEP 0.3: ClientEventsList has a method to create a list of id numbers for events, EventsListIDList
    # [x] STEP 0.4: ClientEvents has (init) methods for location, start, end, id, summary
    # ENDGAME: We wind up with the ability to construct a list of all events in a given calendar.
# [ ] STEP 1.0: We build a function from the list of ids from EventsListIDList, called *GatherEvents*
    # [ ] STEP 1.1: We start a for loop to work our way through ClientCalendarListIdList
    # [ ] STEP 1.2: With each element we ask google for the eventsList corresponding to that id number.
    # [ ] STEP 1.3: For each json that returns, we make that json an instance of a ClientEventsList, summmary as name.
    # [ ] STEP 1.4: We then store the resulting ClientEventsList in a dictionary
# [ ] STEP 2.0: Using that method of the calendar, we call id numbers to get the eventsLists for those calendars.
    # [ ] STEP 2.1: ...Specifically, we make a method which loops through the id method of calendarList's items.
    # [ ] STEP 2.2: ...then this method calls google with that id number...
    # [ ] STEP 2.3: ...and makes the result of that call, an eventsList json, into an eventsList object.
# [ ] STEP 3.0: We define an eventsList.
# [ ] STEP 5.0: We compile the ClientEventsLists and the ClientEvents into a dictionary, MOTHADICT
# [ ] STEP 6.0: We define some utility functions for that dictionary, including:
# [ ] STEP 6.1: ...a function which tells us if there's a next event.
# [ ] STEP 6.2: ...a function that tells us if its the first event of the day.
# [ ] STEP 6.3: ...a function that tells us if its the last event of the day.
# (An open question here: Ought we to put those functions as methods of the ClientX classes? Or make MOTHADICT a class?
# ...Or just make it free-floating?)
# STEP 7: A function that


from __future__ import print_function
import os.path
import dateutil
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googlemaps
from datetime import datetime
import dateutil.parser

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")



class ClientCalendarList:

    def __init__(self, name, json):
        self.json = json
        self.name = name
        self.calendarListIDList = []

    def build_calendarList_id_list(self, creds):
        service = build('calendar', 'v3', credentials=creds) # this will need creds to be defined.
        page_token = None
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        print("For debug: Calendar list object is", calendar_list)
        for calendarList_item in calendar_list['items']:
            self.calendarListIDList.append([calendarList_item['summary'], calendarList_item['id']])

    def debug_print(self):
        print(self.calendarListIDList)

class ClientEventsList:

    def __init__(self, name, json):
        self.name = name
        self.json = json
        self.eventListIDList = []

    def build_eventsList_id_list(self, creds):
        service = build('calendar', 'v3', credentials=creds)
        page_token = None
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_list = service.events().list(calendarId=self.id, timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
        for event_item in events_list['items']:
            self.eventsListIDList.append(event_item['id'])

    def debug_print(self):
        print("Self.json =", self.json)
        print("Self.name =", self.name)
        print("Self.eventListIDList =", self.eventListIDList)


class ClientEvent:

    def __init__(self, name, json):
        self.name = name
        self.json = json
        self.endTime = json["end"]["dateTime"]
        self.startTime = json["start"]["dateTime"]
        self.startTimeISO = dateutil.parser.isoparse(json["end"]["dateTime"])
        self.endTimeISO = dateutil.parser.isoparse(json["end"]["dateTime"])
        self.location = json["location"]
        self.id = json["id"]
        self.etag = json["etag"]
        self.summary = json["summary"]
        self.description = json["description"]


# Step 1: Build a function to authenticate.

def get_authentification_creds():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', CALENDERSCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', CALENDERSCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return [service, creds]

def gather_events():
    # Make the calendarList call into a ClientCalendarList.
    mainCalendarListGet = service.calendarList().get(calendarId='primary').execute()
    mainCalendarList = ClientCalendarList("mainCalendarList", mainCalendarListGet)
    mainCalendarList.build_calendarList_id_list(creds)
    mainCalendarList.debug_print()
    for summaryIdPairs in mainCalendarList.calendarListIDList:
        page_token = None
        while True:
            now = datetime.utcnow().isoformat() + 'Z'
            temporary_eventsList = service.events().list(timeMin= calendarId=summaryIdPairs[1], pageToken=page_token).execute()
            summaryIdPairs[0] = ClientEventsList(name=str(summaryIdPairs[0]), json=temporary_eventsList)
#            summaryIdPairs[0].build_eventsList_id_list(creds)
            #page_token = events.get('nextPageToken')
            summaryIdPairs[0].debug_print()
            if not page_token:
                break


service_creds_pair = get_authentification_creds()
service = service_creds_pair[0]
creds = service_creds_pair[1]
gather_events()
