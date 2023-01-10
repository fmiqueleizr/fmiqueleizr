class StateDrone:
    def __init__(self, idDrone, battery, latitude, longitude, altitude, air_speed, heading, low_level_state):
        self.idDrone = idDrone
        self.battery = battery
        self.latitude = latitude
        self.longitude = longitude
        self.altidue = altitude
        self.air_speed = air_speed
        self.heading = heading
        self.low_level_state = low_level_state
     
    def print_idDrone(self):
        print(self.idDrone)

    # @idDrone.setter     
    # def idDrone(self, idDrone):
    #     self.idDrone = idDrone

    # @battery.setter
    # def battery(self, battery):
    #     self.battery = battery

    @property
    def idDrone(self):
        return self.idDrone

    @property
    def get_battery(self):
        return self.battery 
