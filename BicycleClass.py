class BicycleClass:
    def __init__(self, vehID):
        self.vehID = vehID
        self.drivenOnRoads = {}
        self.roadsReceivedFromOthers = {}
        self.connectedWithCars = {}

    def addRoad(self, roadId):
        if roadId not in self.drivenOnRoads:
            self.drivenOnRoads[roadId] = roadId

    def printRoads(self):
        print("veh " + self.vehID + " has driven on " + str(self.drivenOnRoads) + "\n     - and recieved from others " + str(self.roadsReceivedFromOthers))
        
    def getRecievedRoads(self):
        return self.roadsReceivedFromOthers
    
    def getRoads(self):
        return self.drivenOnRoads
    
    def getConnections(self):
        return self.connectedWithCars
        
    def recieveDesseminationData(self, dataFromOtherVehicle, vehIDOther):
        # print("veh " + self.vehID + " has recieved " + str(dataFromOtherVehicle))
        if vehIDOther not in self.connectedWithCars:
            self.connectedWithCars[vehIDOther] = 1
        else:
            self.connectedWithCars[vehIDOther] += 1
        self.roadsReceivedFromOthers = self.roadsReceivedFromOthers | dataFromOtherVehicle
    
    # this is what the bike will disseminate
    # algorithm for disseminating the data
    def getDisseminationData(self):
        return self.drivenOnRoads