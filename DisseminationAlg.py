#!/usr/bin/env python

import os
import sys
import optparse
import random
import pandas as pd
import json

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
def run(case, vehAmount, mapSize, seed, roadSegmentsFromJson):
    random.seed(seed)
    step = 0
    bikeObjectsInNetwork = {}
    roadEdgeValues = assignValuesToRoadEdges()
    roadEdgePositions = {}
    for edge in roadEdgeValues:
        roadEdgePositions[edge] = traci.lane.getShape(str(edge) + "_0")[0]
    distancesBetweenBikes = {}
    
    for roadSegmentFromJson in roadSegmentsFromJson:
        traci.gui.toggleSelection(roadSegmentFromJson, "edge")
    
    while traci.simulation.getMinExpectedNumber() > 0 and step < 5000:
        traci.simulationStep()
        
        traciActualBikesInNetwork = set(traci.vehicle.getIDList())
        
        # limit veh to vehamount
        if len(bikeObjectsInNetwork) >= vehAmount:
            # Wrong bikes are bikes that are not supposed to be in the networ
            removeWrongBikesFromNetwork(bikeObjectsInNetwork, traciActualBikesInNetwork)
        addingNewOrMissingBikesToNetwork(case, step, bikeObjectsInNetwork, roadEdgeValues, traciActualBikesInNetwork,random.randint(0,1000))
        
        ListOfTheBikeObjectsInNetwork = list(traciActualBikesInNetwork)
        bikeIndex = 0
        mostIndexed = ["0",-1] # [0] is the name of the bike [2] is the amount of roadsegments collected
        for nameOfBike in ListOfTheBikeObjectsInNetwork:
            bikeObject = bikeObjectsInNetwork[nameOfBike]
            bikePosition = traci.vehicle.getPosition(nameOfBike)
            roadSegmentBikeIsCurrentlyOn = traci.vehicle.getRoadID(nameOfBike)
            bikeObject.addRoad(roadSegmentBikeIsCurrentlyOn)
            
            if len(bikeObject.getRecievedRoads()) > mostIndexed[1]:
                mostIndexed = [nameOfBike, len(bikeObject.getRecievedRoads())]
            
            #update route
            if bikeObject.checkIfTarget(traci.vehicle.getRoadID(nameOfBike)):
                if nameOfBike == list(bikeObjectsInNetwork.keys())[0]:
                    setSegmentTarget(bikeObject, random.choice(roadSegmentsFromJson))
                else:
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
                        dataVeh = bikeObject.getDisseminationData(bikePosition, traci, roadEdgePositions)
                        dataVehOther = comparisonBikeObject.getDisseminationData(comparisonBikePosition, traci, roadEdgePositions)
                        comparisonBikeObject.recieveDesseminationData(dataVeh, nameOfBike)
                        bikeObject.recieveDesseminationData(dataVehOther, nameOfComparisonBike)
        step += 1
        
    collectiveKnowledgeOfRoadSegmentsInSubArea = {}
    for nameOfBike in bikeObjectsInNetwork:
            bikeObject = bikeObjectsInNetwork[nameOfBike]
            collectedRoads = bikeObject.getRoads()
            for roadSegmentFromBike in collectedRoads:
                if roadSegmentFromBike in roadSegmentsFromJson:
                    if roadSegmentFromBike not in collectiveKnowledgeOfRoadSegmentsInSubArea:
                        collectiveKnowledgeOfRoadSegmentsInSubArea[roadSegmentFromBike] = []
                    for originOfSegment in collectedRoads[roadSegmentFromBike]:
                        if originOfSegment not in collectiveKnowledgeOfRoadSegmentsInSubArea[roadSegmentFromBike]: 
                            collectiveKnowledgeOfRoadSegmentsInSubArea[roadSegmentFromBike].append(originOfSegment)
    collectiveKnowledgeAmountInSubarea = 0
    collectedAmoundByBikeInSubarea = 0
    for segment in collectiveKnowledgeOfRoadSegmentsInSubArea:
        if list(bikeObjectsInNetwork.keys())[0] in collectiveKnowledgeOfRoadSegmentsInSubArea[segment]:
            collectedAmoundByBikeInSubarea += 1
        collectiveKnowledgeAmountInSubarea += len(collectiveKnowledgeOfRoadSegmentsInSubArea[segment])
        
    percentageBelongingToBike = round(collectedAmoundByBikeInSubarea/collectiveKnowledgeAmountInSubarea*1000)/10
    completionData.append([str(case),vehAmount,str(mapSize),seed,collectiveKnowledgeAmountInSubarea, collectedAmoundByBikeInSubarea, percentageBelongingToBike, len(roadSegmentsFromJson), len(roadEdgeValues)])
    
    traci.close()
    sys.stdout.flush()

