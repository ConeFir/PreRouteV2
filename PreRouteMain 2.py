# SPECIAL NOTE: This version has been modified so that it deals only with the PreRoute_Test_Case calendar.

# STEP 1: BACKGROUND STUFF

# STEP 1.1: Import statements.
#   AIM: Import all relevant libraries, including maps, google api, and datetime.
#   TO DO: Include tkinter.
#   LAST CHANGED:   6-17

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
import json

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")

def main():

# STEP 3.1: Establish main loop

    menu_loop = 1
    while menu_loop == 1:

# STEP 3.2: Run credentials process

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

# STEP 3.2: Enter main menu loop.
        print("Welcome to PreRoute V2.")
        print("Press 1 to download and print calendar.")
        print("Press 2 to check if calendar is pre-routable.")
        print("Press 3 to PreRoute Calendar by departure.")
        print("Press 4 to PreRoute Calendar by arrival.")
        print("Press 5 to exit.")
        menu_input = input("What shall I do?")
        if menu_input == "1":
            print("I am now downloading and printing primary calendar.")
            try:
                service = build('calendar', 'v3', credentials=creds)
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                events_result = service.events().list(calendarId="t8g3fh8gtco10791c4f9m0q9hc@group.calendar.google.com", timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
                events = events_result.get('items', [])

                if not events:
                    print('No upcoming events found.')
                    return

                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(event['summary'], event['location'])

            except HttpError as error:
                print('An error occurred: %s' % error)

        if menu_input == "2":
            print("I am now downloading primary calendar.")
            try:
                service = build('calendar', 'v3', credentials=creds)
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                events_result = service.events().list(calendarId="t8g3fh8gtco10791c4f9m0q9hc@group.calendar.google.com", timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
                events = events_result.get('items', [])

                if not events:
                    print("No upcoming events found, so I cannot check for locations.")
                    return

                for event in events:
                    try:
                        print(event['summary'], event['location'])
                    except:
                        print(event['summary'], "is not preroutable because it does not have a location.")
                    else:
                        print("This calendar can be PreRouted.")

            except HttpError as error:
                print('An error occurred: %s' % error)

        if menu_input == "3":
            print("I am now downloading PreRoute_Test_Case calendar.")
            try:
                service = build('calendar', 'v3', credentials=creds)
                now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
                events_result = service.events().list(calendarId="t8g3fh8gtco10791c4f9m0q9hc@group.calendar.google.com",
                                          timeMin=now, singleEvents=True,
                                          orderBy='startTime').execute()
                events = events_result.get('items', [])

                if not events:
                    print("No upcoming events found in this calendar, so we cannot PreRoute it.")
                    return

            except HttpError as error:
                print('An error occurred: %s' % error)

            for event in events:
                try:
                    print(event['summary'], "which occurs at ", event['location'])
                except:
                    print(event['summary'], "is not preroutable because it does not have a location.")
                else:
                    print("This calendar can be PreRouted.")
                finally:
                    continue

            print("I am now PreRouting this calendar.")

        # CHECK END AND START TIME, STORE AS DEPARTURE_END-TIME and ARRIVAL_START-TIME

            departure_count = 0
            for event in events:
                if departure_count == 0:
                    departure_location = event['location']
                    departure_endTime = dateutil.parser.isoparse(event['end']['dateTime'])
                    departure_count = 1
                if departure_count == 1:
                    arrival_location = event['location']
                    arrival_startTime = dateutil.parser.isoparse(event['end']['dateTime'])

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
