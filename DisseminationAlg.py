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
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # inDistance = []
        allVehicleNames = traci.vehicle.getIDList()
        
        # creating instances of all vehicles and adding them to a list
        if len(allVehicleNames) != len(vehiclesInNetwork):
            for vehName in allVehicleNames:
                if vehName not in vehiclesInNetwork:
                    # print("adding veh " + str(vehName))
                    vehiclesInNetwork[vehName] = BicycleClass(vehName)
        
        # looping through all vehicles currently on the map
        CurrentNoOfVehicle = 0; 
        for vehName in allVehicleNames:
            
            # add road to vehicle
            vehiclesInNetwork[vehName].addRoad(traci.vehicle.getRoadID(vehName))
            
            CurrentNoOfVehicle+=1
            ownPos = traci.vehicle.getPosition(vehName)
            for otherVeh in range(len(allVehicleNames)-CurrentNoOfVehicle):
                vehNameOther = allVehicleNames[otherVeh+CurrentNoOfVehicle]
                otherPos = traci.vehicle.getPosition(vehNameOther)
                dist = traci.simulation.getDistance2D(ownPos[0], ownPos[1], otherPos[0], otherPos[1], False, False)
                if(dist < 25.0):
                    # print(str(round(dist)) + "m for " + str(vehID) + " and " + str(vehIDOther)) # print what what vehicles are in connection with oneanother
                    
                    vehiclesInNetwork[vehNameOther].recieveDesseminationData(vehiclesInNetwork[vehName].getDisseminationData())
                    vehiclesInNetwork[vehName].recieveDesseminationData(vehiclesInNetwork[vehNameOther].getDisseminationData())
        # print(step)
        step += 1

    for veh in vehiclesInNetwork:
        print(str(len(vehiclesInNetwork[veh].getRecievedRoads())) + " of " + str(len(RoadEdgeValues)) + " and has itself driven on " + str(len(vehiclesInNetwork[veh].getRoads())))
        print(str(veh) + " has recieved " + str(round(len(vehiclesInNetwork[veh].getRecievedRoads())*100/len(RoadEdgeValues))) + "% of total road Network")
        
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