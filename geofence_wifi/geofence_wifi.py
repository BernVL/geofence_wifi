# geofence_wifi - Disable wifi when inside geofence and enable when .

from csclient import EventingCSClient
from geopy import distance
import time
import json

config = {
    "geofences": [
        #TAPO1
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        #TAPO2
        {
        "lat": 19.433187, 
        "long": -99.113972,
        "radius": 100},
        #TAPO3
        {
        "lat": 19.43376, 
        "long": -99.11226,
        "radius": 100},
        #CEQ ADO
        {
        "lat": 18.52181, 
        "long": -88.29188,
        "radius": 100},
        #CHK ADO
        {
        "lat": 18.643135, 
        "long": -91.812125,
        "radius": 80},
        #CQQ ADO
        {
        "lat": 21.15008, 
        "long": -86.86393,
        "radius": 250},
        #ENCIERRO TERMINAL CHK ADO
        {
        "lat": 19.82266, 
        "long": -90.53135,
        "radius": 100},
        # ENCIERRO THP ADO
        {
        "lat": 18.46176, 
        "long": -97.40352,
        "radius": 170},
        #TALLER CBV ADO
        {
        "lat": 18.88368, 
        "long": -96.91615,
        "radius": 270},
        #Taller COV ADO 1
        {
        "lat": 18.11751, 
        "long": -94.44571,
        "radius": 300},
        #Taller COV ADO 2
        {
        "lat": 18.11934, 
        "long": -94.44341,
        "radius": 150},
        #Taller MEY ADO
        {
        "lat": 20.94525, 
        "long": -89.65784,
        "radius": 300},
        #TALLER OAO ADO
        {
        "lat": 17.03777, 
        "long": -96.70768,
        "radius": 200},
        #TALLER PUP ADO
        {
        "lat": 19.07402, 
        "long": -98.21215,
        "radius": 300},
        #TALLER VEV ADO
        {
        "lat": 19.16494, 
        "long": -96.13568,
        "radius": 300},
        #TALLER VHT ADO
        {
        "lat": 18.00161, 
        "long": -92.92129,
        "radius": 150}
        ],
    "debug": True
}

cp = EventingCSClient('geofence_wifi')

def get_location():
    """Return latitude and longitude as floats"""
    fix = cp.get('status/gps/fix')
    try:
        lat_deg = fix['latitude']['degree']
        lat_min = fix['latitude']['minute']
        lat_sec = fix['latitude']['second']
        lon_deg = fix['longitude']['degree']
        lon_min = fix['longitude']['minute']
        lon_sec = fix['longitude']['second']
        lat = dec(lat_deg, lat_min, lat_sec)
        long = dec(lon_deg, lon_min, lon_sec)
        accuracy = fix.get('accuracy')
        return lat, long, accuracy
    except:
        return None, None, None

def dec(deg, min, sec):
    """Return decimal version of lat or long from deg, min, sec"""
    if str(deg)[0] == '-':
        dec = deg - (min / 60) - (sec / 3600)
    else:
        dec = deg + (min / 60) + (sec / 3600)
    return round(dec, 5)

def disable_wifi(disable):
    cp.put(f'config/wlan/radio/0/enabled', not disable)
    cp.put(f'config/wlan/radio/1/enabled', not disable)

def get_config(name):
    try:
        appdata = cp.get('config/system/sdk/appdata')
        data = json.loads([x["value"] for x in appdata if x["name"] == name][0])
        if data != config:
            cp.log(f'Loaded config: {data}')
            return data
        else:
            return config
    except Exception as e:
        cp.post('config/system/sdk/appdata', {"name": name, "value": json.dumps(config)})
        cp.log(f'Saved config: {config}')
        return config

def debug_log(msg):
    if config["debug"]:
        cp.log(msg)

cp.log('Starting...')
in_geofence = False

def check_geofence(geofence):
    dist = distance.distance((lat, long), (geofence["lat"], geofence["long"])).m
    debug_log(f'Lat: {lat} Long: {long} Distance: {dist}')
    return dist < geofence["radius"]

while True:
    config = get_config('geofence_wifi')
    lat, long, accuracy = get_location()
    if any(check_geofence(g) for g in config['geofences']):
        if not in_geofence:
            in_geofence = True
            cp.log('Entered geofence. Disabling WiFi.')
            disable_wifi(True)
    else:
        if in_geofence:
            in_geofence = False
            cp.log('Exited Geofence.  Enabling WiFi.')
        disable_wifi(False)
    time.sleep(1)