def addingNewOrMissingBikesToNetwork(case, step, bikeObjectsInNetwork, RoadEdgeValues, traciActualBikesInNetwork,seed):
    random.seed(seed)
    lostAndMissingBikesInNetwork = set(bikeObjectsInNetwork.keys()).symmetric_difference(traciActualBikesInNetwork)
    for bikeToBeAdded in lostAndMissingBikesInNetwork:
        if bikeToBeAdded not in bikeObjectsInNetwork.keys():
            bikeObjectsInNetwork[bikeToBeAdded] = BicycleClass(bikeToBeAdded, case)
        else:
            try:
                # Adding random Route to bike
                routeID = random.choice(list(RoadEdgeValues))
                routeName = str(step) + str(routeID)
                traci.route.add(routeName, [routeID])
                traci.vehicle.add(vehID=bikeToBeAdded,routeID=routeName, typeID="bicycle")
                setSegmentTarget(bikeObjectsInNetwork[bikeToBeAdded], random.choice(list(RoadEdgeValues)))
            except Exception as error:
                # it does sometimes happen that it doesnt work. But for simulation purposes does this not matter
                print("error adding will try again next step" + str(error))

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
    jsonFileForSubArea = None
    match mapsize:
        case Mapsize.SMALL:
            jsonFileForSubArea = open('sumoFiles/small/neighbourhood.json')
            traci.start([sumoBinary, "-c", "sumoFiles/small/small.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case Mapsize.SMALL2:
            jsonFileForSubArea = open('sumoFiles/small2/neighbourhood.json')
            traci.start([sumoBinary, "-c", "sumoFiles/small2/small2.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case Mapsize.MEDIUM:
            jsonFileForSubArea = open('sumoFiles/medium/neighbourhood.json')
            traci.start([sumoBinary, "-c", "sumoFiles/medium/medium.sumocfg",
                                        "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        # case Mapsize.LARGE:
        #     jsonFileForSubArea = open('sumoFiles/large/neighbourhood.json')
        #     traci.start([sumoBinary, "-c", "sumoFiles/large/large.sumocfg",
        #                                 "--tripinfo-output", "tripinfo.xml", "--start" ,"--quit-on-end"])
        case _:
            print("incorrect mapSize Given")
    return json.load(jsonFileForSubArea)
            
    
# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    dataframeCompletionDuration = pd.DataFrame(columns=['name of dissemination case','number of bikes','name of map','seed','collective data collection in area','collected by bike_','Percentage belonging to bike','size of subarea (# edges)','size of total map (# edges)'])

    # looping through all the dissemination cases
    # mapSize = Mapsize.SMALL
    bikeAmounts = [2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25]
    for seed in range(10,15):
        # for mapSize in Mapsize:
        mapSize = Mapsize.SMALL
        for vehAmount in bikeAmounts:
            # for case in SimulationMode:
            case = SimulationMode.Surrounding
            roadSegmentsFromJson = StartTraci(mapSize)
            run(case, vehAmount, mapSize, seed, roadSegmentsFromJson)
            dataForCompletion =pd.DataFrame(completionData, columns=dataframeCompletionDuration.columns)
            dataForCompletion.to_csv('dataLog/percentageSmallSurrounding.csv')
    