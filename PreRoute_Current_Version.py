from __future__ import print_function
import os.path
import dateutil
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import googlemaps
from datetime import datetime
import dateutil.parser

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")

class ClientCalendarList:

    def __init__(self, name:str, json:dict):
        self.json = json
        self.name = name
        self.calendarListSummaryIDPairList = []

    def populate_calendarList_id_list(self, creds):
        service = build('calendar', 'v3', credentials=creds) # this will need creds to be defined.
        page_token = None
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendarList_item in calendar_list['items']:
            self.calendarListSummaryIDPairList.append([calendarList_item['summary'], calendarList_item['id']])

    def debug_print(self):
        print(self.calendarListSummaryIDPairList)


class ClientEventsList:

    def __init__(self, name: str, json: dict, calendar_id: str):
        self.name: str = name
        self.json: dict = json
        self.calendar_id: str = calendar_id
        self.eventListIDList: list = []
        self.client_events_json_dump: dict = {}
        self.classified_event_jsons: list = []
        self.all_events_preroutable: int = 0

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
                now: datetime = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                given_event: dict = service.events().get(calendarId=calender_id_event_id_pairs[0], eventId=calender_id_event_id_pairs[1]).execute()
                given_event_name: str = str(given_event['summary'])
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
        self.check_and_set_if_preroutable()
        if self.all_events_preroutable == 0:
            print(self.name, "is not preroutable, so I'm stopping now.")
        if self.all_events_preroutable ==1:
            print(self.name, "is preroutable, so now I'm going to set scheduling booleans")
            for index in range(len(self.classified_event_jsons)):
                print("Entering main loop, now considering", self.classified_event_jsons[index].name)
                if self.classified_event_jsons[0] == self.classified_event_jsons[index]:
                    print(self.classified_event_jsons[index].name,
                          "is the first event on the classified events jsons for this eventsList.")
                    self.classified_event_jsons[index].first_event_of_day = 1
                    print("Accordingly, ", self.classified_event_jsons[index].name, "has been marked first event of the day.")
                    continue
                if self.classified_event_jsons[index] != self.classified_event_jsons[0]:
                    print(self.classified_event_jsons[index].name,
                          "is NOT the first event on the classified events jsons for this eventsList.")
                    if self.classified_event_jsons[index-1].startISO.date() == self.classified_event_jsons[index].startISO.date():
                        print(self.classified_event_jsons[index].name, "is on the same date as its precedessor, ",
                                    self.classified_event_jsons[index-1].name)
                        if self.classified_event_jsons[index - 1].first_event_of_day == 1:
                            print(self.classified_event_jsons[index-1].name, "is the first event of the day...")
                            self.classified_event_jsons[index].first_event_of_day = 0
                            print("So I'm making", self.classified_event_jsons[index].name, "as a non-first event.")
                        else:
                            print(self.classified_event_jsons[index-1].name, "is not the first event of day.")
                            self.classified_event_jsons[index].first_event_of_day = 0
                            print("So I'm saying", self.classified_event_jsons[index].name, "is not a first event either")
                    if self.classified_event_jsons[index - 1].startISO.date() != self.classified_event_jsons[index].startISO.date():
                        print(self.classified_event_jsons[index].name, "is NOT on the same date as its precedessor, ",
                                    self.classified_event_jsons[index-1].name)
                        self.classified_event_jsons[index].first_event_of_day = 1
                        print(self.classified_event_jsons[index].name, "is now marked as the first event of the day.")
                        self.classified_event_jsons[index-1].last_event_of_day = 0
                        print(self.classified_event_jsons[index-1].name, "is now marked as the last event of the day.")
                    if index + 1 == len(self.classified_event_jsons):
                        print("The index is", index, "so I evaluated ", index +1, "and it is equal to", len(self.classified_event_jsons))
                        print("I've said thisis the last event of the day.")
                        self.classified_event_jsons[index].last_event_of_day = 1



    def debug_print(self):
        print("Self.json =", self.json)
        print("Self.name =", self.name)
        print("Self.eventListIDList =", self.eventListIDList)


