#---------  SWI prolog ------------#
from pyswip import *

#----------- GUI library  ---------#
import pygame
from guizero import App, ListBox, PushButton, Box, Text, info, Slider

#-------- Utils library  ---------#
import random
import numpy

from os import listdir
from os.path import isfile, join

import math

import json
import datetime
#-----------------------------------------#

from SLAMRobot import SLAMAgent
from modules.utils import Vertex, Gameobject, Agent, Room

#inizializzazione pygame
pygame.init()
pygame.display.set_caption("Environment Generator")

#Costanti tipi Gameobject
BEDROOM = "bedroom"
BATHROOM = "bathroom"
KITCHEN = "kitchen"
HALL = "hall"
BED = "bed"
BEDSIDE = "bedside"
WARDROBE = "wardrobe"
SINK = "sink"
SHOWER = "shower"
TOILET = "toilet"
TABLE = "table"
CHAIR = "chair"
DESK = "desk"
SOFA = "sofa"
HALL_TABLE = "hallTable"
CUPBOARD = "cupboard"
DOOR = "door"
FLOOR = "floor"
AGENT = "agent"
OBJECTIVE = "objective"

#Colori PyGame (mockup, verranno sostituite dalle sprite)
WHITE = (255, 255, 255)
BLUE = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED = (255,   0,   0)
ORANGE = (255,   200,   140)
BLACK = (  0,   0,  0)
PINK = (255, 210, 210)
BANANA = (255, 255, 150)
GREY = (150, 150, 150)
LIGHT_GREEN = (150, 255, 150)

