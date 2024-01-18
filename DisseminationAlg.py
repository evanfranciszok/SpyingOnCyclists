#!/usr/bin/env python

import os
import sys
import optparse
import random
import pandas as pd

# displaying all columns
pd.set_option('display.max_columns', None)

# include the other files of this project
from SimulationMode import SimulationMode
from Mapsize import Mapsize
from BicycleClass import BicycleClass
 
# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
# visualizeCoverage = True traci.gui.toggleSelection(segment, "edge")
RoadEdgeValues = {}

# for writing data to a csv file
completionData = []

from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# contains TraCI control loop
def run(case, vehAmount, mapSize, seed):
    random.seed(seed)
    step = 0
    bikeObjectsInNetwork = {}
    roadEdgeValues = assignValuesToRoadEdges()
    distancesBetweenBikes = {}
    endSimulation = False
    
    while traci.simulation.getMinExpectedNumber() > 0 and not endSimulation:
        traci.simulationStep()
        
        traciActualBikesInNetwork = set(traci.vehicle.getIDList())
        
        # limit veh to vehamount
        if len(bikeObjectsInNetwork) >= vehAmount:
            # Wrong bikes are bikes that are not supposed to be in the networ
            removeWrongBikesFromNetwork(bikeObjectsInNetwork, traciActualBikesInNetwork)
        addingNewOrMissingBikesToNetwork(case, step, bikeObjectsInNetwork, roadEdgeValues, traciActualBikesInNetwork)
        
        ListOfTheBikeObjectsInNetwork = list(traciActualBikesInNetwork)
        bikeIndex = 0
        mostIndexed = ["0",-1]
        for nameOfBike in ListOfTheBikeObjectsInNetwork:
            bikeObject = bikeObjectsInNetwork[nameOfBike]
            bikePosition = traci.vehicle.getPosition(nameOfBike)
            test = traci.vehicle.getRoadID(nameOfBike)
            bikeObject.addRoad(test)
            
            if len(bikeObject.getRecievedRoads()) > mostIndexed[1]:
                mostIndexed = [nameOfBike, len(bikeObject.getRecievedRoads())]
            
            #update route
            if bikeObject.checkIfTarget(traci.vehicle.getRoadID(nameOfBike)):
                setSegmentTarget(bikeObject, random.choice(list(roadEdgeValues)))
                
            # disseminate
            bikeIndex+=1
            for otherBikeIndex in range(len(traciActualBikesInNetwork)-bikeIndex):
                nameOfComparisonBike = ListOfTheBikeObjectsInNetwork[otherBikeIndex+bikeIndex]
                comparisonBikeObject = bikeObjectsInNetwork[nameOfComparisonBike]
                comparisonBikePosition = traci.vehicle.getPosition(nameOfComparisonBike)
                
                hashOfBikes = str(hash(nameOfBike) + hash(nameOfComparisonBike))
                if hashOfBikes in distancesBetweenBikes and distancesBetweenBikes.get(hashOfBikes) > 100:
                        distancesBetweenBikes[hashOfBikes] = distancesBetweenBikes.get(hashOfBikes)-30
                else:
                    distanceBetweenBikeAndComparisonBike = traci.simulation.getDistance2D(bikePosition[0], bikePosition[1], comparisonBikePosition[0], comparisonBikePosition[1], False, False)
                    distancesBetweenBikes[hashOfBikes] = distanceBetweenBikeAndComparisonBike
                    # 25 represents the distance between vehicles for dissemination in meters
                    if distanceBetweenBikeAndComparisonBike < 25.0:
                        dataVeh = bikeObject.getDisseminationData()
                        dataVehOther = comparisonBikeObject.getDisseminationData()
                        comparisonBikeObject.recieveDesseminationData(dataVeh, nameOfBike)
                        bikeObject.recieveDesseminationData(dataVehOther, nameOfComparisonBike)
        
        print(str(round(mostIndexed[1]/len(roadEdgeValues)*100)) + '%')
        
        if mostIndexed[1] >= len(roadEdgeValues) or step >= 43200:
            endSimulation = True
            if step >= 43200:
                # undetermined because the simulation took more than 12 (simulated) hours to complete
                completionData.append([str(case), vehAmount, "undetermined", str(mapSize) ,seed])
            else:
                completionData.append([str(case), vehAmount, str(step), str(mapSize) ,seed])
        step += 1
    traci.close()
    sys.stdout.flush()

