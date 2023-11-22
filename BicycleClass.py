class BicycleClass:
    def __init__(self, vehID):
        self.vehID = vehID
        self.drivenOnRoads = {}
        self.roadsReceivedFromOthers = {}

    def addRoad(self, roadId):
        if roadId not in self.drivenOnRoads:
            self.drivenOnRoads[roadId] = roadId

    def printRoads(self):
        print("veh " + self.vehID + " has driven on " + str(self.drivenOnRoads) + "\n     - and recieved from others " + str(self.roadsReceivedFromOthers))
        
    def getRecievedRoads(self):
        return self.roadsReceivedFromOthers
    
    def getRoads(self):
        return self.drivenOnRoads
        
    def recieveDesseminationData(self, dataFromOtherVehicle):
        # print("veh " + self.vehID + " has recieved " + str(dataFromOtherVehicle))
        self.roadsReceivedFromOthers = self.roadsReceivedFromOthers | dataFromOtherVehicle
    
    # this is what the bike will disseminate
    def getDisseminationData(self):
        return self.drivenOnRoads