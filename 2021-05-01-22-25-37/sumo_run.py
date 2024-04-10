import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd

def getdatetime():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    currentDT = utc_now.astimezone(pytz.timezone("Asia/Singapore"))
    DATIME = currentDT.strftime("%Y-%m-%d %H:%M:%S")
    return DATIME

def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

sumoCmd = ["sumo", "-c", r"C:\\Users\\Jeffy Shiju\\Desktop\\ROJECT\\sumo-example\\2021-05-01-22-25-37\\2024-04-10-21-56-55\\osm.sumocfg" ]
traci.start(sumoCmd)

packVehicleData = []
packTLSData = []
packBigData = []

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()
    trafficlights = traci.trafficlight.getIDList()

    for i in range(0, len(vehicles)):
        vehid = vehicles[i]
        x, y = traci.vehicle.getPosition(vehicles[i])
        coord = [x, y]
        lon, lat = traci.simulation.convertGeo(x, y)
        gpscoord = [lon, lat]
        spd = round(traci.vehicle.getSpeed(vehicles[i]) * 3.6, 2)
        edge = traci.vehicle.getRoadID(vehicles[i])
        lane = traci.vehicle.getLaneID(vehicles[i])
        displacement = round(traci.vehicle.getDistance(vehicles[i]), 2)
        turnAngle = round(traci.vehicle.getAngle(vehicles[i]), 2)
        nextTLS = traci.vehicle.getNextTLS(vehicles[i])

        vehList = [getdatetime(), vehid, coord, gpscoord, spd, edge, lane, displacement, turnAngle, nextTLS]

        print("Vehicle: ", vehicles[i], " at datetime: ", getdatetime())
        print(vehicles[i], " >>> Position: ", coord, " | GPS Position: ", gpscoord, " |", \
              " Speed: ", round(traci.vehicle.getSpeed(vehicles[i]) * 3.6, 2), "km/h |", \
              " EdgeID of veh: ", traci.vehicle.getRoadID(vehicles[i]), " |", \
              " LaneID of veh: ", traci.vehicle.getLaneID(vehicles[i]), " |", \
              " Distance: ", round(traci.vehicle.getDistance(vehicles[i]), 2), "m |", \
              " Vehicle orientation: ", round(traci.vehicle.getAngle(vehicles[i]), 2), "deg |", \
              " Upcoming traffic lights: ", traci.vehicle.getNextTLS(vehicles[i]))

        idd = traci.vehicle.getLaneID(vehicles[i])
        tlsList = []

        for k in range(0, len(trafficlights)):
            if idd in traci.trafficlight.getControlledLanes(trafficlights[k]):
                tflight = trafficlights[k]
                tl_state = traci.trafficlight.getRedYellowGreenState(trafficlights[k])
                tl_phase_duration = traci.trafficlight.getPhaseDuration(trafficlights[k])
                tl_lanes_controlled = traci.trafficlight.getControlledLanes(trafficlights[k])
                tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficlights[k])
                tl_next_switch = traci.trafficlight.getNextSwitch(trafficlights[k])

                tlsList = [tflight, tl_state, tl_phase_duration, tl_lanes_controlled, tl_program, tl_next_switch]

                print(trafficlights[k], " --->",
                      " TL state: ", traci.trafficlight.getRedYellowGreenState(trafficlights[k]), " |",
                      " TLS phase duration: ", traci.trafficlight.getPhaseDuration(trafficlights[k]), " |",
                      " Lanes controlled: ", traci.trafficlight.getControlledLanes(trafficlights[k]), " |",
                      " TLS Program: ", traci.trafficlight.getCompleteRedYellowGreenDefinition(trafficlights[k]), " |"
                      " Next TLS switch: ", traci.trafficlight.getNextSwitch(trafficlights[k]))

        packBigDataLine = flatten_list([vehList, tlsList])
        packBigData.append(packBigDataLine)

traci.close()

columnnames = ['dateandtime', 'vehid', 'coord', 'gpscoord', 'spd', 'edge', 'lane', 'displacement', 'turnAngle', 'nextTLS', \
               'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset = pd.DataFrame(packBigData, index=None, columns=columnnames)
dataset.to_excel("output.xlsx", index=False)
time.sleep(5)