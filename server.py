#!/usr/bin/env python
#
# server.py
#
#

from flask import Flask, request
from requests import post
from json import load, dumps, loads
import random
import string
from dotenv import load_dotenv
from os import remove, getenv, path, makedirs
from sys import exit, path as sys_path
from icad_tone_detection import tone_detect
import importlib



# Gets the file path to find the config.json file
try:
    file_path=path.abspath(path.dirname( __file__ ))
except:
    file_path="."

# opens config.json
try:
    with open(file_path+'/systems.json') as jsonfile:
        systemFile=load(jsonfile)
except:
    print('Could not find systems.json file')
    exit()

try:
    with open(file_path+'/tones.json') as jsonfile:
        tonesFile=load(jsonfile)
except:
    print('Could not find tones.json file')
    tonesFile=[]

# tones.json may hold a single tone-group object (legacy) or a list of them
if isinstance(tonesFile, dict):
    tonesFile=[tonesFile]

custom_scripts={}
for toneGroup in tonesFile:
    script_path=toneGroup.get('script-path')
    script_module=toneGroup.get('script-module', 'slack_upload')
    if script_path and script_module not in custom_scripts:
        if script_path not in sys_path:
            sys_path.append(script_path)
        custom_scripts[script_module]=importlib.import_module(script_module).custom_script

from datetime import datetime
from calendar import timegm

load_dotenv() 

app = Flask(__name__)
app.secret_key=''.join(random.choices(string.ascii_lowercase, k=85))

# Determines if the directory exists or not

OPENMHZ_URL=getenv('OPENMHZ_URL', 'https://api.openmhz.com')
CAPTURE_DIR=getenv('CAPTURE_DIR','/var/tmp/')

if not path.isdir(CAPTURE_DIR):
    makedirs(CAPTURE_DIR)

app.config['UPLOAD_FOLDER'] = CAPTURE_DIR


@app.route('/api/call-upload', methods=['POST'])
def rdio_upload():
    # Responds to SDRTrunk's test

    

    if 'audio' in request.files:
        data=dict(request.form)
        if data['system'] not in systemFile:
            return('System Shortname not found'), 500 
        if 'two-tone' in systemFile[data['system']] and systemFile[data['system']]['two-tone']==True:
            file=request.files['audio']
            file.save(f'{CAPTURE_DIR}/{file.filename}')
            filename=file.filename
            filepath=f"{CAPTURE_DIR}/{file.filename}"
            result=tone_detect(open(f"{filepath}", "rb"), detect_pulsed=False, detect_long=False, detect_hi_low=False, detect_mdc=False).two_tone_result
            for qc in result:
                detected_a, detected_b=qc['detected'][0], qc['detected'][1]
                for toneGroup in tonesFile:
                    tolerance_hz=toneGroup.get('tolerance_hz', 2)
                    if abs(detected_a-toneGroup['toneA'])<=tolerance_hz and abs(detected_b-toneGroup['toneB'])<=tolerance_hz:
                        script_module=toneGroup.get('script-module', 'slack_upload')
                        custom_scripts[script_module](detectorName=toneGroup['name'], filename=filename, filepath=filepath, **toneGroup.get('customVariables', {}))
            remove(f"{filepath}")
            return("Call imported successfully.\n",200)
        else:
            start_time=int(timegm(datetime.strptime(data['dateTime'], "%Y-%m-%dT%H:%M:%SZ").timetuple()))
            duration=0

            duration=sum([freq['len'] for freq in loads(data['frequencies'])])
            file=request.files['audio']
            file.save(f'{CAPTURE_DIR}/{file.filename}')
            a=post(f"{OPENMHZ_URL}/{systemFile[data['system']]}/upload",
                files={'call':open(f"{CAPTURE_DIR}/{request.files['audio'].filename}", "rb") },
                data={
                    'talkgroup_num':data['talkgroup'],
                    'freq':data['frequency'],
                    'start_time':start_time,
                    'stop_time':start_time+duration,
                    'call_length':duration,
                    'emergency':0,
                    'source_list':dumps(loads(data['sources'])),
                    'api_key': data['key']
                })
            remove(f"{CAPTURE_DIR}/{request.files['audio'].filename}")
            return("Call imported successfully.\n",200)
    else:
        return('System Shortname not found'), 500 






if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser() 
    parser.add_argument('--debug',action='store_true')
    args = parser.parse_args()
    
    app.run(host=getenv('LISTEN_ADDRESS','0.0.0.0'), port=getenv('LISTEN_PORT','8080'), debug=args.debug)