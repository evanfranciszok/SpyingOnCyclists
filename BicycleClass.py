class BicycleClass:
    def __init__(self, vehID):
        self.vehID = vehID
        self.drivenOnRoads = []

    def addRoad(self, roadId):
        if roadId not in self.drivenOnRoads:
            self.drivenOnRoads.append(roadId)

    def printRoads(self):
        print("veh " + self.vehID + " has driven on " + str(self.drivenOnRoads))