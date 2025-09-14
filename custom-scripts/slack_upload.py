from slack_sdk import WebClient
from sys import argv
from json import loads as json_loads, load as json_load
from datetime import datetime
from pytz import timezone
from os import path
from requests import post


#
# arguments should be 
# [timestamp] "[detectorName]" [description] [recordingRelPath] [filename] [custom]

def custom_script(file, filename, detectorName, **kwargs):

    dt = datetime.now
    # print it
    timestamp=dt.strftime('%Y-%m-%d %H:%M:%S') # formats as 2022-12-31 00:00:00 (Year-Month-Day Hour:Minute:Second)



    # Opens the Slack Connection
    client = WebClient(kwargs['slack_token']) 
    url=client.files_getUploadURLExternal(filename=filename, length=len(file))
    file_id=url['file_id']
    url=url['upload_url']

    client.files_completeUploadExternal(
        channel_id=kwargs['slack-channel'],
        files=[{'id':file_id, 'title':f"{detectorName} Page Received"}],
        initial_comment=kwargs['slack-message'].format(timestamp)
    )
    return True



