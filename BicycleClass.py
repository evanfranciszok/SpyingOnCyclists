import random

from SimulationMode import SimulationMode

random.seed(10)
disseminationAmount = 10

class BicycleClass:
    def __init__(self, vehID, disseminationCase):
        self.vehID = vehID
        self.disseminationCase = disseminationCase
        self.drivenOnRoads = {}
        self.roadsReceivedFromOthers = {}
        self.connectedWithCars = {}
        self.amountOfDoubleDataSent = 0
        self.roadsCollected = 0
        self.target = 0

    def addRoad(self, roadId):
        # prevent junctions being added to the list
        if roadId not in self.drivenOnRoads and roadId[0] != ':':
            self.drivenOnRoads[roadId] = [self.vehID]
                        
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
    
    def getName(self):
            return self.vehID
        
    def setTarget(self, target):
        self.target = target
        
    def checkIfTarget(self, possibleTarget):
        return possibleTarget == self.target
    
    def printData(self):
        if self.roadsCollected != 0:
            print(str(self.vehID) + ": " + str(self.amountOfDoubleDataSent) + " of " + str(self.roadsCollected) + ":" + str(len(self.roadsReceivedFromOthers)) + " is " + str(round(self.amountOfDoubleDataSent*100/self.roadsCollected)) + "%.")
        else:
            print(str(self.vehID) + " no roads collected")
        
    def recieveDesseminationData(self, dataFromOtherVehicle, vehIDOther):
        # print("veh " + self.vehID + " has recieved " + str(dataFromOtherVehicle))
        if vehIDOther not in self.connectedWithCars:
            self.connectedWithCars[vehIDOther] = 1
        else:
            self.connectedWithCars[vehIDOther] += 1

        for recievedRoadSegment in dataFromOtherVehicle:
            self.roadsCollected +=1
            if recievedRoadSegment in self.roadsReceivedFromOthers:
                for senderName in dataFromOtherVehicle[recievedRoadSegment]:
                    if senderName not in self.roadsReceivedFromOthers[recievedRoadSegment]:
                        # If the road is already been recieved but is has been collected by another person origionally
                        self.roadsReceivedFromOthers[recievedRoadSegment].append(senderName)
                    else:
                        self.amountOfDoubleDataSent += 1
                        # If the road is already been collected from the same original source (eventhough it possibly came from another person)
                        # if(self.vehID == "Janet_8"):
                            # print(str(self.vehID) + " double data recieved on " + senderName + " : " + recievedRoadSegment + "\n\t::" + str(self.roadsReceivedFromOthers) + "\n\t::" + str(dataFromOtherVehicle))
            else:
                self.roadsReceivedFromOthers[recievedRoadSegment] = dataFromOtherVehicle[recievedRoadSegment]        
        self.roadsReceivedFromOthers = self.roadsReceivedFromOthers | dataFromOtherVehicle
    
    # this is what the bike will disseminate
    # algorithm for disseminating the data
    def getDisseminationData(self):
        # return self.drivenOnRoads # case 0 (no method)
        # if self.disseminationCase is not SimulationMode.Surrounding:
        return self.scramble(self.disseminationCase)
        # else:
        #     return self.surroundingScramble(bikePosition, traci, roadEdgePositions)
        
    def surroundingScramble(self, bikePosition, traci, roadEdgePositions):
        testSelf = list(self.drivenOnRoads)
        testOther = list(self.roadsReceivedFromOthers)
        toBeDisseminatedData = {}
        amountOfOwnData = disseminationAmount*0.5
        
        while len(toBeDisseminatedData) < amountOfOwnData and len(testSelf) > 0:
            edge = random.choice(list(testSelf))
            testSelf.remove(edge)
            roadSegment = roadEdgePositions[edge]
            if traci.simulation.getDistance2D(bikePosition[0], bikePosition[1], roadSegment[0], roadSegment[1], False, False) < 300:
                toBeDisseminatedData[edge] = self.drivenOnRoads[str(edge)]
        while len(toBeDisseminatedData) < disseminationAmount and len(testOther) > 0:
            edge = random.choice(list(testOther))
            testOther.remove(edge)
            roadSegment = roadEdgePositions[edge]
            if traci.simulation.getDistance2D(bikePosition[0], bikePosition[1], roadSegment[0], roadSegment[1], False, False) < 300:
                toBeDisseminatedData[edge] = self.roadsReceivedFromOthers[str(edge)]
        return toBeDisseminatedData
    
    def scramble(self, case):
        returnDict = {}
        # for i in range(random.randint(1,5)):
        amountOfOwnData = disseminationAmount*(case.value/100)
        for i in range(disseminationAmount):
            if amountOfOwnData > i and len(self.drivenOnRoads)>0:
                roadSegment = random.choice(list(self.drivenOnRoads))
                returnDict[roadSegment] = self.drivenOnRoads[str(roadSegment)]
            else:
                # data from other people
                if len(self.roadsReceivedFromOthers) > 0:
                    roadSegment = random.choice(list(self.roadsReceivedFromOthers))
                    returnDict[roadSegment] = self.roadsReceivedFromOthers[str(roadSegment)]
        return returnDict 