class Environment():
    floor = Gameobject(0, 0, 0, 0, 0, FLOOR)
    agentStartX = 198 #per il reset quando muore
    agentStartY = 268 #per il reset quando muore
    agent = Agent(9999, 9999, 8, 8, 0, AGENT, 90)
    objectivePositions1 = [(160,240),(220,240),(230,280),(170, 320)]
    objectivePositions2 = [(270,190),(250,325),(110,290),(160,170)]
    objectivePositions3 = [(270,190),(250,325),(110,290),(160,170),(160,240),(220,240),(230,280),(170, 320)]
    objective = Gameobject(9800, 9800, 15, 15, 0, OBJECTIVE)
    isAgentLookingAtObjective = False
    spritesLoaded = False
    
    def __init__(self, envWidth, envHeight, multiplier, fakeCollisionMeter, doorFakeCollisionMeter):
        self.envWidth = envWidth * multiplier
        self.envHeight = envHeight * multiplier
        self.multiplier = multiplier
        self.prolog = Prolog()
        self.fakeCollisionMeter = fakeCollisionMeter
        self.doorFakeCollisionMeter = doorFakeCollisionMeter
        self.rooms = []

        prologQuery = "use_module(library(clpr))"

        for solution in self.prolog.query(prologQuery):
            print("CLPR loaded.")
    
    from modules.gui import testGuizero

    from modules.environment import displayEnvironment
    
    from modules.training import runTraining
    
    def isAgentColliding(self):
        isAgentInRoom = False
        for room in self.rooms:
            if not room.sprite.rect.contains(self.agent.sprite.rect):
                if self.agent.sprite.rect.colliderect(room.sprite.rect):
                    if room.door.width == 0:
                        if not (self.agent.sprite.rect.y >= room.door.sprite.rect.y and self.agent.sprite.rect.y+self.agent.sprite.rect.height <= room.door.sprite.rect.y+room.door.sprite.rect.height):
                            print("Collision in room with vertical door")
                            return True
                    else:
                        if not (self.agent.sprite.rect.x >= room.door.sprite.rect.x and self.agent.sprite.rect.x+self.agent.sprite.rect.width <= room.door.sprite.rect.x+room.door.sprite.rect.width):
                            print("Collision in room with orizontal door")
                            return True
            else:
                isAgentInRoom = True
                for roomChild in room.children:
                    if self.agent.sprite.rect.colliderect(roomChild.sprite.rect):
                        print("Collision with an object in the room")
                        return True
                    for child in roomChild.children:
                        if self.agent.sprite.rect.colliderect(child.sprite.rect):
                            print("Collision with an object in the room")
                            return True
        if not isAgentInRoom:
            if not self.floor.sprite.rect.contains(self.agent.sprite.rect):
                print("Collision with the floor")
                return True
        return False
    
    def resetAgent(self):
        self.agent.targetRot = 90
        self.agent.x = self.agentStartX
        self.agent.y = self.agentStartY
        self.agent.sprite.rect.x = self.agentStartX
        self.agent.sprite.rect.y = self.agentStartY
    def resetObjective(self):
        randomNextX = self.objective.sprite.rect.x
        randomNextY = self.objective.sprite.rect.y
        while randomNextX == self.objective.sprite.rect.x and randomNextY == self.objective.sprite.rect.y:
            randomNextPosition = self.objectivePositions3[random.randrange(0,len(self.objectivePositions3))]
            randomNextX = randomNextPosition[0]
            randomNextY = randomNextPosition[1]
        self.objective.sprite.rect.x = randomNextX
        self.objective.sprite.rect.y = randomNextY
    def projectSegments(self):
        #proiettiamo i angleRange/step segmenti dall'occhio del robot
        angleRange = 120
        step = 3
        eyePoint = self.agent.sprite.rect.center #punto di partenza dei segmenti
        # if self.agent.targetRot == 0:
            # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width, self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)
        # elif self.agent.targetRot == 90:
            # eyePoint = (self.agent.x + self.agent.width/2, self.agent.y)
        # elif self.agent.targetRot == 180:
            # eyePoint = (self.agent.sprite.rect.x, self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)
        # elif self.agent.targetRot == 270:
            # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width/2, self.agent.sprite.rect.y + self.agent.sprite.rect.height)
        # elif self.agent.targetRot == 45:
            # eyePoint = (self.agent.x + self.agent.width/2, self.agent.y)
        # elif self.agent.targetRot == 180:
            # eyePoint = (self.agent.sprite.rect.x, self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)
        # elif self.agent.targetRot == 270:
            # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width/2, self.agent.sprite.rect.y + self.agent.sprite.rect.height)
        # elif self.agent.targetRot == 270:
            # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width/2, self.agent.sprite.rect.y + self.agent.sprite.rect.height)
            
        slope = (self.agent.targetRot + angleRange/2) % 360
        points = []
        self.isAgentLookingAtObjective = False
        for i in range(0, angleRange, step):
            isAgentLookingAtObjective = False
            x = math.cos(math.radians(slope)) * 220
            y = math.sin(math.radians(slope)) * 220
            viewPoint = (eyePoint[0] + x, eyePoint[1] - y) #punto di fine del segmento i
            slope = (slope - step) % 360
            #collision check
            intersectionPoints = []
            intersectionPointsDistances = []
            for room in self.rooms:
                intersectionPoint = self.checkLineRoomCollision((eyePoint[0], eyePoint[1], viewPoint[0], viewPoint[1]), room)
                if intersectionPoint is not None:
                    intersectionPoints.append(intersectionPoint)
                for roomChild in room.children:
                    intersectionPoint = self.checkLineRectCollision((eyePoint[0], eyePoint[1], viewPoint[0], viewPoint[1]), roomChild.sprite.rect)
                    if intersectionPoint is not None:
                        intersectionPoints.append(intersectionPoint)
                    for child in roomChild.children:
                        intersectionPoint = self.checkLineRectCollision((eyePoint[0], eyePoint[1], viewPoint[0], viewPoint[1]), child.sprite.rect)
                        if intersectionPoint is not None:
                            intersectionPoints.append(intersectionPoint)
            intersectionPointFloor = self.checkLineRectCollision((eyePoint[0], eyePoint[1], viewPoint[0], viewPoint[1]), self.floor.sprite.rect)
            if intersectionPointFloor is not None:
                anyRoomContainsPoint = False
                for room in self.rooms:
                    if self.checkRectContainsPoint(room.sprite.rect, intersectionPointFloor):
                        anyRoomContainsPoint = True
                        break
                if not anyRoomContainsPoint:
                    intersectionPoints.append(intersectionPointFloor)
            intersectionPointObjective = self.checkLineRectCollision((eyePoint[0], eyePoint[1], viewPoint[0], viewPoint[1]), self.objective.sprite.rect)
            if intersectionPointObjective is not None:
                intersectionPoints.append(intersectionPointObjective)
            for point in intersectionPoints:
                intersectionPointsDistances.append(self.pointPointDistance(eyePoint, point))
            if len(intersectionPoints) > 0:
                chosenIndex = numpy.argmin(intersectionPointsDistances)
                chosenPoint = intersectionPoints[chosenIndex]
                if chosenPoint == intersectionPointObjective:
                    isAgentLookingAtObjective = True
                    self.isAgentLookingAtObjective = True
                points.append((slope / 359, intersectionPointsDistances[chosenIndex] / 220, isAgentLookingAtObjective))
            else:
                points.append((slope / 359, 1, False)) #il raggio non ha colpito nulla, torno una tupla con distanza massima
        return points
    
    def checkLineRectCollision(self, line, rect): #line è (x1,y1,x2,y2) e rect il rect di pygame
        intersectionPoints = []
        eyePoint = (line[0], line[1])
        point1 = self.checkLineLineCollision(line, (rect.x, rect.y, rect.x, rect.y+rect.height)) #lato ovest
        point2 = self.checkLineLineCollision(line, (rect.x, rect.y+rect.height, rect.x+rect.width, rect.y+rect.height)) #lato nord
        point3 = self.checkLineLineCollision(line, (rect.x+rect.width, rect.y+rect.height, rect.x+rect.width, rect.y)) #lato est
        point4 = self.checkLineLineCollision(line, (rect.x, rect.y, rect.x+rect.width, rect.y)) #lato sud
        if point1 is not None:
            intersectionPoints.append(point1)
        if point2 is not None:
            intersectionPoints.append(point2)
        if point3 is not None:
            intersectionPoints.append(point3)
        if point4 is not None:
            intersectionPoints.append(point4)
        intersectionPointsDistances = []
        for point in intersectionPoints:
            intersectionPointsDistances.append(self.pointPointDistance(eyePoint, point))
        if len(intersectionPoints) > 0:
            return intersectionPoints[numpy.argmin(intersectionPointsDistances)]
        else:
            return None
            
    def checkLineRoomCollision(self, line, room): #ho differenziato i metodi per evitare il calcolo relativo alla door a tutti i rect non room
        intersectionPoints = []
        eyePoint = (line[0], line[1])
        rect = room.sprite.rect
        point1 = self.checkLineLineCollision(line, (rect.x, rect.y, rect.x, rect.y+rect.height)) #lato ovest
        point2 = self.checkLineLineCollision(line, (rect.x, rect.y+rect.height, rect.x+rect.width, rect.y+rect.height)) #lato nord
        point3 = self.checkLineLineCollision(line, (rect.x+rect.width, rect.y+rect.height, rect.x+rect.width, rect.y)) #lato est
        point4 = self.checkLineLineCollision(line, (rect.x, rect.y, rect.x+rect.width, rect.y)) #lato sud
        if point1 is not None:
            if not room.door.sprite.rect.collidepoint(point1):
                intersectionPoints.append(point1)
        if point2 is not None:
            if not room.door.sprite.rect.collidepoint(point2):
                intersectionPoints.append(point2)
        if point3 is not None:
            if not room.door.sprite.rect.collidepoint(point3):
                intersectionPoints.append(point3)
        if point4 is not None:
            if not room.door.sprite.rect.collidepoint(point4):
                intersectionPoints.append(point4)
        intersectionPointsDistances = []
        for point in intersectionPoints:
            intersectionPointsDistances.append(self.pointPointDistance(eyePoint, point))
        if len(intersectionPoints) > 0:
            return intersectionPoints[numpy.argmin(intersectionPointsDistances)]
        else:
            return None

    
    def checkRectContainsPoint(self, rect, point):
        return point[0] >= rect.x and point[0] <= rect.x+rect.width and point[1] >= rect.y and point[1] <= rect.y+rect.height
        
    def pointPointDistance(self, point1, point2): #point1 è (x1,y1) -- point2 è (x2,y2)
        return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    
    def checkLineLineCollision(self, line1, line2): #line1 = (x1,y1,x2,y2) -- line2 = (x3,y3,x4,y4)
        x1 = line1[0]
        y1 = line1[1]
        x2 = line1[2]
        y2 = line1[3]
        x3 = line2[0]
        y3 = line2[1]
        x4 = line2[2]
        y4 = line2[3]
        try:
            uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        except ZeroDivisionError:
            uA = 2 #di modo che non collida; tanto se il denominatore tende a zero la frazione tende a +inf
        try:
            uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        except ZeroDivisionError:
            uB = 2 #di modo che non collida; tanto se il denominatore tende a zero la frazione tende a +inf
        if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1:
            return (int(x1 + (uA * (x2-x1))), int(y1 + (uA * (y2-y1))))
        else:
            return None
    def reset(self):
        self.envWidth = 15.0 * self.multiplier
        self.envHeight = 15.0 * self.multiplier
        self.floor = Gameobject(0, 0, 0, 0, 0, FLOOR)
        self.rooms = []

    def generateRoomsAndDoors(self, bathroomNumber, bedroomNumber, kitchenNumber, hallNumber):
        #Numero stanze totali
        roomNumber = bedroomNumber + kitchenNumber + bathroomNumber + hallNumber
        roomDistanceThreshold = 10.0 + 3 * roomNumber
        self.envWidth = self.envWidth + (8.0 * roomNumber * self.multiplier)
        self.envHeight = self.envHeight + (8.0 * roomNumber * self.multiplier)

        self.screen = pygame.display.set_mode((int(self.envWidth), int(self.envHeight)))
        #Carichiamo le sprite in memoria
        #---------------------------------------------------------------------
        self.HALL_IMAGE = pygame.image.load('textures/hall_texture.png').convert_alpha()
        self.KITCHEN_IMAGE = pygame.image.load('textures/kitchen_texture.png').convert_alpha()
        self.BEDROOM_IMAGE = pygame.image.load('textures/bedroom_texture.png').convert_alpha()
        self.BATHROOM_IMAGE = pygame.image.load('textures/bathroom_texture.png').convert_alpha()
        self.SOFA_IMAGE = pygame.image.load('textures/sofa_texture.png').convert_alpha()
        self.HALL_TABLE_IMAGE = pygame.image.load('textures/hall_table_texture.png').convert_alpha()
        self.TABLE_IMAGE = pygame.image.load('textures/table_texture.png').convert_alpha()
        self.CHAIR_IMAGE = pygame.image.load('textures/chair_texture.png').convert_alpha()
        self.DESK_IMAGE = pygame.image.load('textures/desk_texture.png').convert_alpha()
        self.BED_IMAGE = pygame.image.load('textures/green_bed_texture.png').convert_alpha()
        self.BEDSIDE_IMAGE = pygame.image.load('textures/bedside_texture.png').convert_alpha()
        self.WARDROBE_IMAGE = pygame.image.load('textures/wardrobe_texture.png').convert_alpha()
        self.TOILET_IMAGE = pygame.image.load('textures/toilet_texture.png').convert_alpha()
        self.SHOWER_IMAGE = pygame.image.load('textures/shower_texture.png').convert_alpha()
        self.SINK_IMAGE = pygame.image.load('textures/sink_texture.png').convert_alpha()
        self.DOOR_IMAGE = pygame.image.load('textures/door_texture.png').convert_alpha()
        self.FLOOR_IMAGE = pygame.image.load('textures/floor_texture.png').convert_alpha()
        self.AGENT_IMAGE = pygame.image.load('textures/agent_texture_mockup.png').convert_alpha()
        self.OBJECTIVE_IMAGE = pygame.image.load('textures/objective_texture_mockup.png').convert_alpha()
        #---------------------------------------------------------------------
        self.typeToSprite = {
            BEDROOM : self.BEDROOM_IMAGE,
            BATHROOM : self.BATHROOM_IMAGE,
            KITCHEN : self.KITCHEN_IMAGE,
            HALL : self.HALL_IMAGE,
            SOFA : self.SOFA_IMAGE,
            HALL_TABLE : self.HALL_TABLE_IMAGE,
            TABLE : self.TABLE_IMAGE,
            CHAIR: self.CHAIR_IMAGE,
            DESK: self.DESK_IMAGE,
            BED: self.BED_IMAGE,
            BEDSIDE : self.BEDSIDE_IMAGE,
            WARDROBE : self.WARDROBE_IMAGE,
            CUPBOARD : self.WARDROBE_IMAGE,
            TOILET : self.TOILET_IMAGE,
            SHOWER : self.SHOWER_IMAGE,
            SINK : self.SINK_IMAGE,
            DOOR : self.DOOR_IMAGE,
            FLOOR : self.FLOOR_IMAGE,
            AGENT: self.AGENT_IMAGE,
            OBJECTIVE: self.OBJECTIVE_IMAGE
        }
        
        #Inizializzazione rect e image dell'agente
        agentSprite = pygame.sprite.Sprite()
        agentSprite.image = pygame.transform.scale(self.typeToSprite[AGENT], (int(self.agent.width), int(self.agent.height)))
        agentSprite.rect = pygame.Rect(self.agent.x, self.agent.y, self.agent.width, self.agent.height)
        self.agent.sprite = agentSprite
        self.agent.image = self.agent.sprite.image
        
        #Inizializzazione rect e image dell'obiettivo
        objectiveSprite = pygame.sprite.Sprite()
        objectiveSprite.image = pygame.transform.scale(self.typeToSprite[OBJECTIVE], (int(self.objective.width), int(self.objective.height)))
        objectiveSprite.rect = pygame.Rect(self.objective.x, self.objective.y, self.objective.width, self.objective.height)
        self.objective.sprite = objectiveSprite
        
        headVariables = ""
        predicateHead = "generateEnvironment(EnvWidth, EnvHeight, "
        queryStart = "generateEnvironment("+str(self.envWidth)+", "+str(self.envHeight)+", "
        for i in range(0, roomNumber):
            headVariables += "R"+str(i)+"X"+", "
            headVariables += "R"+str(i)+"Y"+", "
            headVariables += "R"+str(i)+"W"+", "
            headVariables += "R"+str(i)+"H"+", "
        headVariables = headVariables[:-2]
        predicateHead = predicateHead + headVariables
        predicateHead += ") "
        query = queryStart + headVariables + ") "

        predicateBody = ":- repeat, "

        roomType = []

        for i in range(0, bedroomNumber):
            roomType.append(BEDROOM)
        for i in range(0, bathroomNumber):
            roomType.append(BATHROOM)
        for i in range(0, kitchenNumber):
            roomType.append(KITCHEN)
        for i in range(0, hallNumber):
            roomType.append(HALL)

        #generazione stanze (vuote)
        for i in range(0, roomNumber):
            if roomType[i] == BEDROOM:
                predicateBody += "random("+str(12.0*self.multiplier)+", "+str(17.0*self.multiplier)+", R"+str(i)+"W), "
                predicateBody += "random("+str(12.0*self.multiplier)+", "+str(17.0*self.multiplier)+", R"+str(i)+"H), "
                predicateBody += "WSUB"+str(i)+" is EnvWidth - R"+str(i)+"W, random(0.0, WSUB"+str(i)+", R"+str(i)+"X), "
                predicateBody += "HSUB"+str(i)+" is EnvHeight - R"+str(i)+"H, random(0.0, HSUB"+str(i)+", R"+str(i)+"Y), "
            if roomType[i] == BATHROOM:
                predicateBody += "random("+str(8.0*self.multiplier)+", "+str(12.0*self.multiplier)+", R"+str(i)+"W), "
                predicateBody += "random("+str(8.0*self.multiplier)+", "+str(12.0*self.multiplier)+", R"+str(i)+"H), "
                predicateBody += "WSUB"+str(i)+" is EnvWidth - R"+str(i)+"W, random(0.0, WSUB"+str(i)+", R"+str(i)+"X), "
                predicateBody += "HSUB"+str(i)+" is EnvHeight - R"+str(i)+"H, random(0.0, HSUB"+str(i)+", R"+str(i)+"Y), "
            if roomType[i] == KITCHEN:
                predicateBody += "random("+str(10.0*self.multiplier)+", "+str(15.0*self.multiplier)+", R"+str(i)+"W), "
                predicateBody += "random("+str(10.0*self.multiplier)+", "+str(15.0*self.multiplier)+", R"+str(i)+"H), "
                predicateBody += "WSUB"+str(i)+" is EnvWidth - R"+str(i)+"W, random(0.0, WSUB"+str(i)+", R"+str(i)+"X), "
                predicateBody += "HSUB"+str(i)+" is EnvHeight - R"+str(i)+"H, random(0.0, HSUB"+str(i)+", R"+str(i)+"Y), "
            if roomType[i] == HALL:
                predicateBody += "random("+str(15.0*self.multiplier)+", "+str(20.0*self.multiplier)+", R"+str(i)+"W), "
                predicateBody += "random("+str(15.0*self.multiplier)+", "+str(20.0*self.multiplier)+", R"+str(i)+"H), "
                predicateBody += "WSUB"+str(i)+" is EnvWidth - R"+str(i)+"W, random(0.0, WSUB"+str(i)+", R"+str(i)+"X), "
                predicateBody += "HSUB"+str(i)+" is EnvHeight - R"+str(i)+"H, random(0.0, HSUB"+str(i)+", R"+str(i)+"Y), "

        #collision detection
        for i in range(0, roomNumber):
            for j in range(i+1, roomNumber):
                predicateBody += "{(R"+str(i)+"X + R"+str(i)+"W + "+str(self.fakeCollisionMeter*self.multiplier)+" =< R"+str(j)+"X ; R"+str(j)+"X + R"+str(j)+"W + "+str(self.fakeCollisionMeter*self.multiplier)+" =< R"+str(i)+"X) ; (R"+str(i)+"Y + R"+str(i)+"H + "+str(self.fakeCollisionMeter*self.multiplier)+" =< R"+str(j)+"Y ; R"+str(j)+"Y + R"+str(j)+"H + "+str(self.fakeCollisionMeter*self.multiplier)+" =< R"+str(i)+"Y)}, "


        #distanza stanze generate dal centro "di massa"
        if(roomNumber > 1):
            predicateBody += "CentroX is ("
            for i in range(0, roomNumber):
                predicateBody += "R"+str(i)+"X + "
            predicateBody = predicateBody[:-3]
            predicateBody += ") / "+str(roomNumber)+", "
            predicateBody += "CentroY is ("
            for i in range(0, roomNumber):
                predicateBody += "R"+str(i)+"Y + "
            predicateBody = predicateBody[:-3]
            predicateBody += ") / "+str(roomNumber)+", "

            for i in range(0, roomNumber):
                predicateBody += "DistanzaRoom"+str(i)+" is "
                predicateBody += "sqrt(((R"+str(i)+"X + R"+str(i)+"W/2) - (CentroX))^2 + ((R"+str(i)+"Y + R"+str(i)+"H/2) - (CentroY))^2), "
                predicateBody += "{DistanzaRoom"+str(i)+" =< "+str(roomDistanceThreshold*self.multiplier)+"}, "


        predicateBody = predicateBody[:-2]
        predicateBody += ", !"

        # print("Il predicato per generare l'ambiente è:")
        print((predicateHead + predicateBody))
        # print("La query è: ")
        # print(query)
        self.prolog.assertz(predicateHead + predicateBody)

        prologQuery = query

        rooms = []

        for sol in self.prolog.query(prologQuery):
            # print("La soluzione alla generazione dell'ambiente è:")
            # print(sol)
            for i in range(0, roomNumber):

                roomSprite = pygame.sprite.Sprite()
                if roomType[i] == BATHROOM:
                    roomSprite.image = pygame.transform.scale(self.BATHROOM_IMAGE, (int(sol["R"+str(i)+"W"]), int(sol["R"+str(i)+"H"])))
                elif roomType[i] == KITCHEN:
                    roomSprite.image = pygame.transform.scale(self.KITCHEN_IMAGE, (int(sol["R"+str(i)+"W"]), int(sol["R"+str(i)+"H"])))
                elif roomType[i] == BEDROOM:
                    roomSprite.image = pygame.transform.scale(self.BEDROOM_IMAGE, (int(sol["R"+str(i)+"W"]), int(sol["R"+str(i)+"H"])))
                else:
                    roomSprite.image = pygame.transform.scale(self.HALL_IMAGE, (int(sol["R"+str(i)+"W"]), int(sol["R"+str(i)+"H"])))

                roomSprite.rect = pygame.Rect(sol["R"+str(i)+"X"], sol["R"+str(i)+"Y"], sol["R"+str(i)+"W"], sol["R"+str(i)+"H"])
                room = Room(sol["R"+str(i)+"X"], sol["R"+str(i)+"Y"], sol["R"+str(i)+"W"], sol["R"+str(i)+"H"], i, roomSprite, roomType[i])
                room.vertex1 = Vertex(room.x, room.y + room.height)
                room.vertex2 = Vertex(room.x + room.width, room.y + room.height)
                room.vertex3 = Vertex(room.x + room.width, room.y)
                room.vertex4 = Vertex(room.x, room.y)
                rooms.append(room)

        self.rooms = rooms
        self.prolog.retract(predicateHead + predicateBody)
        #Generazione baricentro delle stanze
        barycenterX = 0
        barycenterY = 0

        for room in self.rooms:
            barycenterX += room.x + room.width/2
            barycenterY += room.y + room.height/2

        barycenterX /= len(self.rooms)
        barycenterY /= len(self.rooms)

        self.barycenter = Vertex(barycenterX, barycenterY)

        #generazione floor (quadratone)
        vertexesXs = []
        vertexesYs = []

        for room in self.rooms:
            vertex1Distance = math.sqrt((room.vertex1.x - self.barycenter.x)**2 + (room.vertex1.y - self.barycenter.y)**2)
            vertex2Distance = math.sqrt((room.vertex2.x - self.barycenter.x)**2 + (room.vertex2.y - self.barycenter.y)**2)
            vertex3Distance = math.sqrt((room.vertex3.x - self.barycenter.x)**2 + (room.vertex3.y - self.barycenter.y)**2)
            vertex4Distance = math.sqrt((room.vertex4.x - self.barycenter.x)**2 + (room.vertex4.y - self.barycenter.y)**2)

            minDistance = min(vertex1Distance, vertex2Distance, vertex3Distance, vertex4Distance)

            if minDistance == vertex1Distance:
                vertexesXs.append(room.vertex1.x)
                vertexesYs.append(room.vertex1.y)
            elif minDistance == vertex2Distance:
                vertexesXs.append(room.vertex2.x)
                vertexesYs.append(room.vertex2.y)
            elif minDistance == vertex3Distance:
                vertexesXs.append(room.vertex3.x)
                vertexesYs.append(room.vertex3.y)
            else:
                vertexesXs.append(room.vertex4.x)
                vertexesYs.append(room.vertex4.y)

        spaceMultiplier = (random.random()*3 + 3)*self.multiplier
        floorSprite = pygame.sprite.Sprite()
        floorSprite.image = self.FLOOR_IMAGE
        floorSprite.image = pygame.transform.scale(floorSprite.image, (int(max(vertexesXs)-min(vertexesXs) + spaceMultiplier*2), int(max(vertexesYs)-min(vertexesYs) + spaceMultiplier*2)))
        floorSprite.rect = pygame.Rect(min(vertexesXs) - spaceMultiplier, min(vertexesYs) - spaceMultiplier, max(vertexesXs)-min(vertexesXs) + spaceMultiplier*2, max(vertexesYs)-min(vertexesYs) + spaceMultiplier*2)
        self.floor = Gameobject(min(vertexesXs) - spaceMultiplier, min(vertexesYs) - spaceMultiplier, max(vertexesXs)-min(vertexesXs) + spaceMultiplier*2, max(vertexesYs)-min(vertexesYs) + spaceMultiplier*2, floorSprite, FLOOR)

        for room in self.rooms:
            lato1 = (room.vertex1, room.vertex4)
            lato2 = (room.vertex1, room.vertex2)
            lato3 = (room.vertex2, room.vertex3)
            lato4 = (room.vertex3, room.vertex4)

            distanzaLato1 = math.sqrt((((lato1[0].x + lato1[1].x)/2) - self.barycenter.x)**2 + (((lato1[0].y + lato1[1].y)/2) - self.barycenter.y)**2)
            distanzaLato2 = math.sqrt((((lato2[0].x + lato2[1].x)/2) - self.barycenter.x)**2 + (((lato2[0].y + lato2[1].y)/2) - self.barycenter.y)**2)
            distanzaLato3 = math.sqrt((((lato3[0].x + lato3[1].x)/2) - self.barycenter.x)**2 + (((lato3[0].y + lato3[1].y)/2) - self.barycenter.y)**2)
            distanzaLato4 = math.sqrt((((lato4[0].x + lato4[1].x)/2) - self.barycenter.x)**2 + (((lato4[0].y + lato4[1].y)/2) - self.barycenter.y)**2)

            distanzaMinima = min(distanzaLato1, distanzaLato2, distanzaLato3, distanzaLato4)

            if distanzaMinima == distanzaLato1:
                constraintsSatisfied = False
                while not constraintsSatisfied:
                    doorY = random.random() * (room.height - 2.5*self.multiplier) + room.y
                    if doorY >= self.floor.y and doorY + 2.5*self.multiplier <= self.floor.y + self.floor.height:
                        constraintsSatisfied = True
                doorSprite = pygame.sprite.Sprite()
                doorSprite.image = self.DOOR_IMAGE
                doorSprite.image = pygame.transform.scale(doorSprite.image, (int(1.0*self.multiplier), int(2.5*self.multiplier)))
                #doorSprite.rect = pygame.Rect(room.x, doorY, 0.5*self.multiplier, 2.5*self.multiplier)
                room.door = Gameobject(room.x, doorY, 0, 2.5*self.multiplier, doorSprite, DOOR)
            elif distanzaMinima == distanzaLato2:
                constraintsSatisfied = False
                while not constraintsSatisfied:
                    doorX = random.random() * (room.width - 2.5*self.multiplier) + room.x
                    if doorX >= self.floor.x and doorX + 2.5*self.multiplier <= self.floor.x + self.floor.width:
                        constraintsSatisfied = True
                doorSprite = pygame.sprite.Sprite()
                doorSprite.image = self.DOOR_IMAGE
                doorSprite.image = pygame.transform.rotate(doorSprite.image, 90)
                doorSprite.image = pygame.transform.scale(doorSprite.image, (int(2.5*self.multiplier), int(1.0*self.multiplier)))
                #doorSprite.rect = pygame.Rect(doorX, room.y + room.height, 2.5*self.multiplier, 0.5*self.multiplier)
                room.door = Gameobject(doorX, room.y + room.height, 2.5*self.multiplier, 0, doorSprite, DOOR)
            elif distanzaMinima == distanzaLato3:
                constraintsSatisfied = False
                while not constraintsSatisfied:
                    doorY = random.random() * (room.height - 2.5*self.multiplier) + room.y
                    if doorY >= self.floor.y and doorY + 2.5*self.multiplier <= self.floor.y + self.floor.height:
                        constraintsSatisfied = True
                doorSprite = pygame.sprite.Sprite()
                doorSprite.image = self.DOOR_IMAGE
                doorSprite.image = pygame.transform.scale(doorSprite.image, (int(1.0*self.multiplier), int(2.5*self.multiplier)))
                #doorSprite.rect = pygame.Rect(room.x + room.width, doorY, 0.5*self.multiplier, 2.5*self.multiplier)
                room.door = Gameobject(room.x + room.width, doorY, 0, 2.5*self.multiplier, doorSprite, DOOR)
            else:
                constraintsSatisfied = False
                while not constraintsSatisfied:
                    doorX = random.random() * (room.width - 2.5*self.multiplier) + room.x
                    if doorX >= self.floor.x and doorX + 2.5*self.multiplier <= self.floor.x + self.floor.width:
                        constraintsSatisfied = True
                doorSprite = pygame.sprite.Sprite()
                doorSprite.image = self.DOOR_IMAGE
                doorSprite.image = pygame.transform.rotate(doorSprite.image, 90)
                doorSprite.image = pygame.transform.scale(doorSprite.image, (int(2.5*self.multiplier), int(1.0*self.multiplier)))
                #doorSprite.rect = pygame.Rect(doorX, room.y, 2.5*self.multiplier, 0.5*self.multiplier)
                room.door = Gameobject(doorX, room.y, 2.5*self.multiplier, 0, doorSprite, DOOR)

        return rooms

    def drawModel(self):
        if len(self.rooms) > 1:
            #Quadrato dell'area relativa ai corridoi
            self.screen.blit(self.floor.sprite.image, self.floor.sprite.rect)
            pygame.draw.rect(self.screen, WHITE, self.floor.sprite.rect, 2)

        for room in self.rooms:
            self.screen.blit(room.sprite.image, room.sprite.rect)
            pygame.draw.rect(self.screen, WHITE, room.sprite.rect, 2)
      
            if room.door.width == 0:
                blitRect = pygame.Rect(room.door.x - 0.5*self.multiplier, room.door.y, 1.0*self.multiplier, room.door.height)
                self.screen.blit(room.door.sprite.image, blitRect)
                room.door.sprite.rect = blitRect
            else:
                blitRect = pygame.Rect(room.door.x, room.door.y - 0.5*self.multiplier, room.door.width, 1.0*self.multiplier)
                self.screen.blit(room.door.sprite.image, blitRect)
                room.door.sprite.rect = blitRect
               
            for roomChild in room.children:
                self.screen.blit(roomChild.sprite.image, roomChild.sprite.rect)
                for child in roomChild.children:
                    self.screen.blit(child.sprite.image, child.sprite.rect)
        if self.agent.targetRot - self.agent.rot != 0:
            self.agent.image = pygame.transform.rotate(self.agent.sprite.image, self.agent.targetRot - 90)
            oldCenter = self.agent.sprite.rect.center
            self.agent.sprite.rect = self.agent.image.get_rect()
            self.agent.sprite.rect.center = oldCenter
            self.agent.rot = self.agent.targetRot
        self.agent.sprite.rect.x = self.agent.x
        self.agent.sprite.rect.y = self.agent.y
        self.screen.blit(self.agent.image, self.agent.sprite.rect)
        #pygame.draw.rect(self.screen, WHITE, self.agent.sprite.rect, 1)
        self.screen.blit(self.objective.sprite.image, self.objective.sprite.rect) 
        
    def loadModel(self, filePath):
        print(filePath)
        #Numero stanze totali
        with open("./environments/"+filePath, 'r') as infile:
            jsonString = infile.read()
        print(jsonString)
        deserializedEnvironmentDict = json.loads(jsonString)
        roomNumber = deserializedEnvironmentDict["roomNumber"]

        self.envWidth = self.envWidth + (8.5 * roomNumber * self.multiplier)
        self.envHeight = self.envHeight + (8.5 * roomNumber * self.multiplier)

        self.screen = pygame.display.set_mode((int(self.envWidth), int(self.envHeight)))

        if not self.spritesLoaded:
            #Carichiamo le sprite in memoria
            #---------------------------------------------------------------------
            self.HALL_IMAGE = pygame.image.load('textures/hall_texture.png').convert_alpha()
            self.KITCHEN_IMAGE = pygame.image.load('textures/kitchen_texture.png').convert_alpha()
            self.BEDROOM_IMAGE = pygame.image.load('textures/bedroom_texture.png').convert_alpha()
            self.BATHROOM_IMAGE = pygame.image.load('textures/bathroom_texture.png').convert_alpha()
            self.SOFA_IMAGE = pygame.image.load('textures/sofa_texture.png').convert_alpha()
            self.HALL_TABLE_IMAGE = pygame.image.load('textures/hall_table_texture.png').convert_alpha()
            self.TABLE_IMAGE = pygame.image.load('textures/table_texture.png').convert_alpha()
            self.CHAIR_IMAGE = pygame.image.load('textures/chair_texture.png').convert_alpha()
            self.DESK_IMAGE = pygame.image.load('textures/desk_texture.png').convert_alpha()
            self.BED_IMAGE = pygame.image.load('textures/green_bed_texture.png').convert_alpha()
            self.BEDSIDE_IMAGE = pygame.image.load('textures/bedside_texture.png').convert_alpha()
            self.WARDROBE_IMAGE = pygame.image.load('textures/wardrobe_texture.png').convert_alpha()
            self.TOILET_IMAGE = pygame.image.load('textures/toilet_texture.png').convert_alpha()
            self.SHOWER_IMAGE = pygame.image.load('textures/shower_texture.png').convert_alpha()
            self.SINK_IMAGE = pygame.image.load('textures/sink_texture.png').convert_alpha()
            self.DOOR_IMAGE = pygame.image.load('textures/door_texture.png').convert_alpha()
            self.FLOOR_IMAGE = pygame.image.load('textures/floor_texture.png').convert_alpha()
            self.AGENT_IMAGE = pygame.image.load('textures/agent_texture_mockup.png').convert_alpha()
            self.OBJECTIVE_IMAGE = pygame.image.load('textures/objective_texture_mockup.png').convert_alpha()
            #---------------------------------------------------------------------
            self.typeToSprite = {
                BEDROOM : self.BEDROOM_IMAGE,
                BATHROOM : self.BATHROOM_IMAGE,
                KITCHEN : self.KITCHEN_IMAGE,
                HALL : self.HALL_IMAGE,
                SOFA : self.SOFA_IMAGE,
                HALL_TABLE : self.HALL_TABLE_IMAGE,
                TABLE : self.TABLE_IMAGE,
                CHAIR: self.CHAIR_IMAGE,
                DESK: self.DESK_IMAGE,
                BED: self.BED_IMAGE,
                BEDSIDE : self.BEDSIDE_IMAGE,
                WARDROBE : self.WARDROBE_IMAGE,
                CUPBOARD : self.WARDROBE_IMAGE,
                TOILET : self.TOILET_IMAGE,
                SHOWER : self.SHOWER_IMAGE,
                SINK : self.SINK_IMAGE,
                DOOR : self.DOOR_IMAGE,
                FLOOR : self.FLOOR_IMAGE,
                AGENT : self.AGENT_IMAGE,
                OBJECTIVE : self.OBJECTIVE_IMAGE
            }
            self.spritesLoaded = True

        floorDict = deserializedEnvironmentDict["floor"]
        floorSprite = pygame.sprite.Sprite()
        floorSprite.image = pygame.transform.scale(self.FLOOR_IMAGE, (int(floorDict["width"]), int(floorDict["height"])))
        floorSprite.rect = pygame.Rect(floorDict["x"], floorDict["y"], floorDict["width"], floorDict["height"])
        self.floor = Gameobject(floorDict["x"], floorDict["y"], floorDict["width"], floorDict["height"], floorSprite,
                                FLOOR)
        for i in range(0, roomNumber):
            roomDict = deserializedEnvironmentDict["R"+str(i)]
            roomSprite = pygame.sprite.Sprite()
            roomSprite.image = pygame.transform.scale(self.typeToSprite[roomDict["type"]], (int(roomDict["width"]), int(roomDict["height"])))
            roomSprite.rect = pygame.Rect(roomDict["x"], roomDict["y"], roomDict["width"], roomDict["height"])
            deserializedRoom = Room(roomDict["x"], roomDict["y"], roomDict["width"], roomDict["height"], i, roomSprite, roomDict["type"])
            doorDict = roomDict["door"]
            doorSprite = pygame.sprite.Sprite()
            if doorDict["width"] != 0:
                doorSprite.image = pygame.transform.scale(pygame.transform.rotate(self.DOOR_IMAGE, 90), (int(2.5*self.multiplier), int(1.0*self.multiplier)))
            else:
                doorSprite.image = pygame.transform.scale(self.DOOR_IMAGE, (int(1.0*self.multiplier), int(2.5*self.multiplier)))
            doorSprite.rect = pygame.Rect(doorDict["x"], doorDict["y"], doorDict["width"], doorDict["height"])
            deserializedRoom.door = Gameobject(doorDict["x"], doorDict["y"], doorDict["width"], doorDict["height"], doorSprite,
                                               DOOR)
            for childDict in roomDict["children"]:
                childRotation = 0
                if childDict["orientation"] == "W":
                    childRotation = -90
                elif childDict["orientation"] == "N":
                    childRotation = 180
                elif childDict["orientation"] == "E":
                    childRotation = 90
                childSprite = pygame.sprite.Sprite()
                childSprite.image = pygame.transform.scale(pygame.transform.rotate(self.typeToSprite[childDict["type"]], childRotation), (int(childDict["width"]), int(childDict["height"])))
                childSprite.rect = pygame.Rect(childDict["x"], childDict["y"], childDict["width"], childDict["height"])
                deserializedChild = Gameobject(childDict["x"], childDict["y"], childDict["width"], childDict["height"], childSprite, childDict["type"])
                deserializedRoom.children.append(deserializedChild)
                for childchildDict in childDict["children"]:
                    childchildRotation = 0
                    if childchildDict["orientation"] == "W":
                        childchildRotation = -90
                    elif childchildDict["orientation"] == "N":
                        childchildRotation = 180
                    elif childchildDict["orientation"] == "E":
                        childchildRotation = 90
                    childchildSprite = pygame.sprite.Sprite()
                    childchildSprite.image = pygame.transform.scale(pygame.transform.rotate(self.typeToSprite[childchildDict["type"]], childchildRotation), (int(childchildDict["width"]), int(childchildDict["height"])))
                    childchildSprite.rect = pygame.Rect(childchildDict["x"], childchildDict["y"], childchildDict["width"], childchildDict["height"])
                    deserializedChildChild = Gameobject(childchildDict["x"], childchildDict["y"], childchildDict["width"], childchildDict["height"], childchildSprite, childchildDict["type"])
                    deserializedChild.children.append(deserializedChildChild)
            self.rooms.append(deserializedRoom)
        #Inizializzazione rect e image dell'agente
        agentSprite = pygame.sprite.Sprite()
        agentSprite.image = pygame.transform.scale(self.typeToSprite[AGENT], (int(self.agent.width), int(self.agent.height)))
        agentSprite.rect = pygame.Rect(self.agent.x, self.agent.y, self.agent.width, self.agent.height)
        self.agent.sprite = agentSprite
        self.agent.image = self.agent.sprite.image
        
        #Inizializzazione rect e image dell'obiettivo
        objectiveSprite = pygame.sprite.Sprite()
        objectiveSprite.image = pygame.transform.scale(self.typeToSprite[OBJECTIVE], (int(self.objective.width), int(self.objective.height)))
        objectiveSprite.rect = pygame.Rect(self.objective.x, self.objective.y, self.objective.width, self.objective.height)
        self.objective.sprite = objectiveSprite
    
    def saveGeneratedModel(self):
        serializedFloor = {
            "x" : self.floor.x,
            "y" : self.floor.y,
            "width" : self.floor.width,
            "height" : self.floor.height
        }

        serializedEnvironment = {
            "roomNumber" : len(self.rooms),
            "floor" : serializedFloor
        }

        for room in self.rooms:
            serializedRoom = {
                "x" : room.x,
                "y" : room.y,
                "width" : room.width,
                "height" : room.height,
                "type" : room.type,
                "children" : [],
                "door" : {
                    "x" : room.door.x,
                    "y" : room.door.y,
                    "width" : room.door.width,
                    "height" : room.door.height,
                }
            }
            for child in room.children:
                serializedChild = {
                    "x" : child.x,
                    "y" : child.y,
                    "width" : child.width,
                    "height" : child.height,
                    "type" : child.type,
                    "orientation" : child.orientation,
                    "children" : []
                }
                for childchild in child.children:
                    serializedChildChild = {
                    "x" : childchild.x,
                    "y" : childchild.y,
                    "width" : childchild.width,
                    "height" : childchild.height,
                    "type" : childchild.type,
                    "orientation" : childchild.orientation
                }
                    serializedChild["children"].append(serializedChildChild)
                serializedRoom["children"].append(serializedChild)

            serializedEnvironment["R"+str(room.index)] = serializedRoom

        toSave = json.dumps(serializedEnvironment)
        #codice per scrivere su disco il contenuto di toSave
        with open('./environments/environment '+str(str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+" "+str(datetime.datetime.now().hour)+"-"+str(datetime.datetime.now().minute)+"-"+str(datetime.datetime.now().second))+".json", 'w') as outfile:
            json.dump(serializedEnvironment, outfile)

    from modules.bathroom import populateBathroom, getBathrooms    
    from modules.bedroom import populateBedroom, getBedrooms
    from modules.kitchen import populateKitchen, getKitchens
    from modules.hall import populateHall, getHalls

    
    def generateEnvironment(self, bathroomNumber, bedroomNumber, kitchenNumber, hallNumber):
        self.generateRoomsAndDoors(bathroomNumber, bedroomNumber, kitchenNumber, hallNumber)
        for bathroom in self.getBathrooms():
            self.populateBathroom(bathroom, random.randint(0,1), random.randint(0,1), random.randint(0,1))
        for bedroom in self.getBedrooms():
            self.populateBedroom(bedroom, random.randint(0,2), random.randint(0,2))
        for kitchen in self.getKitchens():
            self.populateKitchen(kitchen, random.randint(0,3), random.randint(0,1))
        for hall in self.getHalls():
            self.populateHall(hall, random.randint(0,1), random.randint(0,2), random.randint(0,2), 1.0)

environment = Environment(15.0, 15.0, 8.5, 2.5, 1.5)
environment.testGuizero()