class ClientEvent:

    def __init__(self, name: str, json: dict):

        # Stuff guarenteed to be in the json.

        self.name: str = name
        self.json: dict = json
        self.id: str = json["id"]
        self.etag: str = json["etag"]
        self.summary: str = json["summary"]

        # Tests for if values are defined

        self.End_dateTime_defined: int = 2 # This becomes either 1 or 2 for yes and no depending on extract end dateTime
        self.Start_dateTime_defined: int = 2  # This becomes either 1 or 2 for yes and no depending on extract start dateTime
        self.dateTime_defined: int = 0
        self.location_defined: int = 0
        self.is_preroutable: int = 0

        # These values are not zero only when they are defined in self.json.

        self.end_dateTime: str = 0
        self.start_dateTime: str = 0
        self.startISO: datetime = 0
        self.endISO: datetime = 0
        self.location: str = 0

        # These have to be set via the method set_scheduling_booleans of the eventlist.
        # They are set to 2 until that method gets called.

        self.first_event_of_day: int = 2
        self.last_event_of_day: int = 2

        #self.startTimeISO = dateutil.parser.isoparse(self.startTime["dateTime"])
        #self.endTimeISO = dateutil.parser.isoparse(self.endTime["dateTime"])

        self.scheduling_booleans_set = 0

        #NOT SO SURE ABOUT THESE:
        # For now, I'm attaching the directions to the events.

        self.json_directions_to_this_event = 0

        # This way, if you get a type error, then you'll know that this is at fault.
        # Now we stash a bunch of useful data

        self.step_list = []


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

    def populate_step_list(self):

        for leg in self.json_directions_to_this_event[0]['legs'][0]['steps']:
            self.step_list.append(leg)



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
    mainCalendarList.populate_calendarList_id_list(creds)
    mainCalendarList.debug_print()
    # Using summaryIDPairs, get the eventsLists associated with them.
    # Take those eventsLists and create ClientEventsLists out of them.
    for summaryIdPairs in mainCalendarList.calendarListSummaryIDPairList:
        page_token = None
        while True:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            temporary_eventsList = service.events().list(calendarId=summaryIdPairs[1], pageToken=page_token, timeMin=now).execute()
            summaryIdPairs[0] = ClientEventsList(name=summaryIdPairs[0], json=temporary_eventsList, calendar_id=summaryIdPairs[1])
            summaryIdPairs[0].populate_eventsListIDList()
            eventListList.append(summaryIdPairs[0])
            if not page_token:
                break

# A DEBUG FUNCTION:
def set_background_booleans_for_events_and_eventsList(eventListList: list):
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

def preroute_client_events_List(ClientEventsList: list):
    if ClientEventsList.all_events_preroutable == 0:
        print("This EventsList is not preroutable.")
    else:
        print("This EventsList is preroutable. I am now PreRouting it.")
        for index in range(len(ClientEventsList.classified_event_jsons)):
            this_event = ClientEventsList.classified_event_jsons[index]
            if this_event == ClientEventsList.classified_event_jsons[0]:
                continue
            else:
                if this_event.first_event_of_day == 1:
                    continue
                else:
                    prior_event = ClientEventsList.classified_event_jsons[index-1]
                    # GET DIRECTIONS
                    try:
                        #print("I am now attempting to get directions between", this_event.name, "and", prior_event.name)
                        directions_result = gmaps.directions(destination=str(this_event.location), origin=str(prior_event.location),
                                                             mode="transit", departure_time=prior_event.endISO)
                        this_event.json_directions_to_this_event = directions_result
                        #print("I tried to append the directions result to", this_event.name)
                        #print("Here it is:")
                        #print(this_event.json_directions_to_this_event)
                    except:
                        print("Error appending directions_result to this_event.")
                    try:
                        this_event.populate_step_list()
                    except:
                        print("Problem with populating step_list for", this_event.name)
                    #leg_end_date = this_event.startISO.date()
                    leg_end_dateTime = str(datetime.fromtimestamp(this_event.json_directions_to_this_event[0]['legs'][0]['arrival_time']['value']).isoformat())
                    leg_end_timeZone = this_event.json_directions_to_this_event[0]['legs'][0]['arrival_time']['time_zone']
                    #leg_start_date = this_event.startISO.date()
                    leg_start_dateTime = str(datetime.fromtimestamp(this_event.json_directions_to_this_event[0]['legs'][0]['departure_time']['value']).isoformat())
                    leg_start_timeZone = this_event.json_directions_to_this_event[0]['legs'][0]['arrival_time'][
                        'time_zone']
                    leg_summary = "Transit via PreRoute"
                    event_resource = {'end': {"dateTime": leg_end_dateTime,
                                              "timeZone": leg_end_timeZone},
                                      'start': {"dateTime": leg_start_dateTime,
                                                "timeZone": leg_start_timeZone},
                                      'summary': "test event"}
                    service.events().insert(calendarId=ClientEventsList.calendar_id, body=event_resource).execute()

def package_client_data_for_web():
    web_package = []
    for eventsList in eventListList:
        calendar_web_data = {'calendar_summary': eventsList.name, 'events': []}
        for event in eventsList.classified_event_jsons:
            event_web_data = {'event_summary': event.name, 'location': event.location, 'start': event.start_dateTime,
             'end': event.end_dateTime, 'first': event.first_event_of_day, 'last': event.last_event_of_day,
             'is_preroutable': event.is_preroutable}
            calendar_web_data['events'].append(event_web_data)
        web_package.append(calendar_web_data)
    print(web_package)


eventSet = []
eventListList = []
service_creds_pair = get_authentification_creds()
service = service_creds_pair[0]
creds = service_creds_pair[1]
print("creds are of", type(creds))
gather_events()
set_background_booleans_for_events_and_eventsList(eventListList)
for eventList in eventListList:
    eventList.set_scheduling_booleans()
    preroute_client_events_List(eventList)
print(eventListList)
package_client_data_for_web()
