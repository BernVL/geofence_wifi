# geofence_wifi - Disable wifi when inside geofence and enable when .

from csclient import EventingCSClient
from geopy import distance
import time
import json

config = {
    "geofences": [{
        #Ejemplo
        "lat": 43.67313,
        "long": -116.29205,
        "radius": 10},
        #TAPO
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        #Chetumal
        {
        "lat": 18.52181, 
        "long": -88.29188,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100},
        {
        "lat": 19.43017,
        "long": -99.11219,
        "radius": 100}
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
while True:
    config = get_config('geofence_wifi')
    lat, long, accuracy = get_location()
    for geofence in config["geofences"]:
        dist = distance.distance((lat, long), (geofence["lat"], geofence["long"])).m
        debug_log(f'Lat: {lat} Long: {long} Distance: {dist}')
        if dist < geofence["radius"] and not in_geofence:
            in_geofence = True
            cp.log('Entered geofence. Disabling WiFi.')
            disable_wifi(True)
        elif dist > geofence["radius"] and in_geofence:
            in_geofence = False
            cp.log('Exited Geofence.  Enabling WiFi.')
            disable_wifi(False)
    time.sleep(1)
