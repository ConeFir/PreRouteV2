# WHAT REMAINS:

# The current dateTime approach is strictly about startTime, but we really need to have it handle overlap and
# utilize endTime too.


# AIMS FOR THIS DRAFT
# We are aiming to download the entirety of the user's data from Calendar.
# MEANS:
# We will do this via several steps, with the checklist at left.


# [x] STEP 0.0: We define the following *classes*: ClientCalendarList, ClientEventsList, ClientEvent.
    # [x] STEP 0.1: All classes have (at least) two init methods: name and json. Name, in many cases, is just summary.
    # [x] STEP 0.2: ClientCalendarList has a method to create a list of id numbers for calendars.
    # [x] STEP 0.3: ClientEventsList has a method to create a list of id numbers for events, EventsListIDList
    # [x] STEP 0.4: ClientEvents has (init) methods for location, start, end, id, summary
    # ENDGAME: We wind up with the ability to construct a list of all events in a given calendar.
# [ ] STEP 1.0: We build a function from the list of ids from EventsListIDList, called *GatherEvents*
    # [x] STEP 1.1: We start a for loop to work our way through ClientCalendarListIdList
    # [x] STEP 1.2: With each element we ask google for the eventsList corresponding to that id number.
    # [x] STEP 1.3: For each json that returns, we make that json an instance of a ClientEventsList, summmary as name.
    # [x] STEP 1.4: We then store the resulting ClientEventsList in a list, EventsListSet
# [ ] STEP 2.0: Using that method of the calendar, we call id numbers to get the eventsLists for those calendars.
    # [ ] STEP 2.1: ...Specifically, we make a method which loops through the id method of calendarList's items.
    # [ ] STEP 2.2: ...then this method calls google with that id number...
    # [ ] STEP 2.3: ...and makes the result of that call, an eventsList json, into an eventsList object.
# [ ] STEP 3.0: We define some utility functions for that dictionary, including:
# [ ] STEP 3.1: ...a function which tells us if there's a next event.
# [ ] STEP 3.2: ...a function that tells us if its the first event of the day.
# [ ] STEP 3.3: ...a function that tells us if its the last event of the day.
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

# We begin by defining the ClientCalendarList class.
# This class's parameters are a name and a json.
# The name is going to be primary, because it's for a given user.
# The json will be the CalendarList that we get from google.
# Once we've input the two parameters, we call the build_calendarList_id_list method.
# This method then populates self.calendarListIDList with [summary, id] lists.
# There is also a method, debug print, which prints self.calendarListIDList.

class ClientCalendarList:

    def __init__(self, name:str, json:dict):
        self.json = json
        self.name = name
        self.calendarListIDList = []

    def populate_calendarList_id_list(self, creds):
        service = build('calendar', 'v3', credentials=creds) # this will need creds to be defined.
        page_token = None
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        #print("For debug: Calendar list object is", calendar_list)
        for calendarList_item in calendar_list['items']:
            self.calendarListIDList.append([calendarList_item['summary'], calendarList_item['id']])

    def debug_print(self):
        print(self.calendarListIDList)

# We then go on to define a second class: ClientEventsList.
# This is a function whose parameters are a name (summary) and a json.
# These are got by running through CalendarListIDList.
# It has attributes corresponding to parameters.
# As above, it also comes with an attribute, eventListIDList, initialized as []
# This list is populated with the id's of the events in a given calendar.
# There is a case that we should also pair summaries with them.

# UPDATE: I've also included a new function, populate_ClientEvents.
# This function runs through eventListIdList, fetches the events whose ids they are from google,
# and then makes them into ClientEvents, and stashes them in ClientEvents.

class ClientEventsList:

    def __init__(self, name: str, json: dict, calendar_id: str):
        self.name = name
        self.json = json
        self.calendar_id = calendar_id
        self.eventListIDList = []
        self.client_events_json_dump = []
        self.classified_event_jsons = []
        self.all_events_preroutable = 0

