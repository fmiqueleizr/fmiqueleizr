import asyncio
from mavsdk import System

async def run():
    drone = System(mavsdk_server_address='localhost', port=50051)
    await drone.connect(system_address="udp://:14540")

    # asyncio.ensure_future(print_position(drone))

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break

    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(1)
    # To fly drone 20m above the ground plane
    flying_alt = absolute_altitude + 5.0
    
    # goto_location() takes Absolute MSL altitude
    await drone.action.goto_location(-38.074480, -57.574357, flying_alt, 0)

    await asyncio.sleep(40) # Acá debería esperar a que llegue al punto

    print("-- Return")
    await drone.action.return_to_launch()

    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(5)


# async def print_position(drone):
#     async for position in drone.telemetry.position():
#         print(position)
#         await asyncio.sleep(5)        


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
