# AIMS FOR THIS DRAFT:
# We do this with functions and classes.
# The core functions will be:
#   1.)
# IMPORTS

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

# SCOPES

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")

# CLASS DEFINITIONS:

# So, my aim here is to create a series of classes, for calendars, calendarlists

class Calendar_List_Class:
    def __init__(self, calenderList_json):
        self.etag = json["etag"]
        self.nextPageToken = json["nextPageToken"]

    def list_calendars(self):

        calender_choice_number = 1
        for calendar_list_entry in json['items']:
            print("(", calender_choice_number, ") ", calendar_list_entry['summary'])
            calender_choice_number += 1
        calendar_number_to_preroute = input("Enter the number of the calendar you want to PreRoute?")
        try:
            calendar_to_preroute = calendar_list['items'][int(calendar_number_to_preroute) - 1]
            print("Calendar_to_preroute set to", calendar_to_preroute['summary'])
        except:
            print("Error: Either something is wrong with the indicies or something is wrong with your input.")

    def create_all_calendars(self):

        for calendar_list_entry in json['items']:
            calendar_class(calendar_list_entry)

class Calendar_Class:
    def __init__(self, calendarList_item_json):
        self.etag = calendarList_item_json['etag']
        self.id = calendarList_item_json['id']
        self.summary = calendarList_item_json[]
        self.location = calendarList_item_json[]
        self.timezone = calendarList_item_json[]



def credential_flow():

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


def download_and_print_calendarList():

        print("Okay, I'm downloading your calenders now. Here they are:")
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', CALENDERSCOPES)
        if not creds or not creds.valid:
            credential_flow()
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
            calendar_to_preroute = calendar_list['items'][int(calendar_number_to_preroute) - 1]
            print("Calendar_to_preroute set to", calendar_to_preroute['summary'])
        except:
            print("Error: Either something is wrong with the indicies or something is wrong with your input.")





def main():
    credential_flow()
    download_and_print_calendarList()

main()