import random

random.seed(10)

class BicycleClass:
    def __init__(self, vehID):
        self.vehID = vehID
        self.drivenOnRoads = {}
        self.roadsReceivedFromOthers = {}
        self.connectedWithCars = {}

    def addRoad(self, roadId):
        # prevent junctions being added to the list
        if roadId not in self.drivenOnRoads and roadId[0] != ':':
            self.drivenOnRoads[roadId] = roadId
            
    def setDrivenOnRoads(self, roads):
        self.drivenOnRoads = roads

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
        # return self.drivenOnRoads # case 0 (no method)
        return self.scramble()
    
    def scramble(self):
        returnDict = {}
        for i in range(random.randint(1,5)):
            if random.randint(1,4) == 1:
                roadSegment = random.choice(list(self.drivenOnRoads.values()))
                returnDict[roadSegment] = roadSegment
            else:
                roadSegment = random.choice(list(self.roadsReceivedFromOthers.values()))
                returnDict[roadSegment] = roadSegment
        return returnDict