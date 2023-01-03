import asyncio
from mavsdk import System
from datetime import datetime

import random
import time
from paho.mqtt import client as mqtt_client

import json

import stateDrone


broker = 'localhost'
port = 1883
topic = "python/mqttFM"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = ''
password = ''


gLatitude_deg = ''
gLongitude_deg = ''
gAltitude_m = ''
gBattery = ''
gFlightMode = ''
gHeading = ''
gAirSpeed = ''


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, msg):
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

async def run():

    aux = stateDrone()

    client = connect_mqtt()
    client.loop_start()

    # Init the drone
    drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="udp://:14540")

    # Start the tasks
    asyncio.ensure_future(print_battery(drone))
    # asyncio.ensure_future(print_gps_info(drone))
    # asyncio.ensure_future(print_in_air(drone))
    asyncio.ensure_future(print_position(drone, client))
    asyncio.ensure_future(print_flightMode_info(drone))
    asyncio.ensure_future(print_heading_info(drone))
    asyncio.ensure_future(print_rawGps_info(drone))
    

    asyncio.ensure_future(makeData(client))

    # global number

    # print("variable global:" + str(number))
    # number = number + 12


async def print_battery(drone):
    global gBattery
    async for battery in drone.telemetry.battery():
        # print(f"Battery: {battery.remaining_percent}")
        gBattery = round(battery.remaining_percent * 100)


async def print_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")

async def print_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")

async def print_flightMode_info(drone):
    global gFlightMode 
    async for flightMode in drone.telemetry.flight_mode():
        # print(f"GPS info: {gps_info}")
        gFlightMode = flightMode

async def print_rawGps_info(drone):
    global gAirSpeed 
    async for rawGps in drone.telemetry.raw_gps():
        # print(f"GPS info: {gps_info}")
        gAirSpeed = "{0:.2f}".format(rawGps.velocity_m_s)

async def print_heading_info(drone):
    global gHeading 
    async for heading in drone.telemetry.heading():
        # print(f"GPS info: {gps_info}")
        gHeading = "{0:.2f}".format(heading.heading_deg) 

async def print_position(drone, client):
    # aux = 1

    global gLatitude_deg
    global gLongitude_deg
    global gAltitude_m

    # global number
    async for position in drone.telemetry.position():
        # print(position.latitude_deg, ", ", position.longitude_deg)
        # await asyncio.sleep(120)

        # if (datetime.now().second % 10 == 0):

            gLatitude_deg = str(position.latitude_deg)[:10]
            gLongitude_deg = str(position.longitude_deg)[:10]
            gAltitude_m = str("{0:.2f}".format(position.relative_altitude_m))

            # publish(client, topic, "json: " + str(position.latitude_deg) + ", " + str(position.longitude_deg))

            # stateDrone = {
            #     "idDrone": "0001",
            #     "battery": "",
            #     "latitude": str(position.latitude_deg),
            #     "longitude": str(position.longitude_deg)
            # }

            # publish(client, topic, json.dumps(stateDrone))

            # print(position.latitude_deg, ", ", position.longitude_deg)
            # print(aux)
            # aux = aux + 1
            # Debería publicar los datos del drone para el FrontEnd

            # print("variable global:" + str(number))
            # number = number + 15        

async def makeData(client):
    # global number
    global gBattery
    global gLatitude_deg
    global gLongitude_deg
    global gHeading
    global gFlightMode

    while True:

        # print("variable global:" + str(number))
        # number = number + 15
        await asyncio.sleep(5)

        stateDrone = {
            "idDrone": "0001",
            "battery": str(gBattery),
            "latitude": str(gLatitude_deg),
            "longitude": str(gLongitude_deg),
            "altitude": str(gAltitude_m),
            "air_speed": str(gAirSpeed),
            "heading": str(gHeading),
            "low_level_state": str(gFlightMode),
        }

        # print(json.dumps(stateDrone))
        publish(client, topic, json.dumps(stateDrone))




if __name__ == "__main__":

    

    # Start the main function
    asyncio.ensure_future(run())

    # Runs the event loop until the program is canceled with e.g. CTRL-C
    asyncio.get_event_loop().run_forever()


# Estructura del json que va a publicar el Drone. Esto lo va a tomar el coordinador. Y luego se lo publicará al Front.
# {		
#     "id_drone" : "D001",
#     "battery" :  "80",
#     "status" :  "flying",
#     "latitude" : "-34.550455",
#     "longitude" : "-59.040551",
#     "altitude" : "30",
#     "air_speed" : "5",
#     "heading" :  "90",
#     "mission_step" :  "3",
#     "low_level_state" :  "mission"
# }


