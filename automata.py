import time
import pywinctl as pwc
from datetime import datetime,timedelta
from dateutil.parser import parse as dtparse
import sys
from colorama import Fore,Style
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import os


application_list=[]

class DataProcessor:
       
        def __init__(self,creds):
            self.creds=creds
          

        def sendData(self,startTime,endTime):
            try:
                print(self.creds)
                service=build("calendar","v3",credentials=self.creds)
                event = {
                'summary': 'NewShit',
                'colorId':'2',
                'description': 'You coded for 6 fucking hours',
                'start': {
                    'dateTime': startTime,
                    'timeZone': 'Asia/Colombo',
                },
                'end': {
                    'dateTime': endTime,
                    'timeZone': 'Asia/Colombo',
                }
                }

                event = service.events().insert(calendarId='primary', body=event).execute()
                print ('Event created: %s' % (event.get('htmlLink')))
            except HttpError as error:
                print(f"got flipped by {error}")

        #Duplicating a day feels useless because you should aim to make tomorrow as an ideal day where you get most of your work done.
        #So in most cases, youre not gonna work for the exact total hours as the ideal day or youre not gonna work between the exact time frames given
        def fetchData(self):

            try:
                service=build("calendar","v3",credentials=self.creds)
                today = datetime.today(); 
                start = (datetime(today.year, today.month, today.day, 00, 00)).isoformat() + 'Z'
                tomorrow = today + timedelta(days=1)
                end =  (datetime(tomorrow.year, tomorrow.month, tomorrow.day, 00, 00)).isoformat() + 'Z'
                events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start,
                    timeMax=end,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
                )
              
                # page_token=None
                # calendar_list = service.calendarList().list().execute()
            
                # for calendar in calendar_list['items']:
                #     print(f"{calendar['summary']}:{calendar['id']}")

                events = events_result.get("items", [])
                for event in events:
                    start_n = event["start"].get("dateTime")
                    end_n=event["end"].get("dateTime")
                    time_format='%H:%M'
                    print("{}:{}-{}".format(datetime.strftime(dtparse(start_n),format=time_format),datetime.strftime(dtparse(end_n),format=time_format),event["summary"]))
            except HttpError as error:
                print(f"got fucked by {error}")
def monitor_mode(creds,application_choice):
    application_was_running=True
    print(application_was_running)
    while True:
        try:
            applications = pwc.getAllAppsNames()
            animation_frames=["waiting for application to open    ","waiting for application to open .","waiting for application to open ..","waiting for application to open ..."]
            idx=0
            while application_choice not in applications and not application_was_running:
                applications = pwc.getAllAppsNames()
                if application_choice in applications:
                    application_was_running=True
                    break
                sys.stdout.write(animation_frames[idx%len(animation_frames)])
                sys.stdout.write('\r')
                sys.stdout.flush()
                idx+=1
                time.sleep(0.5)

            if application_choice not in application_list and application_choice in applications:
                CURR_TIME=datetime.utcnow()
                application_list.append(application_choice)

            elif application_choice not in applications:
                endtime=datetime.utcnow()
                delta=endtime-CURR_TIME
                duration=delta.total_seconds()
                dt_processor=DataProcessor(creds=creds)
                dt_processor.sendData(startTime=(endtime+timedelta(hours=5,minutes=30)).isoformat(),endTime=(endtime+timedelta(hours=5,minutes=30+divmod(duration,60)[0])).isoformat())
                print("Your application was open for {} minutes ({}:{})".format(divmod(duration,60)[0],CURR_TIME,endtime))
                break
            time.sleep(1)
        except KeyboardInterrupt:
            break
        #time.sleep()

def main(creds):

    print(Fore.RED+'''
            
    $$$$$$\  $$\            $$\     $$\     
    $$  __$$\ $$ |           $$ |    $$ |    
    $$ /  \__|$$ | $$$$$$\ $$$$$$\ $$$$$$\   
    \$$$$$$\  $$ | \____$$\\_$$  _|\_$$  _|  
    \____$$\ $$ | $$$$$$$ | $$ |    $$ |    
    $$\   $$ |$$ |$$  __$$ | $$ |$$\ $$ |$$\ 
    \$$$$$$  |$$ |\$$$$$$$ | \$$$$  |\$$$$  |
    \______/ \__| \_______|  \____/  \____/ 
                                                                                
    ''')
    print(Style.RESET_ALL)
    print("Greetings Thee Wretched Imbecile!\n",end="")
    print("Picketh what thee wanteth :")
    print("\t{}\n\t{}".format("1) Duplicate a Weekday as Tomorrow","2) Event Tracker"))
    choice=input(":")
    match choice:
        case "1":
            print("Nope!")
        case "2":
            print("Opening Event Tracker")
            applications = pwc.getAllAppsNames()
            app_array=[]
            idx=1
            for application in applications:
                print("\t{}:{}".format(idx,application))
                app_array.append(application)
                idx+=1
            application_choice=int(input(":"))
            monitor_mode(creds,app_array[application_choice-1])


if __name__=='__main__':
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds=None
    if os.path.exists("token.json"):
            creds=Credentials.from_authorized_user_file("token.json",SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow=InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES)
            creds=flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
  
    main(creds)


"""
The script has several options to choose : 1) Duplicate Today as Tomorrow
                                           2) Event Tracker

Case 1)

Case 2)
     + which program do you want to monitor : lists down the programs
     + starts the timer
     + stops the timer and updates the event according to the app usage

TODO: Create an application list to track and make the times round off to the nearest multiple of 10
"""