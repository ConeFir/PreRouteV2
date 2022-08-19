# SPECIAL NOTE: Updating PreRoute 2 to add the following functionalities:
# Fetch all of the user calendars, and give them an option to choose among them.
# Cut down the menu. Now you just pick a calender, and decide to arrive "just in time" or "leave right away" for each event.
# Later versions should also give the option to pick one option and apply it to the entire calender.

# IMPORT STATEMENTS

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

#SCOPES

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")

# MAIN LOOP

def main():
    missing_value_counter=0
    menu_loop = 1
    while menu_loop == 1:

# STARTUP CREDENTIALIZATION

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

# PRINT MAIN MENU

        print("Welcome to PreRoute V2.")
        print("Press 1 to PreRoute a calender, and 2 to exit.")
        print("Press 3 to print a CalenderListJson, a calendar json, and the eventslist json.")
        menu_input = input("Which would you prefer?")

# GIVE LIST OF CALENDARS AND CHOICE AMONG THEM.

        if menu_input == "1":
            print("Okay, I'm downloading your calenders now. Here they are:")
            service = build('calendar', 'v3', credentials=creds)
            page_token = None
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            # for debugging: print(calendar_list)
            calender_choice_number = 1
            for calendar_list_entry in calendar_list['items']:
                print("(", calender_choice_number, ") ", calendar_list_entry['summary'])
                calender_choice_number += 1
            calendar_number_to_preroute = input("Enter the number of the calendar you want to PreRoute?")
            try:
                calendar_to_preroute = calendar_list['items'][int(calendar_number_to_preroute)-1]
                print("Calendar_to_preroute set to", calendar_to_preroute['summary'])
            except:
                print("Error: Either something is wrong with the indicies or something is wrong with your input.")
                break

# GET LIST OF EVENTS IN CHOSEN CALENDAR.

            print("I will now print the events in ", calendar_to_preroute['summary'])
            try:
                service = build('calendar', 'v3', credentials=creds)
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                events_result = service.events().list(calendarId=calendar_to_preroute['id'], timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
                events = events_result.get('items', [])

                if not events:
                    print('No upcoming events found.')
                    return

# CHECK CHOSEN CALENDAR IS PREROUTABLE.

                event_count = 1
                for event in events:
                    if event['location'] = None:
                        print(event['summary'], "cannot be PreRouted because it does not have a location.")
                        missing_value_counter = 1
                    if event['start'] = None:
                        print(event['summary'], "cannot be PreRouted because it does not have start time.")
                        missing_value_counter = 1
                    if event['end'] = None:
                        print(event['summary'], "cannot be PreRouted because it does not have a start time.")
                        missing_value_counter = 1
                    if missing_value_counter == 1:
                        print("This calender cannot be prerouted.")
                        break
                    if missing_value_counter != 1:
                        print("(", event_count, ")", event['summary'], event['location'])
                        print("We can PreRoute this calender.")
            except HttpError as error:
                print('An error occurred: %s' % error)

# GET END AND START TIME, STORE AS DEPARTURE_END-TIME and ARRIVAL_START-TIME.
# AT THIS POINT, WHAT DO WE KNOW?
            # We know that every event in the calendar has 

            for event in events:
                departure_location = event['location']
                departure_endTime = dateutil.parser.isoparse(event['end']['dateTime'])
                if events[events.index(event)+1] != None:
                    next_event = events[events.index(event)+1]
                if events[events.index(event)+1]['location'] != None:
                    arrival_location = next_event['location']
                if events[events.index(event)+1]['location'] != None:
                    arrival_location = dateutil.parser.isoparse(next_event['end']['dateTime'])
                if events[events.index(event)+1] == None:
                    print("There is no next event.")
                if  events[events.index(event)+1]['location'] != None:
                    print("There is no event location")
                if events[events.index(event)+1] == None or events[events.index(event)+1]['location'] != None:
                    print("There was an error with finding the next event or the next event's location.")
                    break

                arrival_location = events[next_event]['location']
                departure_endTime = dateutil.parser.isoparse(event['end']['dateTime'])

            # Get directions

            try:
                directions_result = gmaps.directions(destination=str(arrival_location), origin=str(departure_location),
                                     mode="transit",
                                     departure_time=departure_endTime)
                print(directions_result)
            except BaseException as error:
                print("Error: Directions returns error")

# Store the data about about legs in lists. Note that this code, as written, assumes a single leg. FIX ME.

            first_leg_arrival = directions_result[0]['legs'][0]['arrival_time']['value']
            print("arrival data is", first_leg_arrival)
            print("arrival data type is,", type(first_leg_arrival))
            first_leg_arrival_timeZone = directions_result[0]['legs'][0]['arrival_time']['time_zone']
            first_leg_departure = directions_result[0]['legs'][0]['departure_time']['value']
            first_leg_departure_timeZone = directions_result[0]['legs'][0]['departure_time']['time_zone']
            print("departure data is", first_leg_departure)
            print("departure data type is,", type(first_leg_departure))
            print("Converting departure and arrival to date-time.")
            first_leg_arrival_datetime = datetime.fromtimestamp(first_leg_arrival)
            first_leg_departure_datetime = datetime.fromtimestamp(first_leg_departure)
            first_leg_arrival_iso = first_leg_arrival_datetime.isoformat()
            first_leg_departure_iso = first_leg_departure_datetime.isoformat()
            print("departure data is", first_leg_departure_datetime)
            print("departure data type is,", type(first_leg_departure_datetime))
            print("arrival data is", first_leg_arrival_datetime)
            print("arrival data type is,", type(first_leg_arrival_datetime))


# Create a calender event based off of this data, which begins the first_leg departure and ends with first_leg arrival.

# NOTE I'M NOT SURE ABT DATATYPES HERE.

            print("Adding new event with the departure time as the start-time and arrival time-as end time", )
            event_body = {'start': {'dateTime': first_leg_departure_iso, 'timeZone': first_leg_departure_timeZone},
                          'end': {'dateTime': first_leg_departure_iso, 'timeZone': first_leg_arrival_timeZone},
                          'description': "This event scheduled using PreRoute",
                          'summary': "PreRoute: Bus trip"}

            PreRouted_Event = service.events().insert(calendarId="t8g3fh8gtco10791c4f9m0q9hc@group.calendar.google.com",
                                                    body=event_body).execute()
print("I did it!")
main()



# PILE OF STUFF:

# This is the second half of the quickstart. What it does is run the build, get the events, print them, error on failure.
