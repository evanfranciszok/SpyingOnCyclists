#!/usr/bin/env python

import os
import sys
import optparse
import random
from BicycleClass import BicycleClass

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():
    step = 0
    RoadEdgeValues = assignValuesToRoadEdges()
    vehiclesInNetwork = {}
    # print(RoadEdgeValues)
    while traci.simulation.getMinExpectedNumber() > 0: # type: ignore
        traci.simulationStep()
        inDistance = []
        vehicleList = traci.vehicle.getIDList()
        CurrentNoOfVehicle = 0; 
        for vehID in vehicleList:
            # creating instances of all vehicles and adding them to a list
            if vehID not in vehiclesInNetwork:
                vehiclesInNetwork[vehID] = BicycleClass(vehID)
            
            # add road to vehicle
            vehiclesInNetwork[vehID].addRoad(traci.vehicle.getRoadID(vehID))
            
            CurrentNoOfVehicle+=1
            ownPos = traci.vehicle.getPosition(vehID)
            for otherID in range(len(vehicleList)-CurrentNoOfVehicle):
                vehIDOther = vehicleList[otherID+CurrentNoOfVehicle]
                otherPos = traci.vehicle.getPosition(vehIDOther)
                dist = traci.simulation.getDistance2D(ownPos[0], ownPos[1], otherPos[0], otherPos[1], False, False)
                if(dist < 25.0):
                    print(str(round(dist)) + "m for " + str(vehID) + " and " + str(vehIDOther))
                    inDistance.append(tuple((str(vehID), str(vehIDOther))))
        # print(step)
        step += 1

    for veh in vehiclesInNetwork:
        print(veh)
        print(vehiclesInNetwork[veh].printRoads())
        
    print("end")
    traci.close()
    sys.stdout.flush()
    

def assignValuesToRoadEdges():
    roadEdges = {}
    random.seed(10) #make sure the random numbers are the same everytime. Remove this if this is not wanted behaviour
    for roadId in traci.edge.getIDList():
        roadEdges[roadId] = random.randint(1,9)#value of 1 to (and including) 9 to simulate the road score
    return roadEdges

# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "sumoFiles/DualRoad.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()