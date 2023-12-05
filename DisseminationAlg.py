#!/usr/bin/env python

import os
import sys
import optparse
import random
import json
import pandas as pd
# displaying all columns
pd.set_option('display.max_columns', None)

from BicycleClass import BicycleClass

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
JSONBackGroundData = json.load(open('TEST.json'))

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
    # create an empty dataframe
    df = pd.DataFrame(columns=['Vehicle','Collected Roads', 'Connections'])

    # looping for all the steps in de simuation
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # inDistance = []
        allVehicleNames = traci.vehicle.getIDList()
        
        # creating instances of all vehicles and adding them to a list
        if len(allVehicleNames) != len(vehiclesInNetwork):
            # following code should only run once as it is only on spawning of a new vehicle
            for vehName in allVehicleNames:
                if vehName not in vehiclesInNetwork:
                    # print("adding veh " + str(vehName))
                    vehiclesInNetwork[vehName] = BicycleClass(vehName)
                    vehiclesInNetwork[vehName].setDrivenOnRoads(generateListWithRoadsFromJson(len(allVehicleNames)-1)) # minus one because the index of the file starts with 0 and the length of the array is one more        
        
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
                # 25 represents the distance between vehicles for dissemination in meters
                if(dist < 25.0):
                    # print(str(round(dist)) + "m for " + str(vehID) + " and " + str(vehIDOther)) # print what what vehicles are in connection with oneanother
                    
                    vehiclesInNetwork[vehNameOther].recieveDesseminationData(vehiclesInNetwork[vehName].getDisseminationData(), vehName)
                    vehiclesInNetwork[vehName].recieveDesseminationData(vehiclesInNetwork[vehNameOther].getDisseminationData(), vehNameOther)
        step += 1

    # Create a list to store the data
    data = []

    for veh in vehiclesInNetwork:
        #print(str(veh) + " has recieved " +str(round(len(vehiclesInNetwork[veh].getRecievedRoads())*100/len(RoadEdgeValues)))+ "% (" + str(len(vehiclesInNetwork[veh].getRecievedRoads())) + " of " + str(len(RoadEdgeValues)) + ") and has collected " + str(len(vehiclesInNetwork[veh].getRoads())))
        #print("       and has connected with " + str(vehiclesInNetwork[veh].getConnections()))

        collected_roads = vehiclesInNetwork[veh].getRoads()
        connections = vehiclesInNetwork[veh].getConnections()

        # Append the data to the list
        data.append([veh, collected_roads, connections])
        
    # Concatenate the data to the dataframe
    df = pd.concat([df, pd.DataFrame(data, columns=df.columns)], ignore_index=True)

    # Print the dataframe
    print(df)
    df.to_csv('disseminatedData.csv')
    print("end")
    traci.close()
    sys.stdout.flush()
    

def assignValuesToRoadEdges():
    roadEdges = {}
    random.seed(10) #make sure the random numbers are the same everytime. Remove this if this is not wanted behaviour
    for roadId in traci.edge.getIDList():
        # prevent junctions being added to the list
        if roadId[0] != ':':
            roadEdges[roadId] = random.randint(1,9) #value of 1 to (and including) 9 to simulate the road score
    return roadEdges

def generateListWithRoadsFromJson(indexInJsonFile):
    currentJSONElement = JSONBackGroundData[str(indexInJsonFile)]
    returnValue = {}
    for attribute, value in currentJSONElement.items(): # attribute is not used but is necessary to remove the attributes of the json file
        for roadSegment in value:
            if roadSegment not in returnValue:
                returnValue[roadSegment] = roadSegment
    return returnValue

# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    # remove --start (starting the simulation automatically) and --quit-on-end (closes sumo on end of simulation) if this is unwanted behaviour
    traci.start([sumoBinary, "-c", "sumoFiles/DualRoad.sumocfg",
                             "--tripinfo-output", "tripinfo.xml", "--start", "--quit-on-end"])
    run()