# STEP 1: We populate the list of events for a given calendar.

    def populate_eventsListIDList(self):
        service = build('calendar', 'v3', credentials=creds) # this will need creds to be defined.
        page_token = None
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self.client_events_json_dump = service.events().list(calendarId=self.calendar_id, timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
        for event_item in self.client_events_json_dump['items']:
            self.eventListIDList.append([self.calendar_id, event_item['id']])

    def populate_ClientEvents(self):
        for calender_id_event_id_pairs in self.eventListIDList:
            page_token = None
            while True:
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                given_event = service.events().get(calendarId=calender_id_event_id_pairs[0], eventId=calender_id_event_id_pairs[1]).execute()
                given_event_name = str(given_event['summary'])
                arbitrary_value = ClientEvent(given_event_name, given_event)
                arbitrary_value.debug_dateTime() # for debugging
                self.classified_event_jsons.append(arbitrary_value)
                if not page_token:
                    break

    def check_and_set_if_preroutable(self):
        counter=1
        for event in self.classified_event_jsons:
            if event.is_preroutable == 1:
                continue
            if event.is_preroutable == 0:
                counter = 0
                break
        if counter == 1:
            self.all_events_preroutable = 1

    def set_scheduling_booleans(self):
        # NOTE: This uses startime to guage whether an event occurs on the same day.
        # It is also returning bad values
        if self.all_events_preroutable == 0:
            print("Error: This calendar is not preroutable.")
        else:
            for event in self.classified_event_jsons:
                if event.first_event_of_day == 2:
                    event.first_event_of_day = 1
                    for other_event in self.classified_event_jsons:
                        if event == other_event:
                            continue
                        if event != other_event:
                                if event.startISO > other_event.startISO and event.startISO.date == other_event.startISO.date:
                                    event.first_event_of_day = 0
                if event.last_event_of_day == 2:
                    event.last_event_of_day = 1
                    for other_event in self.classified_event_jsons:
                        if event == other_event:
                            continue
                        if event != other_event:
                            for other_event in self.classified_event_jsons:
                                if event.startISO < other_event.startISO and event.startISO.date == other_event.startISO.date:
                                    event.first_event_of_day = 0
                if event.has_successor == 2:
                    event.has_successor = 1
                    for other_event in self.classified_event_jsons:
                        if event.last_event_of_day == 1 and event != other_event:
                            event.has_successor = 0
            # debug stuff below:
                print (event.name, "has the successor value ", event.has_successor)
                print (event.name, "has the first_event value ", event.first_event_of_day)
                print (event.name, "has the last_event value", event.last_event_of_day)



    def debug_print(self):
        print("Self.json =", self.json)
        print("Self.name =", self.name)
        print("Self.eventListIDList =", self.eventListIDList)


# Finally, we have the ClientEvent class. This takes jsons of events and makes elements of them into attributes.
# Major attributes it handles are end and start times, iso versions of both, locations, ids, etags, descriptions, and summaries.

class ClientEvent:

    def __init__(self, name, json):

        # Stuff guarenteed to be in the json.

        self.name = name
        self.json = json
        self.id = json["id"]
        self.etag = json["etag"]
        self.summary = json["summary"]

        # Tests for if values are defined

        self.End_dateTime_defined = 2 # This becomes either 1 or 2 for yes and no depending on extract end dateTime
        self.Start_dateTime_defined = 2  # This becomes either 1 or 2 for yes and no depending on extract start dateTime
        self.dateTime_defined = 0
        self.location_defined = 0
        self.is_preroutable = 0

        # These values are not zero only when they are defined in self.json.

        self.end_dateTime = 0
        self.start_dateTime = 0
        self.startISO = 0
        self.endISO = 0
        self.location = 0

        # These have to be set via the method set_scheduling_booleans of the eventlist.
        # They are set to 2 until that method gets called.

        self.first_event_of_day = 2
        self.last_event_of_day = 2
        self.has_successor = 2

        #self.startTimeISO = dateutil.parser.isoparse(self.startTime["dateTime"])
        #self.endTimeISO = dateutil.parser.isoparse(self.endTime["dateTime"])


    def set_background_booleans(self):
        try:
            self.end_dateTime = self.json["end"]["dateTime"]
        except:
            print(self.name, "does NOT have a defined dateTime key in ['end']")
            self.End_dateTime_defined = 2
        else:
            print(self.name, "does have a defined dateTimekey in ['end']")
            self.End_dateTime_defined = 1
        try:
            self.start_dateTime = self.json["start"]["dateTime"]
        except:
            print(self.name, "does NOT have a defined dateTime key in ['end']")
            self.Start_dateTime_defined = 2
        else:
            print(self.name, "does have a defined dateTimekey in ['end']")
            self.Start_dateTime_defined = 1
        if self.End_dateTime_defined == 1 and self.Start_dateTime_defined == 1:
            self.dateTime_defined = 1
        else:
            self.dateTime_defined = 0
        try:
            self.location = self.json["location"]
        except:
            print("Location is NOT defined.")
        else:
            print("Location IS defined.")
            self.location_defined = 1
        if self.dateTime_defined == 1 and self.location_defined == 1:
            self.is_preroutable = 1
            self.startISO = dateutil.parser.isoparse(self.start_dateTime)
            self.endISO = dateutil.parser.isoparse(self.end_dateTime)


    def debug_dateTime(self):
        print("Json is", self.json)
        print("End_dateTime_defined is", self.End_dateTime_defined)
        print("end_dateTime is", self.end_dateTime)
        print("endISO is", self.endISO)
        print("Start_dateTime_defined is", self.Start_dateTime_defined)
        print("start_dateTime is", self.start_dateTime)
        print("startISO is", self.startISO)
        print("Location_defined is", self.location_defined)
        print("Location is", self.location)
        print("Is_preroutable is", self.is_preroutable)


# QUESTIONS:
# (1) We have the name parameter but I think the jsons should all contain summary data.
# (2) This whole process would likely be more straightforward if we just used the json and named the object via summary

# OBSERVATION
# (1) We will eventually need to include a function which compiles all of the ClientEvents of a given ClientEventsList
# into a chronological list, maybe by day.

# Step 1: Build a function to authenticate.

# Pretty straightforward, not gonna think too much about it.

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

# Now we set out to define a function whose purpose is to "go and get all of the events," that is:
# (1) Make the calendarList into a ClientCalendarList.
#

def gather_events():
    # Make the calendarList call into a ClientCalendarList.
    mainCalendarListGet = service.calendarList().get(calendarId='primary').execute()
    mainCalendarList = ClientCalendarList("mainCalendarList", mainCalendarListGet)
    mainCalendarList.populate_calendarList_id_list(creds)
    mainCalendarList.debug_print()
    # Using summaryIDPairs, get the eventsLists associated with them.
    # Take those eventsLists and create ClientEventsLists out of them.
    for summaryIdPairs in mainCalendarList.calendarListIDList:
        page_token = None
        while True:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            temporary_eventsList = service.events().list(calendarId=summaryIdPairs[1], pageToken=page_token, timeMin=now).execute()
            summaryIdPairs[0] = ClientEventsList(name=summaryIdPairs[0], json=temporary_eventsList, calendar_id=summaryIdPairs[1])
            summaryIdPairs[0].populate_eventsListIDList()
            summaryIdPairs[0].populate_ClientEvents()
            eventListList.append(summaryIdPairs[0])
            if not page_token:
                break

# A DEBUG FUNCTION:
def set_background_booleans_for_events_and_eventsList(eventListList):
    for eventList in eventListList:
        print("This is the eventList for the calendar", eventList.name) # debug
        for event in eventList.classified_event_jsons:
            event.set_background_booleans()
            print("Setting background booleans for", event.name) # debug
        print("Checking and setting if this calendar can be prerouted.") # debug
        eventList.check_and_set_if_preroutable()
        print("The value of eventList.is_preroutable is", eventList.all_events_preroutable) # debug
        for event in eventList.classified_event_jsons:
           event.debug_dateTime() #a debug function which tracks whether the classes attributes are set correctly.

def pre_route_eventsList(ClientEventsList):
    if ClientEventsList.all_events_preroutable == 0:
        print("This EventsList is not preroutable.")
    else:
        print("This EventsList is preroutable.")
        # At this juncture, it may be prudent to create two more booleans.
        # One for "first_event_of_day"
        # One for "last_event_of_day"
        # Another for "has_successor_event"



eventSet = []
eventListList = []
service_creds_pair = get_authentification_creds()
service = service_creds_pair[0]
creds = service_creds_pair[1]
gather_events()
set_background_booleans_for_events_and_eventsList(eventListList)
for eventList in eventListList:
    eventList.set_scheduling_booleans()




