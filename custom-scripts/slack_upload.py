from slack_sdk import WebClient
from sys import argv
from json import loads as json_loads, load as json_load
from datetime import datetime
from pytz import timezone
from os import path
from requests import post,put


#
# arguments should be
# [timestamp] "[detectorName]" [description] [recordingRelPath] [filename] [custom]

def custom_script(filename, filepath, detectorName, **kwargs):
    dt = datetime.now()
    # print it
    timestamp=dt.strftime('%Y-%m-%d %H:%M:%S') # formats as 2022-12-31 00:00:00 (Year-Month-Day Hour:Minute:Second)

    file=open(f"{filepath}", "rb")
    # Opens the Slack Connection
    client = WebClient(kwargs['slack-token'])

    client.files_upload_v2(
        channel=kwargs['slack-channel'],
        file=file,
        title=f"{detectorName} Page Received at {timestamp}",
        initial_comment=kwargs['slack-message'].format(timestamp)
    )
    file.close()
    return True



