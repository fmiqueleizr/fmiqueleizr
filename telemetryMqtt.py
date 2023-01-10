import asyncio
from mavsdk import System
from datetime import datetime

import random
import time
from paho.mqtt import client as mqtt_client

import json

# import stateDrone


broker =  '54.233.200.155' # 'localhost'
port = 1883
topic = "/drones/telemetry"
topic_ReceivedCommandForCoordinator = "python/mqttFM/Coordinator/Command"
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
gMissionStep = ''
gStatus = ''


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


def subscribe(client: mqtt_client, drone):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # asyncio.run(doCommand(msg, drone)) 

    client.subscribe(topic_ReceivedCommandForCoordinator)
    client.on_message = on_message
 


async def doCommand(msg, drone):
    # Acá debería tomar lo enviado por el coordinador y realizarlo
    print(f"Commando Recibido `{msg.payload.decode()}` en el topico `{msg.topic}` ")

    # async for terrain_info in drone.telemetry.home():
    #     absolute_altitude = terrain_info.absolute_altitude_m
    #     break
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(1)
    # # To fly drone 20m above the ground plane
    # # flying_alt = absolute_altitude + 5.0
    
    # # goto_location() takes Absolute MSL altitude
    # await drone.action.goto_location(-38.074480, -57.574357, 500, 0)

    # await asyncio.sleep(40) # Acá debería esperar a que llegue al punto

    # print("-- Return")
    # await drone.action.return_to_launch()

async def run():

    # aux = stateDrone()

    client = connect_mqtt()
    client.loop_start()

    # Init the drone
    drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="udp://:14540")

    # Start the tasks
    asyncio.ensure_future(print_battery(drone))
    asyncio.ensure_future(print_position(drone, client))
    asyncio.ensure_future(print_flightMode_info(drone))
    asyncio.ensure_future(print_heading_info(drone))
    asyncio.ensure_future(print_rawGps_info(drone))
    asyncio.ensure_future(print_mission_step(drone))
    asyncio.ensure_future(print_status(drone))
    
    asyncio.ensure_future(receiveCommandForCoordinator(client, drone))

    asyncio.ensure_future(makeData(client))


async def receiveCommandForCoordinator(client,drone):
    subscribe(client, drone)


async def print_status(drone):
    global gStatus
    async for status in drone.telemetry.landed_state():
        gStatus = status

        # UNKNOWN	
        # ON_GROUND	
        # IN_AIR	
        # TAKING_OFF	
        # LANDING 

async def print_mission_step(drone):
    global gMissionStep
    async for mission_step in drone.mission.mission_progress():
        gMissionStep = mission_step.current

async def print_battery(drone):
    global gBattery
    async for battery in drone.telemetry.battery():
        # print(f"Battery: {battery.remaining_percent}")
        gBattery = round(battery.remaining_percent * 100)

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
    global gLatitude_deg
    global gLongitude_deg
    global gAltitude_m

    async for position in drone.telemetry.position():
        gLatitude_deg = str(position.latitude_deg)[:10]
        gLongitude_deg = str(position.longitude_deg)[:10]
        gAltitude_m = str("{0:.2f}".format(position.relative_altitude_m))



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
            "idDrone": "D001",
            "battery": str(gBattery),
            "status": str(gStatus),
            "latitude": str(gLatitude_deg),
            "longitude": str(gLongitude_deg),
            "altitude": str(gAltitude_m),
            "air_speed": str(gAirSpeed),
            "heading": str(gHeading),
            "mission_step": str(gMissionStep),
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