def addingNewOrMissingBikesToNetwork(case, step, bikeObjectsInNetwork, RoadEdgeValues, traciActualBikesInNetwork):
    lostAndMissingBikesInNetwork = set(bikeObjectsInNetwork.keys()).symmetric_difference(traciActualBikesInNetwork)
    for bikeToBeAdded in lostAndMissingBikesInNetwork:
        if bikeToBeAdded not in bikeObjectsInNetwork.keys():
            bikeObjectsInNetwork[bikeToBeAdded] = BicycleClass(bikeToBeAdded, case)
            # Adding random Route to bike
        else:
            try:
                routeID = random.choice(list(RoadEdgeValues))
                traci.route.add(str(step), [routeID])
                traci.vehicle.add(vehID=bikeToBeAdded,routeID=str(step), typeID="bicycle")
                setSegmentTarget(bikeObjectsInNetwork[bikeToBeAdded], random.choice(list(RoadEdgeValues)))
            except:
                    # it does sometimes happen that it doesnt work. But for simulation purposes does this not matter
                print("error adding will try again next step")

def removeWrongBikesFromNetwork(bikeObjectsInNetwork, traciActualBikesInNetwork):
    wrongBikesInNetwork = traciActualBikesInNetwork.difference(set(bikeObjectsInNetwork.keys())) 
    if len(wrongBikesInNetwork) != 0:
        for wrongBike in wrongBikesInNetwork:
            traci.vehicle.remove(wrongBike)
            traciActualBikesInNetwork.remove(wrongBike)

def assignValuesToRoadEdges():
    roadEdges = {}
    #make sure the random numbers are the same everytime. Remove this if this is not wanted behaviour
    for roadId in traci.edge.getIDList():
        # prevent junctions being added to the list
        if roadId[0] != ':':
            #value of 1 to (and including) 9 to simulate the road score
            roadEdges[roadId] = random.randint(1,9)
    return roadEdges

def setSegmentTarget(vehicle, segment):
    vehicle.setTarget(segment)
    traci.vehicle.changeTarget(vehicle.getName(),segment)

def StartTraci(mapsize):
    # remove --start (starting the simulation automatically) and --quit-on-end (closes sumo on end of simulation) if this is unwanted behaviour
    match mapsize:
        case Mapsize.SMALL:
            traci.start([sumoBinary, "-c", "sumoFiles/small/small.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case Mapsize.MEDIUMSMALL:
            traci.start([sumoBinary, "-c", "sumoFiles/smallMedium/smallMedium.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case Mapsize.MEDIUM:
            traci.start([sumoBinary, "-c", "sumoFiles/medium/medium.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case _:
            return
    
# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    dataframeCompletionDuration = pd.DataFrame(columns=['name of dissemination case','number of bikes','duration','name of map','seed'])

    # looping through all the dissemination cases
    for seed in range(10,15):
        for vehAmount in range(2,10):
            for mapSize in Mapsize:
                for case in SimulationMode:
                    StartTraci(mapSize)
                    run(case, vehAmount, mapSize, seed)
                    
                    # dataframe = pd.concat([dataframeCompletionDuration, pd.DataFrame(completionData, columns=dataframeCompletionDuration.columns)], ignore_index=True)
                    dfer =pd.DataFrame(completionData, columns=dataframeCompletionDuration.columns)
                    dfer.to_csv('dataLog/completionTimeOptimized.csv')
    