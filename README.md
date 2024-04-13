# Rdio Scanner - OpenMHZ Downstream
This is an middleware for [Rdio-Scanner](https://github.com/chuot/rdio-scanner/) to upload to [OpenMHZ](https://openmhz.com/). This allows you to select what talkgroups are being sent to OpenMHZ. In my case I want to upload all talkgroups to Rdio, but only some to OpenMHZ.

## Setup
This guide assumes you have both [Rdio-Scanner](https://github.com/chuot/rdio-scanner/) and [OpenMHZ](https://openmhz.com/) installed and configure. On Rdio-Scanner, you need to a system and an API Key defined. 

### Install and Run
You can run this locally (Gunicorn) or via Docker. 
#### systems.json file
The `systems.json` file matches at system id from Rdio-Scanner to a shortname in OpenMHZ. These should have a one-to-one link.
```json
{
    "1":"myshortname"
}
```
#### Variables
You can use the .env.example file to create a .env file if you are running locally, or utilize the docker environmental variables for setting the container arguments.<br>
<br>
The configurable variables are
```
OPENMHZ_URL= (default http://127.0.0.1:8080) - the URL that the middleware is publicly accessible. This is used as a return URL for SDRTrunk.
LISTENING_PORT - (default 8080) port that the middleware is listening on
LISTENING_ADDRESS - (default 0.0.0.0) the IP address that Flask binds to
CAPTURE_DIR - (default /var/tmp) the directory the JSON metadata is sent to
WORKERS - (default 2) the number of workers for Flask (should be no more than 2n+1 where n is the number of CPU cores)
```

#### Gunicorn
Gunicorn is a WSGI for Flask. You can run it in the background. You need to clone repository, then install the Python requirements.
```
git clone https://github.com/robertlynch3/rdio-openmhz-downstream.git
cd rdio-openmhz-downstream
pip3 install -r requirements.txt
```
Once you have the requirments installed, you can run Gunicorn via
```
gunicorn server:app --config gunicorn.py
```

You can run Gunicorn as a systemd process, but that is out of scope. Follow [this guide](https://www.edmondchuc.com/blog/deploying-python-flask-with-gunicorn-nginx-and-systemd) for more information.
#### Docker
To run via docker, you must have docker installed. Run the following to bring up the container.

```
docker run -d \
-p 8080:8080 \
-e OPENMHZ_URL=https://api.openmhz.com \
-e LISTEN_ADDRESS=8080 \
-v ./systems.json:/systems.json \
robertlynch3/rdio-openmhz-downstream:latest
```
Use the [docker-compose.yml](docker-compose.yml) file for reference. You can run this as a stand-alone container or incorporate it into an existing Rdio-Scanner docker-compose. 


### Configure
#### Rdio Scanner Configuration
On Rdio-Scanner's admin panel, add a new downstream instance. Configure the URL for the middleware. Set the API Key as the key needed for OpenMHZ




# Issues
Please report any issues via [GitHub issues](https://github.com/robertlynch3/rdio-openmhz-downstream./issues).<br>
<br>
Currently this only supports MP3 uploads, but it is fairly trivial to add other media uploads.
