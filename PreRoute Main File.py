# CHAPTER 1: PreRoute Backend

# STEP 1: IMPORT STATEMENTS HERE

# Import statements here.

from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googlemaps
from datetime import datetime

# Scopes and Keys

CALENDERSCOPES = ['https://www.googleapis.com/auth/calendar']
gmaps = googlemaps.Client(key="AIzaSyDLR45KuaYHoy_RxreHCoQoKuWVPsSOIHY")

# STEP 2: MAIN FUNCTION

def main():

# We begin with standard cloud stuff.

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
        try:
            service = build('calendar', 'v3', credentials=creds)

            print("Fetching the primary calender.")
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = service.events().list(calendarId='primary', timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            print(events_result)

            if not events:
                print('No upcoming events found.')
                return

            for event in events:
                print("Printing events in primary calender.")
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])

        except HttpError as error:
            print('An error occurred: %s' % error)

        if __name__ == '__main__':
            main()



#   STEP 2.2: Geocoding API

#   Appears this is not strictly required. Maybe the above logs us into both?


# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))



#   STEP 2.3: Directions API

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)

print(directions_result)

#   STEP 2.4: Maps Static API



# STEP 3: Building ClientEventsList


main()

#   STEP 3.1: GET PrimaryCalender's contents.
#   STEP 3.2: ...data manipulation...
# STEP 4: Getting Route Data
#   STEP 4.1: GET routes if possible.
#   STEP 5.1: WRITE routes if possible to CALENDER