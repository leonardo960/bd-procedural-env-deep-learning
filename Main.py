from pyswip import *
import pygame
from guizero import App, ListBox, PushButton, Box, Text, info, Slider
import random
from os import listdir
from os.path import isfile, join
import math
import json
import datetime
from SLAMRobot import SLAMAgent
import numpy

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

class Vertex():
    def __init__(self, x , y):
        self.x = x
        self.y = y

class Gameobject():
    #orientation può valere N, E, W, S
    orientation = ""
    def __init__(self, x, y, width, height, sprite, type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = sprite
        self.children = []
        self.type = type

class Agent(Gameobject):
    def __init__(self, x, y, width, height, sprite, type, rot):
        Gameobject.__init__(self, x, y, width, height, sprite, type)
        self.rot = rot
        self.targetRot = rot #serve per calcolare di quanto roteare (e.g. targetRot - rot = gradi di rotazione)
        self.image = 0

class Room(Gameobject):
    vertex1 = Vertex(0, 0)
    vertex2 = Vertex(0, 0)
    vertex3 = Vertex(0, 0)
    vertex4 = Vertex(0, 0)
    door = Gameobject(0, 0, 0, 0, 0, DOOR)

    def __init__(self, x, y, width, height, index, sprite, type):
        Gameobject.__init__(self, x, y, width, height, sprite, type)
        self.index = index

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

    def testGuizero(self):
        app = App(title="Tesi Addestramento Robot 2019", width = 600, height = 600)

        menuBox = Box(app, layout="grid", width=600, height=250)
        def goToVistaAmbienti_cmd():
            menuBox.hide()
            vistaAmbientiBox.show()
        def goToVistaGenerazione_cmd():
            menuBox.hide()
            vistaGenerazioneAmbientiBox.show()
            generazioneAmbientiBox1.show()
            generazioneAmbientiBox2.show()
            generazioneAmbientiButtonBox.show()
        def goToAddestraAgente_cmd():
            menuBox.hide()
            vistaAddestramentoBox.show()
            
        Box(menuBox, height=50, width=600, grid=[0,0])
        Box(menuBox, height=20, grid=[0,2])
        Box(menuBox, height=20, grid=[0,4])
        PushButton(menuBox, command=goToVistaAmbienti_cmd, text="Visualizza ambienti generati", width=18, height=1, grid=[0, 1])
        PushButton(menuBox, command=goToVistaGenerazione_cmd, text="Genera nuovi ambienti", width=18, height=1, grid=[0, 3])
        PushButton(menuBox, command=goToAddestraAgente_cmd, text="Addestra Agente", width=18, height=1, grid=[0, 5])

        vistaAmbientiBox = Box(app, visible=False, layout="grid")
        envFiles = [f for f in listdir("./environments") if isfile(join("./environments", f))]
        listbox = ListBox(vistaAmbientiBox, items = envFiles, scrollbar = True, width = 350, height = 350, grid=[0,1])
        def visualizza_cmd():
            self.loadModel(listbox.value)
            self.drawModel()
            self.displayEnvironment()
        def vistaAmbientiBack_cmd():
            vistaAmbientiBox.hide()
            menuBox.show()
        Box(vistaAmbientiBox, height=40, grid=[0,0])
        visualizzaButtonBox = Box(vistaAmbientiBox, layout="grid", grid=[0,2])
        PushButton(visualizzaButtonBox, command=visualizza_cmd, text = "Visualizza", grid=[0,0])
        PushButton(visualizzaButtonBox, command=vistaAmbientiBack_cmd, text="Indietro", grid=[1,0])

        vistaGenerazioneAmbientiBox = Box(app, visible=False, layout="grid")
        generazioneAmbientiBox1 = Box(vistaGenerazioneAmbientiBox, visible=False, layout="grid", grid=[0, 1])
        generazioneAmbientiBox2 = Box(vistaGenerazioneAmbientiBox, visible=False, layout="grid", grid=[1, 1])
        generazioneAmbientiButtonBox = Box(vistaGenerazioneAmbientiBox, visible=False, layout="grid", grid=[0,3])

        def vistaGenerazioneAmbientiBack_cmd():
            vistaGenerazioneAmbientiBox.hide()
            generazioneAmbientiBox1.hide()
            generazioneAmbientiBox2.hide()
            generazioneAmbientiButtonBox.hide()
            menuBox.show()
        def generate_cmd():
            info("Utilizzare il Generatore", "- Durante la generazione ambienti, premere il tasto \n'S' per salvare un ambiente e generare il successivo.\n\n- Premere il tasto 'N' per generare un nuovo ambiente\n scartando quello precedente.\n\n- Chiudere PyGame per tornare al menu.")
            #avvia generazione ambienti
            self.generateEnvironment(self.sliderBAR.value, self.sliderBR.value, self.sliderKI.value, self.sliderHA.value)
            self.drawModel()
            self.displayEnvironment(mode="generate")

        Box(vistaGenerazioneAmbientiBox, height=40, grid=[0,0])

        Text(generazioneAmbientiBox1, text="Numero camere da letto:", grid=[0,0], size=10, bg=LIGHT_GREEN)
        self.sliderBR = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,0])
        self.sliderBR.__setattr__("bg", LIGHT_GREEN)

        Text(generazioneAmbientiBox2, text="MAX letti:", grid=[0,0], size=10, bg=LIGHT_GREEN)
        self.sliderBR_B = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,0])
        Text(generazioneAmbientiBox2, text="MAX armadi:", grid=[0,1], size=10, bg=LIGHT_GREEN)
        self.sliderBR_W = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,1])

        Box(generazioneAmbientiBox1, height=40, grid=[0,1])

        Text(generazioneAmbientiBox1, text="Numero bagni:", grid=[0,2], size=10, bg=PINK)
        self.sliderBAR = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,2])
        self.sliderBAR.__setattr__("bg", PINK)

        Text(generazioneAmbientiBox2, text="MAX water:", grid=[0,2], size=10, bg=PINK)
        self.sliderBAR_T = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,2])
        Text(generazioneAmbientiBox2, text="MAX docce:", grid=[0,3], size=10, bg=PINK)
        self.sliderBAR_S = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,3])
        Text(generazioneAmbientiBox2, text="MAX lavandini:", grid=[0,4], size=10, bg=PINK)
        self.sliderBAR_SI = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,4])

        Box(generazioneAmbientiBox1, height=40, grid=[0,3])

        Text(generazioneAmbientiBox1, text="Numero cucine:", grid=[0,4], size=10, bg=BANANA)
        self.sliderKI = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,4])
        self.sliderKI.__setattr__("bg", BANANA)

        Text(generazioneAmbientiBox2, text="MAX tavoli:", grid=[0,5], size=10, bg=BANANA)
        self.sliderKI_KTA = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,5])
        Text(generazioneAmbientiBox2, text="MAX banconi:", grid=[0,6], size=10, bg=BANANA)
        self.sliderKI_D = Slider(generazioneAmbientiBox2, horizontal=True, end=3, grid=[1,6])

        Box(generazioneAmbientiBox1, height=40, grid=[0,5])

        Text(generazioneAmbientiBox1, text="Numero saloni:", grid=[0,6], size=10, bg=ORANGE)
        self.sliderHA = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,6])
        self.sliderHA.__setattr__("bg", ORANGE)

        Text(generazioneAmbientiBox2, text="MAX tavoli:", grid=[0,7], size=10, bg=ORANGE)
        self.sliderHA_HT = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,7])
        Text(generazioneAmbientiBox2, text="MAX divani:", grid=[0,8], size=10, bg=ORANGE)
        self.sliderHA_SO = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,8])
        Text(generazioneAmbientiBox2, text="MAX scaffali:", grid=[0,9], size=10, bg=ORANGE)
        self.sliderHA_CB = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,9])

        Box(vistaGenerazioneAmbientiBox, height=40, grid=[0,2])

        PushButton(generazioneAmbientiButtonBox, command=generate_cmd, text = "Genera Ambienti", grid=[0,0])
        PushButton(generazioneAmbientiButtonBox, command=vistaGenerazioneAmbientiBack_cmd, text = "Indietro", grid=[1,0])

        vistaAddestramentoBox = Box(app, visible=False, layout="grid")
        envFiles = [f for f in listdir("./environments") if isfile(join("./environments", f))]
        listbox2 = ListBox(vistaAddestramentoBox, items = envFiles, scrollbar = True, width = 350, height = 350, grid=[0,1])
        def addestra_cmd():
            self.loadModel(listbox2.value)
            self.runTraining()
        def vistaAddestramentoBack_cmd():
            vistaAddestramentoBox.hide()
            menuBox.show()
        Box(vistaAddestramentoBox, height=40, grid=[0,0])
        visualizzaButtonBox2 = Box(vistaAddestramentoBox, layout="grid", grid=[0,2])
        PushButton(visualizzaButtonBox2, command=addestra_cmd, text = "Addestra", grid=[0,0])
        PushButton(visualizzaButtonBox2, command=vistaAddestramentoBack_cmd, text="Indietro", grid=[1,0])
        
        app.display()

    def displayEnvironment(self, mode="view"):
        running = True
        clock = pygame.time.Clock()
        pygame.init()
        pygame.display.set_caption("Environment Generator")
        frames = 1500
        score = 0
        while running:
            self.screen.fill((30,30,30))
            self.drawModel()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    self.reset()
            if not running:
                break        
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_s] and mode == "generate":
                self.saveGeneratedModel()
                self.reset()
                self.generateEnvironment(self.sliderBAR.value, self.sliderBR.value, self.sliderKI.value, self.sliderHA.value)
                self.drawModel()
            if pressed[pygame.K_n] and mode == "generate":
                self.reset()
                self.generateEnvironment(self.sliderBAR.value, self.sliderBR.value, self.sliderKI.value, self.sliderHA.value)
                self.drawModel()
            if pressed[pygame.K_UP] and pressed[pygame.K_RIGHT]:
                self.agent.targetRot = 45
                self.agent.x += 2
                self.agent.y -= 2
            elif pressed[pygame.K_UP] and pressed[pygame.K_LEFT]:
                self.agent.targetRot = 135
                self.agent.x -= 2
                self.agent.y -= 2
            elif pressed[pygame.K_DOWN] and pressed[pygame.K_RIGHT]:
                self.agent.targetRot = 315
                self.agent.x += 2
                self.agent.y += 2
            elif pressed[pygame.K_DOWN] and pressed[pygame.K_LEFT]:
                self.agent.targetRot = 225
                self.agent.x -= 2
                self.agent.y += 2
            elif pressed[pygame.K_UP]:
                self.agent.targetRot = 90
                self.agent.y -= 2
            elif pressed[pygame.K_DOWN]:
                self.agent.targetRot = 270
                self.agent.y += 2
            elif pressed[pygame.K_LEFT]:
                self.agent.targetRot = 180
                self.agent.x -= 2
            elif pressed[pygame.K_RIGHT]:
                self.agent.targetRot = 0
                self.agent.x += 2
            
            elif pressed[pygame.K_SPACE]:
                #proiettiamo i 120 segmenti dall'occhio del robot
                angleRange = 120
                step = 3
                eyePoint = self.agent.sprite.rect.center
                # if self.agent.targetRot == 0:
                    # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width, self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)
                    # pygame.draw.circle(self.screen, (255,0,0), (self.agent.sprite.rect.x + self.agent.sprite.rect.width, int(self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)), 2)
                # elif self.agent.targetRot == 90:
                    # eyePoint = (self.agent.x + self.agent.width/2, self.agent.y)
                    # pygame.draw.circle(self.screen, (255,0,0), (int(self.agent.x + self.agent.width/2), self.agent.y), 2)
                # elif self.agent.targetRot == 180:
                    # eyePoint = (self.agent.sprite.rect.x, self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)
                    # pygame.draw.circle(self.screen, (255,0,0), (self.agent.sprite.rect.x, int(self.agent.sprite.rect.y + self.agent.sprite.rect.height/2)), 2)
                # elif self.agent.targetRot == 270:
                    # eyePoint = (self.agent.sprite.rect.x + self.agent.sprite.rect.width/2, self.agent.sprite.rect.y + self.agent.sprite.rect.height)
                    # pygame.draw.circle(self.screen, (255,0,0), (int(self.agent.sprite.rect.x + self.agent.sprite.rect.width/2), self.agent.sprite.rect.y + self.agent.sprite.rect.height), 2)
                slope = (self.agent.targetRot + angleRange/2) % 360
                testDistances = []
                for i in range(0, angleRange, step):
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
                        testDistances.append(min(intersectionPointsDistances)/220)
                        chosenIndex = numpy.argmin(intersectionPointsDistances)
                        chosenPoint = intersectionPoints[chosenIndex]
                        if i/step >= 10 and i/step <= 30:
                            pygame.draw.circle(self.screen, (255,0,0), chosenPoint, 2)
                if min(testDistances) < 0.049:
                    print("attivazione avoidance")
            if self.agent.sprite.rect.colliderect(self.objective.sprite.rect):
                self.resetObjective()
                score += 1
            pygame.display.update()
            clock.tick(100)
            frames -= 1
            if frames == 0:
                running = False
                print("punteggio ottenuto: " + str(score))
        pygame.quit()    
    def runTraining(self):
        state_size = 40
        slamAgent = SLAMAgent(state_size, 3)
        #slamAgent.load("test", 0.19) 
        speed = 2
        frames = 1500
        for i in range(1,10001): #10k episodi
            self.screen = pygame.display.set_mode((int(self.envWidth), int(self.envHeight)))
            #pygame.init()
            #self.reset()
            #self.generateEnvironment(2, 2, 2, 2)
            #self.drawModel()
            #pygame.display.set_caption("Agent Training Episode {}/{}".format(i,10000))
            done = False
            frameCount = 0
            self.resetAgent()
            self.resetObjective()
            state = numpy.reshape(self.projectSegments(), [1,state_size,3])
            lastDistFromSpawn = 0
            randomActions = 0
            
            score = 0

            
            while not done:
                #renderOn = (i-1) % 100 == 0 #renderizzo un episodio ogni 100
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:
                            slamAgent.save("test")
                renderOn = True
                if renderOn:
                    frameCount += 1
                    if frameCount == frames: #episodi lunghi massimo 10 secondi 
                        done = True
                    self.screen.fill((30,30,30))
                    action, wasItRandom = slamAgent.act(state)
                    if wasItRandom:
                        randomActions += 1
                    if action == 0: #LOOK RIGHT
                        self.agent.targetRot = (self.agent.targetRot + 45) % 360
                    elif action == 1: #LOOK LEFT
                        self.agent.targetRot = (self.agent.targetRot - 45) % 360
                    elif action == 2: #GO FORWARD
                        if self.agent.targetRot == 90:
                            self.agent.y -= speed
                        elif self.agent.targetRot == 270:
                            self.agent.y += speed
                        elif self.agent.targetRot == 180:
                            self.agent.x -= speed
                        elif self.agent.targetRot == 0:
                            self.agent.x += speed
                        elif self.agent.targetRot == 45:
                            self.agent.y -= speed
                            self.agent.x += speed
                        elif self.agent.targetRot == 135:
                            self.agent.x -= speed
                            self.agent.y -= speed
                        elif self.agent.targetRot == 225:
                            self.agent.x -= speed
                            self.agent.y += speed
                        elif self.agent.targetRot == 315:
                            self.agent.x += speed
                            self.agent.y += speed
                    self.drawModel()
                    pygame.display.update()
                    if self.isAgentColliding():
                        currentMinDistance = state[0][0][1]
                        print("len(state[0]): " + str(len(state[0])))
                        for k in range(len(state[0])):
                            if state[0][k][1] < currentMinDistance and not state[0][k][2]:
                                print("state[0][k][1]: " + str(state[0][k][1]))
                                currentMinDistance = state[0][k][1]
                        print("currentMinDistance: " + str(currentMinDistance))
                        print("distanze: " + str(state))
                        done = True                      
                    currentDistFromSpawn = self.pointPointDistance((self.agent.sprite.rect.x, self.agent.sprite.rect.y), (self.agentStartX, self.agentStartY))
                    
                    if  currentDistFromSpawn > lastDistFromSpawn:
                        lastDistFromSpawn = currentDistFromSpawn
                        wasDistFromSpawnUpdated = 1
                    else:
                        wasDistFromSpawnUpdated = 0
                    
                    #assegno reward
                    reward = 0
                    if self.agent.sprite.rect.colliderect(self.objective.sprite.rect): #spostato da isAgentColliding per cambiare reward
                        self.resetObjective()
                        reward += 1
                    next_state = numpy.reshape(self.projectSegments(), [1,state_size,3])
                    #reward += wasDistFromSpawnUpdated
                    score += reward
                    
                    slamAgent.remember(state, action, reward, next_state, done)
                    state = next_state
                else:
                    frameCount += 1
                    if frameCount == 600: #episodi lunghi massimo 10 secondi 
                        done = True
                    reward = 0
                    action = slamAgent.act(state)
                    if action == 0: #UP
                        self.agent.targetRot = 90
                        self.agent.y -= 2
                    elif action == 1: #DOWN
                        self.agent.targetRot = 270
                        self.agent.y += 2
                    elif action == 2: #LEFT
                        self.agent.targetRot = 180
                        self.agent.x -= 2
                    elif action == 3: #RIGHT
                        self.agent.targetRot = 0
                        self.agent.x += 2
                    if self.isAgentColliding():
                        done = True
                    #sta sopravvivendo, 1 punto di reward
                    reward += 1
                    next_state = numpy.reshape(self.projectSegments(), [1,state_size,2])
                    if self.isAgentLookingAtObjective:
                        reward += 3
                        newDistToObjective = self.pointPointDistance((self.agent.x, self.agent.y), (self.objective.x, self.objective.y))
                        if newDistToObjective < distToObjective:
                            distToObjective = newDistToObjective
                            reward += 5
                    slamAgent.remember(state, action, reward, next_state, done)
                    state = next_state
                    if done:
                        break
            print("Episodio {}/{}: fine al frame {}/{}, score: {}, random: {}%".format(i,10000,frameCount,frames, score, int((randomActions * 100)/frameCount)))
            print("Inizio replay agente.")
            slamAgent.replay(500)
            print("Replay agente completato.")
        print("Salvataggio pesi...")
        slamAgent.save("test")
        print("Salvataggio pesi completato.")
        pygame.quit()
            
    def isAgentColliding(self):
        isAgentInRoom = False
        for room in self.rooms:
            if not room.sprite.rect.contains(self.agent.sprite.rect):
                if self.agent.sprite.rect.colliderect(room.sprite.rect):
                    if room.door.width == 0:
                        if not (self.agent.sprite.rect.y >= room.door.sprite.rect.y and self.agent.sprite.rect.y+self.agent.sprite.rect.height <= room.door.sprite.rect.y+room.door.sprite.rect.height):
                            print("Collisione con stanza con porta verticale")
                            return True
                    else:
                        if not (self.agent.sprite.rect.x >= room.door.sprite.rect.x and self.agent.sprite.rect.x+self.agent.sprite.rect.width <= room.door.sprite.rect.x+room.door.sprite.rect.width):
                            print("Collisione con stanza con porta orizzontale")
                            return True
            else:
                isAgentInRoom = True
                for roomChild in room.children:
                    if self.agent.sprite.rect.colliderect(roomChild.sprite.rect):
                        print("Collisione a causa di un oggetto della stanza")
                        return True
                    for child in roomChild.children:
                        if self.agent.sprite.rect.colliderect(child.sprite.rect):
                            print("Collisione a causa di un oggetto di un oggetto")
                            return True
        if not isAgentInRoom:
            if not self.floor.sprite.rect.contains(self.agent.sprite.rect):
                print("Collisione con il floor")
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
        print(predicateHead + predicateBody)
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

    def populateBathroom(self, bathroom, toiletNumber, showerNumber, sinkNumber):
        headVariables = ""
        predicateHead = "generateBathroom"+str(bathroom.index)+"(ZeroX, ZeroY, RoomWidth, RoomHeight, "
        query = "generateBathroom"+str(bathroom.index)+"("+str(bathroom.x)+", "+str(bathroom.y)+", "+str(bathroom.width)+", "+str(bathroom.height)+", "
        for i in range(0, toiletNumber):
            headVariables += "T"+str(i)+"X"+", "
            headVariables += "T"+str(i)+"Y"+", "
            headVariables += "T"+str(i)+"W"+", "
            headVariables += "T"+str(i)+"H"+", "

            query += "T"+str(i)+"X"+", "
            query += "T"+str(i)+"Y"+", "
            query += "T"+str(i)+"W"+", "
            query += "T"+str(i)+"H"+", "
        for i in range(0, showerNumber):
            headVariables += "S"+str(i)+"X"+", "
            headVariables += "S"+str(i)+"Y"+", "
            headVariables += "S"+str(i)+"W"+", "
            headVariables += "S"+str(i)+"H"+", "

            query += "S"+str(i)+"X"+", "
            query += "S"+str(i)+"Y"+", "
            query += "S"+str(i)+"W"+", "
            query += "S"+str(i)+"H"+", "
        for i in range(0, sinkNumber):
            headVariables += "SI"+str(i)+"X"+", "
            headVariables += "SI"+str(i)+"Y"+", "
            headVariables += "SI"+str(i)+"W"+", "
            headVariables += "SI"+str(i)+"H"+", "

            query += "SI"+str(i)+"X"+", "
            query += "SI"+str(i)+"Y"+", "
            query += "SI"+str(i)+"W"+", "
            query += "SI"+str(i)+"H"+", "

        predicateHead = predicateHead + headVariables
        predicateHead = predicateHead[:-2]
        predicateHead += ") "

        query = query[:-2]
        query += ")"

        predicateBody = ":- repeat, "

        # generazione delle Toilet -----------------------------------------------------------------------
        predicateBody += "Rwidthbound is RoomWidth + ZeroX, Rheightbound is RoomHeight + ZeroY, "
        # -- constraints di X ed Y delle Toilet
        for i in range(0, toiletNumber):
            predicateBody += "{T"+str(i)+"X + T"+str(i)+"W =< Rwidthbound, T"+str(i)+"Y + T"+str(i)+"H =< Rheightbound}, "
        # --

        toiletInfo = []
        for i in range(0, toiletNumber):
            toiletInfo.append((random.randint(1, 4))) #(toiletSideInRoom -> determina toiletOrientation)
        for i in range(0, toiletNumber):
            if toiletInfo[i] == 1:
                predicateBody += "random("+str(1.0*self.multiplier)+", "+str(1.3*self.multiplier)+", T"+str(i)+"H" + "), "
                predicateBody += "{T"+str(i)+"X = ZeroX, T"+str(i)+"W = T"+str(i)+"H + "+str(0.7*self.multiplier)+"}, THSUB"+str(i)+" is Rheightbound - T"+str(i)+"H, random(ZeroY, THSUB"+str(i)+", T"+str(i)+"Y"+"), "
            elif toiletInfo[i] == 2:
                predicateBody += "random("+str(1.0*self.multiplier)+", "+str(1.3*self.multiplier)+", T"+str(i)+"W" + "), "
                predicateBody += "{T"+str(i)+"Y + T"+str(i)+"H = Rheightbound, T"+str(i)+"H = T"+str(i)+"W + "+str(0.7*self.multiplier)+"}, TWSUB"+str(i)+" is Rwidthbound - T"+str(i)+"W, random(ZeroX, TWSUB"+str(i)+", T"+str(i)+"X"+"), "
            elif toiletInfo[i] == 3:
                predicateBody += "random("+str(1.0*self.multiplier)+", "+str(1.3*self.multiplier)+", T"+str(i)+"H" + "), "
                predicateBody += "{T"+str(i)+"X + T"+str(i)+"W = Rwidthbound, T"+str(i)+"W = T"+str(i)+"H + "+str(0.7*self.multiplier)+"}, THSUB"+str(i)+" is Rheightbound - T"+str(i)+"H, random(ZeroY, THSUB"+str(i)+", T"+str(i)+"Y"+"), "
            elif toiletInfo[i] == 4:
                predicateBody += "random("+str(1.0*self.multiplier)+", "+str(1.3*self.multiplier)+", T"+str(i)+"W" + "), "
                predicateBody += "{T"+str(i)+"Y = ZeroY, T"+str(i)+"H = T"+str(i)+"W + "+str(0.7*self.multiplier)+"}, TWSUB"+str(i)+" is Rwidthbound - T"+str(i)+"W, random(ZeroX, TWSUB"+str(i)+", T"+str(i)+"X"+"), "

        showerInfo = [] #lato a cui è attaccato
        for i in range(0, showerNumber):
            showerInfo.append(random.randint(1,4))
        for i in range(0, showerNumber):
            if showerInfo[i] == 1:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(4.0*self.multiplier)+", S"+str(i)+"W), S"+str(i)+"H = S"+str(i)+"W, S"+str(i)+"X = ZeroX, SHSUB"+str(i)+" is Rheightbound - S"+str(i)+"H, random(ZeroY, SHSUB"+str(i)+", S"+str(i)+"Y), "
            if showerInfo[i] == 2:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(4.0*self.multiplier)+", S"+str(i)+"W), S"+str(i)+"H = S"+str(i)+"W, S"+str(i)+"Y is Rheightbound - S"+str(i)+"H, SWSUB"+str(i)+" is Rwidthbound - S"+str(i)+"W, random(ZeroX, SWSUB"+str(i)+", S"+str(i)+"X), "
            if showerInfo[i] == 3:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(4.0*self.multiplier)+", S"+str(i)+"W), S"+str(i)+"H = S"+str(i)+"W, S"+str(i)+"X is Rwidthbound - S"+str(i)+"W, SHSUB"+str(i)+" is Rheightbound - S"+str(i)+"H, random(ZeroY, SHSUB"+str(i)+", S"+str(i)+"Y), "
            if showerInfo[i] == 4:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(4.0*self.multiplier)+", S"+str(i)+"W), S"+str(i)+"H = S"+str(i)+"W, S"+str(i)+"Y = ZeroY, SWSUB"+str(i)+" is Rwidthbound - S"+str(i)+"W, random(ZeroX, SWSUB"+str(i)+", S"+str(i)+"X), "


        sinkInfo = []
        for i in range(0, sinkNumber):
            sinkInfo.append((random.randint(1, 4))) #(sinkSideInRoom -> determina sinkOrientation)
        for i in range(0, sinkNumber):
            if sinkInfo[i] == 1:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.5*self.multiplier)+", SI"+str(i)+"H" + "), "
                predicateBody += "{SI"+str(i)+"X = ZeroX, SI"+str(i)+"W = SI"+str(i)+"H * (2/3)}, SIHSUB"+str(i)+" is Rheightbound - SI"+str(i)+"H, random(ZeroY, SIHSUB"+str(i)+", SI"+str(i)+"Y"+"), "
            elif sinkInfo[i] == 2:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.5*self.multiplier)+", SI"+str(i)+"W" + "), "
                predicateBody += "{SI"+str(i)+"Y + SI"+str(i)+"H = Rheightbound, SI"+str(i)+"H = SI"+str(i)+"W * (2/3)}, SIWSUB"+str(i)+" is Rwidthbound - SI"+str(i)+"W, random(ZeroX, SIWSUB"+str(i)+", SI"+str(i)+"X"+"), "
            elif sinkInfo[i] == 3:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.5*self.multiplier)+", SI"+str(i)+"H" + "), "
                predicateBody += "{SI"+str(i)+"X + SI"+str(i)+"W = Rwidthbound, SI"+str(i)+"W = SI"+str(i)+"H * (2/3)}, SIHSUB"+str(i)+" is Rheightbound - SI"+str(i)+"H, random(ZeroY, SIHSUB"+str(i)+", SI"+str(i)+"Y"+"), "
            elif sinkInfo[i] == 4:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.5*self.multiplier)+", SI"+str(i)+"W" + "), "
                predicateBody += "{SI"+str(i)+"Y = ZeroY, SI"+str(i)+"H = SI"+str(i)+"W * (2/3)}, SIWSUB"+str(i)+" is Rwidthbound - SI"+str(i)+"W, random(ZeroX, SIWSUB"+str(i)+", SI"+str(i)+"X"+"), "

        #collisioni oggetti bagno
        #per ora evitiamo di inserire constraint relativi alla collisioni di oggetti dello stesso tipo
        #in quanto presenti sempre 1 in quantità (1 doccia, 1 lavandino, 1 toilet)
        # for i in range(0, bedNumber):
        #     for j in range(i+1, bedNumber):
        #         predicateBody += "{(B"+str(i)+"X + B"+str(i)+"W =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< B"+str(i)+"X) ; (B"+str(i)+"Y + B"+str(i)+"H =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< B"+str(i)+"Y)}, "

        # -- Shower x Toilet --
        for j in range(0, showerNumber):
            for i in range(0, toiletNumber):
                predicateBody += "{(T"+str(i)+"X + T"+str(i)+"W =< S"+str(j)+"X ; S"+str(j)+"X + S"+str(j)+"W =< T"+str(i)+"X) ; (T"+str(i)+"Y + T"+str(i)+"H =< S"+str(j)+"Y ; S"+str(j)+"Y + S"+str(j)+"H =< T"+str(i)+"Y)}, "

        # -- Shower x Door --
        for j in range(0, showerNumber):
            if bathroom.door.width == 0:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< S"+str(j)+"X ; S"+str(j)+"X + S"+str(j)+"W =< "+str(bathroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bathroom.door.y + bathroom.door.height)+" =< S"+str(j)+"Y ; S"+str(j)+"Y + S"+str(j)+"H =< "+str(bathroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width)+" =< S"+str(j)+"X ; S"+str(j)+"X + S"+str(j)+"W =< "+str(bathroom.door.x)+") ; ("+str(bathroom.door.y + bathroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< S"+str(j)+"Y ; S"+str(j)+"Y + S"+str(j)+"H =< "+str(bathroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Shower x Sink --
        for j in range(0, showerNumber):
            for i in range(0, sinkNumber):
                predicateBody += "{(SI"+str(i)+"X + SI"+str(i)+"W =< S"+str(j)+"X ; S"+str(j)+"X + S"+str(j)+"W =< SI"+str(i)+"X) ; (SI"+str(i)+"Y + SI"+str(i)+"H =< S"+str(j)+"Y ; S"+str(j)+"Y + S"+str(j)+"H =< SI"+str(i)+"Y)}, "

        # -- Sink x Door --
        for j in range(0, sinkNumber):
            if bathroom.door.width == 0:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< SI"+str(j)+"X ; SI"+str(j)+"X + SI"+str(j)+"W =< "+str(bathroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bathroom.door.y + bathroom.door.height)+" =< SI"+str(j)+"Y ; SI"+str(j)+"Y + SI"+str(j)+"H =< "+str(bathroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width)+" =< SI"+str(j)+"X ; SI"+str(j)+"X + SI"+str(j)+"W =< "+str(bathroom.door.x)+") ; ("+str(bathroom.door.y + bathroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< SI"+str(j)+"Y ; SI"+str(j)+"Y + SI"+str(j)+"H =< "+str(bathroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "


        # -- Sink x Toilet --
        for j in range(0, sinkNumber):
            for i in range(0, toiletNumber):
                predicateBody += "{(T"+str(i)+"X + T"+str(i)+"W =< SI"+str(j)+"X ; SI"+str(j)+"X + SI"+str(j)+"W =< T"+str(i)+"X) ; (T"+str(i)+"Y + T"+str(i)+"H =< SI"+str(j)+"Y ; SI"+str(j)+"Y + SI"+str(j)+"H =< T"+str(i)+"Y)}, "

        # -- Toilet x Door --
        for j in range(0, toiletNumber):
            if bathroom.door.width == 0:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< T"+str(j)+"X ; T"+str(j)+"X + T"+str(j)+"W =< "+str(bathroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bathroom.door.y + bathroom.door.height)+" =< T"+str(j)+"Y ; T"+str(j)+"Y + T"+str(j)+"H =< "+str(bathroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bathroom.door.x + bathroom.door.width)+" =< T"+str(j)+"X ; T"+str(j)+"X + T"+str(j)+"W =< "+str(bathroom.door.x)+") ; ("+str(bathroom.door.y + bathroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< T"+str(j)+"Y ; T"+str(j)+"Y + T"+str(j)+"H =< "+str(bathroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "



        predicateBody = predicateBody[:-2]
        predicateBody += ", !"
        # no il punto . dopo il predicato

        print("Il predicato per generare il bagno è: ")
        print(predicateHead + predicateBody)
        self.prolog.assertz(predicateHead + predicateBody)

        for sol in self.prolog.query(query):
            for i in range(0, toiletNumber):
                toiletSprite = pygame.sprite.Sprite()
                toiletSprite.image = self.TOILET_IMAGE
                spriteOrientation = "S"
                if toiletInfo[i] == 1:
                    toiletSprite.image = pygame.transform.rotate(toiletSprite.image, 90)
                    spriteOrientation = "E"
                elif toiletInfo[i] == 3:
                    toiletSprite.image = pygame.transform.rotate(toiletSprite.image, -90)
                    spriteOrientation = "W"
                elif toiletInfo[i] == 4:
                    toiletSprite.image = pygame.transform.rotate(toiletSprite.image, 180)
                    spriteOrientation = "N"
                toiletSprite.image = pygame.transform.scale(toiletSprite.image, (int(sol["T"+str(i)+"W"]), int(sol["T"+str(i)+"H"])))
                toiletSprite.rect = pygame.Rect(sol["T"+str(i)+"X"], sol["T"+str(i)+"Y"], sol["T"+str(i)+"W"], sol["T"+str(i)+"H"])
                toilet = Gameobject(sol["T"+str(i)+"X"], sol["T"+str(i)+"Y"], sol["T"+str(i)+"W"], sol["T"+str(i)+"H"], toiletSprite, TOILET)
                toilet.orientation = spriteOrientation
                bathroom.children.append(toilet)
            for i in range(0, showerNumber):
                showerSprite = pygame.sprite.Sprite()
                showerSprite.image = self.SHOWER_IMAGE
                spriteOrientation = "S"
                if showerInfo[i] == 1:
                    showerSprite.image = pygame.transform.rotate(showerSprite.image, 90)
                    spriteOrientation = "E"
                elif showerInfo[i] == 3:
                    showerSprite.image = pygame.transform.rotate(showerSprite.image, -90)
                    spriteOrientation = "W"
                elif showerInfo[i] == 4:
                    showerSprite.image = pygame.transform.rotate(showerSprite.image, 180)
                    spriteOrientation = "N"
                showerSprite.image = pygame.transform.scale(showerSprite.image, (int(sol["S"+str(i)+"W"]), int(sol["S"+str(i)+"H"])))
                showerSprite.rect = pygame.Rect(sol["S"+str(i)+"X"], sol["S"+str(i)+"Y"], sol["S"+str(i)+"W"], sol["S"+str(i)+"H"])
                shower = Gameobject(sol["S"+str(i)+"X"], sol["S"+str(i)+"Y"], sol["S"+str(i)+"W"], sol["S"+str(i)+"H"], showerSprite, SHOWER)
                shower.orientation = spriteOrientation
                bathroom.children.append(shower)
            for i in range(0, sinkNumber):
                sinkSprite = pygame.sprite.Sprite()
                sinkSprite.image = self.SINK_IMAGE
                spriteOrientation = "S"
                if sinkInfo[i] == 1:
                    sinkSprite.image = pygame.transform.rotate(sinkSprite.image, 90)
                    spriteOrientation = "E"
                elif sinkInfo[i] == 3:
                    sinkSprite.image = pygame.transform.rotate(sinkSprite.image, -90)
                    spriteOrientation = "W"
                elif sinkInfo[i] == 2:
                    sinkSprite.image = pygame.transform.rotate(sinkSprite.image, 180)
                    spriteOrientation = "N"
                sinkSprite.image = pygame.transform.scale(sinkSprite.image, (int(sol["SI"+str(i)+"W"]), int(sol["SI"+str(i)+"H"])))
                sinkSprite.rect = pygame.Rect(sol["SI"+str(i)+"X"], sol["SI"+str(i)+"Y"], sol["SI"+str(i)+"W"], sol["SI"+str(i)+"H"])
                sink = Gameobject(sol["SI"+str(i)+"X"], sol["SI"+str(i)+"Y"], sol["SI"+str(i)+"W"], sol["SI"+str(i)+"H"], sinkSprite, SINK)
                sink.orientation = spriteOrientation
                bathroom.children.append(sink)
        self.prolog.retract(predicateHead + predicateBody)

    def getBathrooms(self):
        result = []
        for bathroom in (x for x in self.rooms if x.type == BATHROOM):
            result.append(bathroom)
        return result

    def populateBedroom(self, bedroom, bedNumber, wardrobeNumber):

        headVariables = ""
        predicateHead = "generateBedroom"+str(bedroom.index)+"(ZeroX, ZeroY, RoomWidth, RoomHeight, "
        query = "generateBedroom"+str(bedroom.index)+"("+str(bedroom.x)+", "+str(bedroom.y)+", "+str(bedroom.width)+", "+str(bedroom.height)+", "
        for i in range(0, bedNumber):
            headVariables += "B"+str(i)+"X"+", "
            headVariables += "B"+str(i)+"Y"+", "
            headVariables += "B"+str(i)+"W"+", "
            headVariables += "B"+str(i)+"H"+", "

            query += "B"+str(i)+"X"+", "
            query += "B"+str(i)+"Y"+", "
            query += "B"+str(i)+"W"+", "
            query += "B"+str(i)+"H"+", "

        for i in range(0, bedNumber):
            headVariables += "BS"+str(i)+"X"+", "
            headVariables += "BS"+str(i)+"Y"+", "
            headVariables += "BS"+str(i)+"W"+", "
            headVariables += "BS"+str(i)+"H"+", "

            query += "BS"+str(i)+"X"+", "
            query += "BS"+str(i)+"Y"+", "
            query += "BS"+str(i)+"W"+", "
            query += "BS"+str(i)+"H"+", "

        for i in range(0, wardrobeNumber):
            headVariables += "W"+str(i)+"X"+", "
            headVariables += "W"+str(i)+"Y"+", "
            headVariables += "W"+str(i)+"W"+", "
            headVariables += "W"+str(i)+"H"+", "

            query += "W"+str(i)+"X"+", "
            query += "W"+str(i)+"Y"+", "
            query += "W"+str(i)+"W"+", "
            query += "W"+str(i)+"H"+", "

        predicateHead = predicateHead + headVariables
        predicateHead = predicateHead[:-2]
        predicateHead += ") "

        query = query[:-2]
        query += ")"

        predicateBody = ":- repeat, "

        # generazione dei Letti -----------------------------------------------------------------------
        predicateBody += "Rwidthbound is RoomWidth + ZeroX, Rheightbound is RoomHeight + ZeroY, "
        # -- constraints di X ed Y di Letti e Comò
        for i in range(0, bedNumber):
            predicateBody += "{B"+str(i)+"X + B"+str(i)+"W =< Rwidthbound, B"+str(i)+"Y + B"+str(i)+"H =< Rheightbound}, "
            predicateBody += "{BS"+str(i)+"X >= ZeroX, BS"+str(i)+"Y >= ZeroY, BS"+str(i)+"X + BS"+str(i)+"W =< Rwidthbound, BS"+str(i)+"Y + BS"+str(i)+"H =< Rheightbound}, "
        # --

        bedInfo = []
        wardrobeInfo = []


        while True:

            for i in range(0, bedNumber):
                bedInfo.append((random.randint(0, 1), random.randint(1, 4))) #(bedOrientation, bedSideInRoom)
            for i in range(0, wardrobeNumber):
                wardrobeInfo.append((random.randint(1, 4))) #(wardrobeSideInRoom -> determina wardrobeOrientation)

            side1Sum = 0
            side2Sum = 0
            side3Sum = 0
            side4Sum = 0

            #sommiamo il valore medio dei range per ampliare il range delle soluzioni
            #intese come combinazione di orientamento e grandezza nel contesto di un lato
            for bedTuple in bedInfo:
                if bedTuple[1] == 1:
                    if bedTuple[0] == 0:
                        side1Sum += 3.0 #bed
                        side1Sum += 2.0 #bedside
                    else:
                        side1Sum += 6.0 #bed
                        side1Sum += 2.0 #bedside
                if bedTuple[1] == 2:
                    if bedTuple[0] == 0:
                        side2Sum += 6.0 #bed
                        side2Sum += 2.0 #bedside
                    else:
                        side2Sum += 3.0 #bed
                        side2Sum += 2.0 #bedside
                if bedTuple[1] == 3:
                    if bedTuple[0] == 0:
                        side3Sum += 3.0 #bed
                        side3Sum += 2.0 #bedside
                    else:
                        side3Sum += 6.0 #bed
                        side3Sum += 2.0 #bedside
                if bedTuple[1] == 4:
                    if bedTuple[0] == 0:
                        side4Sum += 6.0 #bed
                        side4Sum += 2.0#bedside
                    else:
                        side4Sum += 3.0 #bed
                        side4Sum += 2.0 #bedside
            for wardrobeSide in wardrobeInfo:
                if wardrobeSide == 1:
                    side1Sum += 7.5
                if wardrobeSide == 2:
                    side2Sum += 7.5
                if wardrobeSide == 3:
                    side3Sum += 7.5
                if wardrobeSide == 4:
                    side4Sum += 7.5

            side1Sum *= self.multiplier
            side2Sum *= self.multiplier
            side3Sum *= self.multiplier
            side4Sum *= self.multiplier

            #calcoliamo lo spazio delle due parti in cui un lato è diviso dalla porta
            #e se è almeno uno dei due è sufficiente per posizionare il resto
            #del contenuto giacente sul lato allora l'assegnamento randomico
            #lato-contenuto è soddisfacente
            if bedroom.door.x == bedroom.x and bedroom.door.width == 0:
                side1Top = (bedroom.y + bedroom.height) - (bedroom.door.y + bedroom.door.height)
                side1Bot = bedroom.door.y - bedroom.y
                if (side1Sum <= side1Top or side1Sum <= side1Bot) and side2Sum <= bedroom.height and side3Sum <= bedroom.width and side4Sum <= bedroom.height:
                    break
            if bedroom.door.x == bedroom.x + bedroom.width and bedroom.door.width == 0:
                side3Top = (bedroom.y + bedroom.height) - (bedroom.door.y + bedroom.door.height)
                side3Bot = bedroom.door.y - bedroom.y
                if side1Sum <= bedroom.width and side2Sum <= bedroom.height and (side3Sum <= side3Top or side3Sum <= side3Bot) and side4Sum <= bedroom.height:
                    break
            if bedroom.door.y == bedroom.y + bedroom.height and bedroom.door.height == 0:
                side2Left = bedroom.door.x - bedroom.x
                side2Right = (bedroom.x + bedroom.width) - (bedroom.door.x + bedroom.door.width)
                if side1Sum <= bedroom.width and (side2Sum <= side2Left or side2Sum <= side2Right) and side3Sum <= bedroom.width and side4Sum <= bedroom.height:
                    break
            else:
                side4Left = bedroom.door.x - bedroom.x
                side4Right = (bedroom.x + bedroom.width) - (bedroom.door.x + bedroom.door.width)
                if side1Sum <= bedroom.width and side2Sum <= bedroom.height and side3Sum <= bedroom.width and (side4Sum <= side4Left or side4Sum <= side4Right):
                    break

            bedInfo = []
            wardrobeInfo = []

        for i in range(0, bedNumber):
            if bedInfo[i][0] == 1:
                predicateBody += "random("+str(2.0*self.multiplier)+", "+str(3.0*self.multiplier)+", B"+str(i)+"W" + "), "
                predicateBody += "{B"+str(i)+"H = B"+str(i)+"W + "+str(3.0*self.multiplier)+"}" + ", "
            else:
                predicateBody += "random("+str(5.0*self.multiplier)+", "+str(6.0*self.multiplier)+", B"+str(i)+"W" + "), "
                predicateBody += "{B"+str(i)+"H = B"+str(i)+"W - "+str(3.0*self.multiplier)+"}" + ", "
            if bedInfo[i][1] == 1:
                predicateBody += "{B"+str(i)+"X = ZeroX}, random(ZeroY, Rheightbound, B"+str(i)+"Y"+"), "
            elif bedInfo[i][1] == 2:
                predicateBody += "{B"+str(i)+"Y + B"+str(i)+"H = Rheightbound}, random(ZeroX, Rwidthbound, B"+str(i)+"X"+"), "
            elif bedInfo[i][1] == 3:
                predicateBody += "{B"+str(i)+"X + B"+str(i)+"W = Rwidthbound}, random(ZeroY, Rheightbound, B"+str(i)+"Y"+"), "
            elif bedInfo[i][1] == 4:
                predicateBody += "{B"+str(i)+"Y = ZeroY}, random(ZeroX, Rwidthbound, B"+str(i)+"X"+"), "

        # generazione dei Comò -----------------------------------------------------------------------

        for i in range(0, bedNumber):
            if bedInfo[i][1] == 1:
                if random.randint(1, 2) == 1: #sopra
                    predicateBody += "{BS"+str(i)+"X = ZeroX, BS"+str(i)+"Y = B"+str(i)+"Y + B"+str(i)+"H}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
                else: #sotto
                    predicateBody += "{BS"+str(i)+"X = ZeroX, BS"+str(i)+"Y + BS"+str(i)+"H = B"+str(i)+"Y}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
            elif bedInfo[i][1] == 2:
                if random.randint(1, 2) == 1: #destra
                    predicateBody += "{BS"+str(i)+"Y + BS"+str(i)+"H = Rheightbound, BS"+str(i)+"X = B"+str(i)+"X + B"+str(i)+"W}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
                else: #sinistra
                    predicateBody += "{BS"+str(i)+"Y + BS"+str(i)+"H = Rheightbound, BS"+str(i)+"X + BS"+str(i)+"W = B"+str(i)+"X}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
            elif bedInfo[i][1] == 3:
                if random.randint(1, 2) == 1: #sopra
                    predicateBody += "{BS"+str(i)+"X + BS"+str(i)+"W = Rwidthbound, BS"+str(i)+"Y = B"+str(i)+"Y + B"+str(i)+"H}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
                else: #sotto
                    predicateBody += "{BS"+str(i)+"X + BS"+str(i)+"W = Rwidthbound, BS"+str(i)+"Y + BS"+str(i)+"H = B"+str(i)+"Y}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
            elif bedInfo[i][1] == 4:
                if random.randint(1, 2) == 1: #destra
                    predicateBody += "{BS"+str(i)+"Y = ZeroY, BS"+str(i)+"X = B"+str(i)+"X + B"+str(i)+"W}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "
                else: #sinistra
                    predicateBody += "{BS"+str(i)+"Y = ZeroY, BS"+str(i)+"X + BS"+str(i)+"W = B"+str(i)+"X}, random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", BS"+str(i)+"W), {BS"+str(i)+"H = BS"+str(i)+"W}, "

        # generazione degli Armadi -----------------------------------------------------------------------

        for i in range(0, wardrobeNumber):
            predicateBody += "{W"+str(i)+"X + W"+str(i)+"W =< Rwidthbound, W"+str(i)+"Y + W"+str(i)+"H =< Rheightbound}, "



        for i in range(0, wardrobeNumber):
            if wardrobeInfo[i] == 1:
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", W"+str(i)+"W" + "), "
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(7.5*self.multiplier)+", W"+str(i)+"H" + "), "
                predicateBody += "{W"+str(i)+"X = ZeroX}, random(ZeroY, Rheightbound, W"+str(i)+"Y"+"), "
            elif wardrobeInfo[i] == 2:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(7.5*self.multiplier)+", W"+str(i)+"W" + "), "
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", W"+str(i)+"H" + "), "
                predicateBody += "{W"+str(i)+"Y + W"+str(i)+"H = Rheightbound}, random(ZeroX, Rwidthbound, W"+str(i)+"X"+"), "
            elif wardrobeInfo[i] == 3:
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", W"+str(i)+"W" + "), "
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(7.5*self.multiplier)+", W"+str(i)+"H" + "), "
                predicateBody += "{W"+str(i)+"X + W"+str(i)+"W = Rwidthbound}, random(ZeroY, Rheightbound, W"+str(i)+"Y"+"), "
            elif wardrobeInfo[i] == 4:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(7.5*self.multiplier)+", W"+str(i)+"W" + "), "
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", W"+str(i)+"H" + "), "
                predicateBody += "{W"+str(i)+"Y = ZeroY}, random(ZeroX, Rwidthbound, W"+str(i)+"X"+"), "

        # generazione delle constraint per le collisioni

        # -- Beds B x B --
        for i in range(0, bedNumber):
            for j in range(i+1, bedNumber):
                predicateBody += "{(B"+str(i)+"X + B"+str(i)+"W =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< B"+str(i)+"X) ; (B"+str(i)+"Y + B"+str(i)+"H =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< B"+str(i)+"Y)}, "

        # -- Beds x Door --
        for j in range(0, bedNumber):
            if bedroom.door.width == 0:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< "+str(bedroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bedroom.door.y + bedroom.door.height)+" =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< "+str(bedroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width)+" =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< "+str(bedroom.door.x)+") ; ("+str(bedroom.door.y + bedroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< "+str(bedroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- BedSides BS x BS --
        for i in range(0, bedNumber):
            for j in range(i+1, bedNumber):
                predicateBody += "{(BS"+str(i)+"X + BS"+str(i)+"W =< BS"+str(j)+"X ; BS"+str(j)+"X + BS"+str(j)+"W =< BS"+str(i)+"X) ; (BS"+str(i)+"Y + BS"+str(i)+"H =< BS"+str(j)+"Y ; BS"+str(j)+"Y + BS"+str(j)+"H =< BS"+str(i)+"Y)}, "

        # -- BedSides x Door --
        for j in range(0, bedNumber):
            if bedroom.door.width == 0:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< BS"+str(j)+"X ; BS"+str(j)+"X + BS"+str(j)+"W =< "+str(bedroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bedroom.door.y + bedroom.door.height)+" =< BS"+str(j)+"Y ; BS"+str(j)+"Y + BS"+str(j)+"H =< "+str(bedroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width)+" =< BS"+str(j)+"X ; BS"+str(j)+"X + BS"+str(j)+"W =< "+str(bedroom.door.x)+") ; ("+str(bedroom.door.y + bedroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< BS"+str(j)+"Y ; BS"+str(j)+"Y + BS"+str(j)+"H =< "+str(bedroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Wardrobes W x W --
        for i in range(0, wardrobeNumber):
            for j in range(i+1, wardrobeNumber):
                predicateBody += "{(W"+str(i)+"X + W"+str(i)+"W =< W"+str(j)+"X ; W"+str(j)+"X + W"+str(j)+"W =< W"+str(i)+"X) ; (W"+str(i)+"Y + W"+str(i)+"H =< W"+str(j)+"Y ; W"+str(j)+"Y + W"+str(j)+"H =< W"+str(i)+"Y)}, "

        # -- Wardrobes x Door --
        for j in range(0, wardrobeNumber):
            if bedroom.door.width == 0:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< W"+str(j)+"X ; W"+str(j)+"X + W"+str(j)+"W =< "+str(bedroom.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(bedroom.door.y + bedroom.door.height)+" =< W"+str(j)+"Y ; W"+str(j)+"Y + W"+str(j)+"H =< "+str(bedroom.door.y)+")}, "
            else:
                predicateBody += "{("+str(bedroom.door.x + bedroom.door.width)+" =< W"+str(j)+"X ; W"+str(j)+"X + W"+str(j)+"W =< "+str(bedroom.door.x)+") ; ("+str(bedroom.door.y + bedroom.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< W"+str(j)+"Y ; W"+str(j)+"Y + W"+str(j)+"H =< "+str(bedroom.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Beds + BedSides B x BS --
        for i in range(0, bedNumber):
            for j in range(0, bedNumber):
                if i != j:
                    predicateBody += "{(BS"+str(i)+"X + BS"+str(i)+"W =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< BS"+str(i)+"X) ; (BS"+str(i)+"Y + BS"+str(i)+"H =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< BS"+str(i)+"Y)}, "

        # -- Beds + Wardrobes B x W --
        for j in range(0, bedNumber):
            for i in range(0, wardrobeNumber):
                predicateBody += "{(W"+str(i)+"X + W"+str(i)+"W =< B"+str(j)+"X ; B"+str(j)+"X + B"+str(j)+"W =< W"+str(i)+"X) ; (W"+str(i)+"Y + W"+str(i)+"H =< B"+str(j)+"Y ; B"+str(j)+"Y + B"+str(j)+"H =< W"+str(i)+"Y)}, "

        # -- BedSides + Wardrobes BS x W --
        for i in range(0, bedNumber):
            for j in range(0, wardrobeNumber):
                predicateBody += "{(BS"+str(i)+"X + BS"+str(i)+"W =< W"+str(j)+"X ; W"+str(j)+"X + W"+str(j)+"W =< BS"+str(i)+"X) ; (BS"+str(i)+"Y + BS"+str(i)+"H =< W"+str(j)+"Y ; W"+str(j)+"Y + W"+str(j)+"H =< BS"+str(i)+"Y)}, "

        predicateBody = predicateBody[:-2]
        predicateBody += ", !"
        # no il punto . dopo il predicato

        print("Il predicato per generare la camera da letto "+str(bedroom.index)+" è:")
        print(predicateHead + predicateBody)
        self.prolog.assertz(predicateHead + predicateBody)

        for sol in self.prolog.query(query):
            for i in range(0, bedNumber):
                bedSprite = pygame.sprite.Sprite()
                bedSprite.image = self.BED_IMAGE
                spriteOrientation = "S"
                if bedInfo[i][1] == 1:
                    if bedInfo[i][0] == 0:
                        bedSprite.image = pygame.transform.rotate(bedSprite.image, 90)
                        spriteOrientation = "E"
                    else:
                        if random.randint(0,1) == 0:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, 180)
                            spriteOrientation = "N"
                elif bedInfo[i][1] == 4:
                    if bedInfo[i][0] == 0:
                        if random.randint(0,1) == 0:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, 90)
                            spriteOrientation = "E"
                        else:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, -90)
                            spriteOrientation = "W"
                elif bedInfo[i][1] == 3:
                    if bedInfo[i][0] == 0:
                        bedSprite.image = pygame.transform.rotate(bedSprite.image, -90)
                        spriteOrientation = "W"
                    else:
                        if random.randint(0,1) == 0:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, 180)
                            spriteOrientation = "N"
                elif bedInfo[i][1] == 2:
                    if bedInfo[i][0] == 0:
                        if random.randint(0,1) == 0:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, 90)
                            spriteOrientation = "E"
                        else:
                            bedSprite.image = pygame.transform.rotate(bedSprite.image, -90)
                            spriteOrientation = "W"
                    else:
                        bedSprite.image = pygame.transform.rotate(bedSprite.image, 180)
                        spriteOrientation = "N"
                bedSprite.image = pygame.transform.scale(bedSprite.image, (int(sol["B"+str(i)+"W"]), int(sol["B"+str(i)+"H"])))
                bedSprite.rect = pygame.Rect(sol["B"+str(i)+"X"], sol["B"+str(i)+"Y"], sol["B"+str(i)+"W"], sol["B"+str(i)+"H"])
                bed = Gameobject(sol["B"+str(i)+"X"], sol["B"+str(i)+"Y"], sol["B"+str(i)+"W"], sol["B"+str(i)+"H"], bedSprite, BED)
                bed.orientation = spriteOrientation

                bedsideSprite = pygame.sprite.Sprite()
                bedsideSprite.image = self.BEDSIDE_IMAGE
                bedsideSprite.image = pygame.transform.scale(bedsideSprite.image, (int(sol["BS"+str(i)+"W"]), int(sol["BS"+str(i)+"H"])))
                bedsideSprite.rect = pygame.Rect(sol["BS"+str(i)+"X"], sol["BS"+str(i)+"Y"], sol["BS"+str(i)+"W"], sol["BS"+str(i)+"H"])
                bedside = Gameobject(sol["BS"+str(i)+"X"], sol["BS"+str(i)+"Y"], sol["BS"+str(i)+"W"], sol["BS"+str(i)+"H"], bedsideSprite, BEDSIDE)
                bed.children.append(bedside)
                bedroom.children.append(bed)
            for i in range(0, wardrobeNumber):
                wardrobeSprite = pygame.sprite.Sprite()
                wardrobeSprite.image = self.WARDROBE_IMAGE
                spriteOrientation = "S"
                if wardrobeInfo[i] == 2:
                    wardrobeSprite.image = pygame.transform.rotate(wardrobeSprite.image, 90)
                    spriteOrientation = "E"
                elif wardrobeInfo[i] == 4:
                    wardrobeSprite.image = pygame.transform.rotate(wardrobeSprite.image, -90)
                    spriteOrientation = "E"

                wardrobeSprite.image = pygame.transform.scale(wardrobeSprite.image, (int(sol["W"+str(i)+"W"]), int(sol["W"+str(i)+"H"])))
                wardrobeSprite.rect = pygame.Rect(sol["W"+str(i)+"X"], sol["W"+str(i)+"Y"], sol["W"+str(i)+"W"], sol["W"+str(i)+"H"])
                wardrobe = Gameobject(sol["W"+str(i)+"X"], sol["W"+str(i)+"Y"], sol["W"+str(i)+"W"], sol["W"+str(i)+"H"], wardrobeSprite, WARDROBE)
                wardrobe.orientation = spriteOrientation
                bedroom.children.append(wardrobe)
        self.prolog.retract(predicateHead + predicateBody)

    def getBedrooms(self):
        result = []
        for bedroom in (x for x in self.rooms if x.type == BEDROOM):
            result.append(bedroom)
        return result

    def populateKitchen(self, kitchen, deskNumber, tableNumber):
        headVariables = ""
        predicateHead = "generateKitchen"+str(kitchen.index)+"(ZeroX, ZeroY, RoomWidth, RoomHeight, "
        query = "generateKitchen"+str(kitchen.index)+"("+str(kitchen.x)+", "+str(kitchen.y)+", "+str(kitchen.width)+", "+str(kitchen.height)+", "
        for i in range(0, deskNumber):
            headVariables += "D"+str(i)+"X"+", "
            headVariables += "D"+str(i)+"Y"+", "
            headVariables += "D"+str(i)+"W"+", "
            headVariables += "D"+str(i)+"H"+", "

            query += "D"+str(i)+"X"+", "
            query += "D"+str(i)+"Y"+", "
            query += "D"+str(i)+"W"+", "
            query += "D"+str(i)+"H"+", "
        for i in range(0, tableNumber):
            headVariables += "KTA"+str(i)+"X"+", "
            headVariables += "KTA"+str(i)+"Y"+", "
            headVariables += "KTA"+str(i)+"W"+", "
            headVariables += "KTA"+str(i)+"H"+", "

            query += "KTA"+str(i)+"X"+", "
            query += "KTA"+str(i)+"Y"+", "
            query += "KTA"+str(i)+"W"+", "
            query += "KTA"+str(i)+"H"+", "
        for i in range(0, 4*tableNumber):
            headVariables += "C"+str(i)+"X"+", "
            headVariables += "C"+str(i)+"Y"+", "
            headVariables += "C"+str(i)+"W"+", "
            headVariables += "C"+str(i)+"H"+", "

            query += "C"+str(i)+"X"+", "
            query += "C"+str(i)+"Y"+", "
            query += "C"+str(i)+"W"+", "
            query += "C"+str(i)+"H"+", "

        query = query[:-2]
        predicateHead = predicateHead + headVariables
        predicateHead = predicateHead[:-2]
        predicateHead += ") "
        query += ")"

        predicateBody = ":- repeat, "

        # generazione dei Banconi -----------------------------------------------------------------------
        predicateBody += "Rwidthbound is RoomWidth + ZeroX, Rheightbound is RoomHeight + ZeroY, random("+str(1.5*self.multiplier)+", "+str(1.8*self.multiplier)+", DeskSize), "
        # -- constraints di X ed Y dei Banconi
        #for i in range(0, deskNumber):
        #   predicateBody += "{D"+str(i)+"X + D"+str(i)+"W =< Rwidthbound, D"+str(i)+"Y + D"+str(i)+"H =< Rheightbound}, "
        # --
        firstAngle = []
        secondAngle = []
        thirdAngle = []
        fourthAngle = []

        firstAngleDisabled = False
        secondAngleDisabled = False
        thirdAngleDisabled = False
        fourthAngleDisabled = False

        if kitchen.door.x == kitchen.x and kitchen.door.width == 0:
            firstAngleDisabled = True
            fourthAngleDisabled = True
        elif kitchen.door.x == kitchen.x + kitchen.width and kitchen.door.width == 0:
            secondAngleDisabled = True
            thirdAngleDisabled = True
        elif kitchen.door.y == kitchen.y and kitchen.door.height == 0:
            fourthAngleDisabled = True
            thirdAngleDisabled = True
        elif kitchen.door.y == kitchen.y + kitchen.height and kitchen.door.height == 0:
            firstAngleDisabled = True
            secondAngleDisabled = True

        for i in range(0, deskNumber):

            posizionato = False
            while(not posizionato):

                newPosition = random.randint(1, 4)
                # print("newPosition: "+ str(newPosition))
                ostacoloTrovato = False

                if newPosition == 1 and not firstAngleDisabled:
                    if(len(firstAngle) < 2):
                        if(len(firstAngle) == 1):
                            orientamentoBanconePre = firstAngle[0][1]
                            orientamentoBanconeNew = 1 - orientamentoBanconePre
                            if(orientamentoBanconePre == 0):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in fourthAngle:
                                        ostacoloTrovato = True
                            if(orientamentoBanconePre == 1):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in secondAngle:
                                        ostacoloTrovato = True
                            if(not ostacoloTrovato):
                                #codice di generazione
                                if(orientamentoBanconeNew == 0):
                                    predicateBody += "D"+str(i)+"X is ZeroX + D"+str(firstAngle[0][0])+"W, {D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomWidth - 2*DeskSize,  random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), "
                                    firstAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"X is ZeroX, {D"+str(i)+"Y = Rheightbound - DeskSize - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomHeight - 2*DeskSize,  random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                    firstAngle.append((i, 1))
                                posizionato = True
                        else:
                            optionZero = True
                            optionOne = True
                            for j in range(0, deskNumber):
                                if (j, 0) in secondAngle:
                                    optionZero = False
                            for j in range(0, deskNumber):
                                if (j, 1) in fourthAngle:
                                    optionOne = False
                            if(optionZero and optionOne):
                                #orientamento random
                                if(random.randint(0, 1) == 0):
                                    predicateBody += "D"+str(i)+"X is ZeroX, {D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), "
                                    firstAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"X is ZeroX, {D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize,  random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                    firstAngle.append((i, 1))
                                posizionato = True
                            if(optionZero and not optionOne):
                                #orientamento zero
                                predicateBody += "D"+str(i)+"X is ZeroX, {D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), "
                                firstAngle.append((i, 0))
                                posizionato = True
                            if(optionOne and not optionZero):
                                #orientamento one
                                predicateBody += "D"+str(i)+"X is ZeroX, {D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize,  random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                firstAngle.append((i, 1))
                                posizionato = True

                if newPosition == 2 and not secondAngleDisabled:
                    if(len(secondAngle) < 2):
                        if(len(secondAngle) == 1):
                            orientamentoBanconePre = secondAngle[0][1]
                            orientamentoBanconeNew = 1 - orientamentoBanconePre
                            if(orientamentoBanconePre == 1):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in firstAngle:
                                        ostacoloTrovato = True
                            if(orientamentoBanconePre == 0):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in thirdAngle:
                                        ostacoloTrovato = True
                            if(not ostacoloTrovato):
                                #codice di generazione
                                if(orientamentoBanconeNew == 0):
                                    predicateBody += "{D"+str(i)+"Y = Rheightbound - DeskSize}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomWidth - 2*DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - DeskSize - D"+str(i)+"W, "
                                    secondAngle.append((i, 0))
                                else:
                                    predicateBody += "{D"+str(i)+"Y = Rheightbound - DeskSize - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomHeight - 2*DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                    secondAngle.append((i, 1))
                                posizionato = True
                        else:
                            optionZero = True
                            optionOne = True
                            for j in range(0, deskNumber):
                                if (j, 0) in firstAngle:
                                    optionZero = False
                            for j in range(0, deskNumber):
                                if (j, 1) in thirdAngle:
                                    optionOne = False
                            if(optionZero and optionOne):
                                #orientamento random
                                if(random.randint(0, 1) == 0):
                                    predicateBody += "{D"+str(i)+"Y = Rheightbound - DeskSize}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - D"+str(i)+"W, "
                                    secondAngle.append((i, 0))
                                else:
                                    predicateBody += "{D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                    secondAngle.append((i, 1))
                                posizionato = True
                            if(optionZero and not optionOne):
                                #orientamento zero
                                predicateBody += "{D"+str(i)+"Y = Rheightbound - DeskSize}, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - D"+str(i)+"W, "
                                secondAngle.append((i, 0))
                                posizionato = True
                            if(optionOne and not optionZero):
                                #orientamento one
                                predicateBody += "{D"+str(i)+"Y = Rheightbound - D"+str(i)+"H}, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                secondAngle.append((i, 1))
                                posizionato = True

                if newPosition == 3 and not thirdAngleDisabled:
                    if(len(thirdAngle) < 2):
                        if(len(thirdAngle) == 1):
                            orientamentoBanconePre = thirdAngle[0][1]
                            orientamentoBanconeNew = 1 - orientamentoBanconePre
                            if(orientamentoBanconePre == 1):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in fourthAngle:
                                        ostacoloTrovato = True
                            if(orientamentoBanconePre == 0):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in secondAngle:
                                        ostacoloTrovato = True
                            if(not ostacoloTrovato):
                                #codice di generazione
                                if(orientamentoBanconeNew == 0):
                                    predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomWidth - 2*DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - DeskSize - D"+str(i)+"W, "
                                    thirdAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"Y is ZeroY + DeskSize, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomHeight - 2*DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                    thirdAngle.append((i, 1))
                                posizionato = True
                        else:
                            optionZero = True
                            optionOne = True
                            for j in range(0, deskNumber):
                                if (j, 0) in fourthAngle:
                                    optionZero = False
                            for j in range(0, deskNumber):
                                if (j, 1) in secondAngle:
                                    optionOne = False
                            if(optionZero and optionOne):
                                #orientamento random
                                if(random.randint(0, 1) == 0):
                                    predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - D"+str(i)+"W, "
                                    thirdAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                    thirdAngle.append((i, 1))
                                posizionato = True
                            if(optionZero and not optionOne):
                                #orientamento zero
                                predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), D"+str(i)+"X is Rwidthbound - D"+str(i)+"W, "
                                thirdAngle.append((i, 0))
                                posizionato = True
                            if(optionOne and not optionZero):
                                #orientamento one
                                predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), D"+str(i)+"X is Rwidthbound - DeskSize, "
                                thirdAngle.append((i, 1))
                                posizionato = True

                if newPosition == 4 and not fourthAngleDisabled:
                    if(len(fourthAngle) < 2):
                        if(len(fourthAngle) == 1):
                            orientamentoBanconePre = fourthAngle[0][1]
                            orientamentoBanconeNew = 1 - orientamentoBanconePre
                            if(orientamentoBanconePre == 1):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in thirdAngle:
                                        ostacoloTrovato = True
                            if(orientamentoBanconePre == 0):
                                for j in range(0, deskNumber):
                                    if (j, orientamentoBanconeNew) in firstAngle:
                                        ostacoloTrovato = True
                            if(not ostacoloTrovato):
                                #codice di generazione
                                if(orientamentoBanconeNew == 0):
                                    predicateBody += "D"+str(i)+"Y is ZeroY, D"+str(i)+"X is ZeroX + DeskSize, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - 2*DeskSize, RoomSupBound is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", RoomSupBound, D"+str(i)+"W), "
                                    fourthAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"X is ZeroX, D"+str(i)+"Y is ZeroY + DeskSize, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - 2*DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                    fourthAngle.append((i, 1))
                                posizionato = True
                        else:
                            optionZero = True
                            optionOne = True
                            for j in range(0, deskNumber):
                                if (j, 0) in thirdAngle:
                                    optionZero = False
                            for j in range(0, deskNumber):
                                if (j, 1) in firstAngle:
                                    optionOne = False
                            if(optionZero and optionOne):
                                #orientamento random
                                if(random.randint(0, 1) == 0):
                                    predicateBody += "D"+str(i)+"X is ZeroX, D"+str(i)+"Y is ZeroY, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), "
                                    fourthAngle.append((i, 0))
                                else:
                                    predicateBody += "D"+str(i)+"X is ZeroX, D"+str(i)+"Y is ZeroY, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                    fourthAngle.append((i, 1))
                                posizionato = True
                            if(optionZero and not optionOne):
                                #orientamento zero
                                predicateBody += "D"+str(i)+"X is ZeroX, D"+str(i)+"Y is ZeroY, D"+str(i)+"H is DeskSize, DeskInfBound"+str(i)+" is RoomWidth * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomWidth - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"W), "
                                fourthAngle.append((i, 0))
                                posizionato = True
                            if(optionOne and not optionZero):
                                #orientamento one
                                predicateBody += "D"+str(i)+"X is ZeroX, D"+str(i)+"Y is ZeroY, D"+str(i)+"W is DeskSize, DeskInfBound"+str(i)+" is RoomHeight * (7/10) - DeskSize, DeskSupBound"+str(i)+" is RoomHeight - DeskSize, random(DeskInfBound"+str(i)+", DeskSupBound"+str(i)+", D"+str(i)+"H), "
                                fourthAngle.append((i, 1))
                                posizionato = True

        # Generazione tavolo cucina
        predicateBody += "random("+str(0.7*self.multiplier)+", "+str(1.0*self.multiplier)+", ChairSize), "
        for i in range(0, tableNumber):
            predicateBody += "KTA"+str(i)+"WInfBound is RoomWidth*(1/5), KTA"+str(i)+"WSupBound is RoomWidth*(3/10), random(KTA"+str(i)+"WInfBound, KTA"+str(i)+"WSupBound, KTA"+str(i)+"W), "
            predicateBody += "KTA"+str(i)+"HInfBound is RoomHeight*(1/5), KTA"+str(i)+"HSupBound is RoomHeight*(3/10), random(KTA"+str(i)+"HInfBound, KTA"+str(i)+"HSupBound, KTA"+str(i)+"H), "

            chairStartIndex = i*4
            for k in range(chairStartIndex, chairStartIndex+4):
                predicateBody += "C"+str(k)+"W is ChairSize, C"+str(k)+"H is C"+str(k)+"W, "

            firstSideOccupied = False
            secondSideOccupied = False
            thirdSideOccupied = False
            fourthSideOccupied = False
            for j in range(0, deskNumber):
                if (j, 1) in firstAngle or (j, 1) in fourthAngle:
                    firstSideOccupied = True
                if (j, 0) in firstAngle or (j, 0) in secondAngle:
                    secondSideOccupied = True
                if (j, 1) in secondAngle or (j, 1) in thirdAngle:
                    thirdSideOccupied = True
                if (j, 0) in thirdAngle or (j, 0) in fourthAngle:
                    fourthSideOccupied = True
            if firstSideOccupied:
                predicateBody += "KTA"+str(i)+"XInfBound is ZeroX + DeskSize + ChairSize, "
            else:
                predicateBody += "KTA"+str(i)+"XInfBound is ZeroX + ChairSize, "
            if secondSideOccupied:
                predicateBody += "KTA"+str(i)+"YSupBound is Rheightbound - DeskSize - ChairSize - KTA"+str(i)+"H, "
            else:
                predicateBody += "KTA"+str(i)+"YSupBound is Rheightbound - ChairSize - KTA"+str(i)+"H, "
            if thirdSideOccupied:
                predicateBody += "KTA"+str(i)+"XSupBound is Rwidthbound - DeskSize - ChairSize - KTA"+str(i)+"W, "
            else:
                predicateBody += "KTA"+str(i)+"XSupBound is Rwidthbound - ChairSize - KTA"+str(i)+"W, "
            if fourthSideOccupied:
                predicateBody += "KTA"+str(i)+"YInfBound is ZeroY + DeskSize + ChairSize, "
            else:
                predicateBody += "KTA"+str(i)+"YInfBound is ZeroY + ChairSize, "

            predicateBody += "random(KTA"+str(i)+"XInfBound, KTA"+str(i)+"XSupBound, KTA"+str(i)+"X), random(KTA"+str(i)+"YInfBound, KTA"+str(i)+"YSupBound, KTA"+str(i)+"Y), "

            predicateBody += "C"+str(chairStartIndex)+"X is KTA"+str(i)+"X + ((KTA"+str(i)+"W - ChairSize)/2), C"+str(chairStartIndex)+"Y is KTA"+str(i)+"Y + KTA"+str(i)+"H, "
            predicateBody += "C"+str(chairStartIndex+1)+"X is KTA"+str(i)+"X + KTA"+str(i)+"W, C"+str(chairStartIndex+1)+"Y is KTA"+str(i)+"Y + ((KTA"+str(i)+"H - ChairSize)/2), "
            predicateBody += "C"+str(chairStartIndex+2)+"X is KTA"+str(i)+"X + ((KTA"+str(i)+"W - ChairSize)/2), C"+str(chairStartIndex+2)+"Y is KTA"+str(i)+"Y - ChairSize, "
            predicateBody += "C"+str(chairStartIndex+3)+"X is KTA"+str(i)+"X - ChairSize, C"+str(chairStartIndex+3)+"Y is KTA"+str(i)+"Y + ((KTA"+str(i)+"H - ChairSize)/2), "

        # -- Tables x Door --
        for j in range(0, tableNumber):
            if kitchen.door.width == 0:
                predicateBody += "{("+str(kitchen.door.x + kitchen.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< KTA"+str(j)+"X - ChairSize ; KTA"+str(j)+"X + KTA"+str(j)+"W + ChairSize =< "+str(kitchen.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(kitchen.door.y + kitchen.door.height)+" =< KTA"+str(j)+"Y - ChairSize ; KTA"+str(j)+"Y + KTA"+str(j)+"H + ChairSize =< "+str(kitchen.door.y)+")}, "
            else:
                predicateBody += "{("+str(kitchen.door.x + kitchen.door.width)+" =< KTA"+str(j)+"X - ChairSize ; KTA"+str(j)+"X + KTA"+str(j)+"W + ChairSize =< "+str(kitchen.door.x)+") ; ("+str(kitchen.door.y + kitchen.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< KTA"+str(j)+"Y - ChairSize ; KTA"+str(j)+"Y + KTA"+str(j)+"H + ChairSize =< "+str(kitchen.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "


        predicateBody = predicateBody[:-2]
        predicateBody += ", !"
        # no il punto . dopo il predicato

        print("Il predicato per generare le cucine è:")
        print(predicateHead + predicateBody)
        self.prolog.assertz(predicateHead + predicateBody)

        for sol in self.prolog.query(query):
            for i in range(0, deskNumber):
                deskSprite = pygame.sprite.Sprite()
                deskSprite.image = self.DESK_IMAGE
                spriteOrientation = "S"
                if (i, 0) in firstAngle or (i, 0) in secondAngle or (i, 0) in thirdAngle or (i, 0) in fourthAngle:
                    deskSprite.image = pygame.transform.rotate(deskSprite.image, 90)
                    spriteOrientation = "E"
                deskSprite.image = pygame.transform.scale(deskSprite.image, (int(sol["D"+str(i)+"W"]), int(sol["D"+str(i)+"H"])))
                deskSprite.rect = pygame.Rect(sol["D"+str(i)+"X"], sol["D"+str(i)+"Y"], sol["D"+str(i)+"W"], sol["D"+str(i)+"H"])
                desk = Gameobject(sol["D"+str(i)+"X"], sol["D"+str(i)+"Y"], sol["D"+str(i)+"W"], sol["D"+str(i)+"H"], deskSprite, DESK)
                desk.orientation = spriteOrientation
                kitchen.children.append(desk)
            for i in range(0, tableNumber):
                tableSprite = pygame.sprite.Sprite()
                tableSprite.image = self.TABLE_IMAGE
                tableSprite.image = pygame.transform.scale(tableSprite.image, (int(sol["KTA"+str(i)+"W"]), int(sol["KTA"+str(i)+"H"])))
                tableSprite.rect = pygame.Rect(sol["KTA"+str(i)+"X"], sol["KTA"+str(i)+"Y"], sol["KTA"+str(i)+"W"], sol["KTA"+str(i)+"H"])
                table = Gameobject(sol["KTA"+str(i)+"X"], sol["KTA"+str(i)+"Y"], sol["KTA"+str(i)+"W"], sol["KTA"+str(i)+"H"], tableSprite, TABLE)
                for j in range(i*4, i*4+4):
                    chairSprite = pygame.sprite.Sprite()
                    chairSprite.image = self.CHAIR_IMAGE
                    chairSprite.image = pygame.transform.rotate(chairSprite.image, ((j+2) % 4)*(90))
                    chairSprite.image = pygame.transform.scale(chairSprite.image, (int(sol["C"+str(j)+"W"]), int(sol["C"+str(j)+"H"])))
                    chairSprite.rect = pygame.Rect(sol["C"+str(j)+"X"], sol["C"+str(j)+"Y"], sol["C"+str(j)+"W"], sol["C"+str(j)+"H"])
                    chair = Gameobject(sol["C"+str(j)+"X"], sol["C"+str(j)+"Y"], sol["C"+str(j)+"W"], sol["C"+str(j)+"H"], chairSprite, CHAIR)
                    if j == i*4:
                        chair.orientation = "S"
                    elif j == i*4+1:
                        chair.orientation = "E"
                    elif j == i*4 + 2:
                        chair.orientation = "N"
                    else:
                        chair.orientation = "W"
                    table.children.append(chair)
                kitchen.children.append(table)
        self.prolog.retract(predicateHead + predicateBody)

    def getKitchens(self):
        results = []
        for x in (y for y in self.rooms if y.type == KITCHEN):
            results.append(x)
        return results

    def populateHall(self, hall, tableNumber, sofaNumber, cupboardNumber, sofaDistanceThreshold):
        headVariables = ""
        predicateHead = "generateHall"+str(hall.index)+"(ZeroX, ZeroY, RoomWidth, RoomHeight, "
        query = "generateHall"+str(hall.index)+"("+str(hall.x)+", "+str(hall.y)+", "+str(hall.width)+", "+str(hall.height)+", "
        for i in range(0, tableNumber):
            headVariables += "TA"+str(i)+"X"+", "
            headVariables += "TA"+str(i)+"Y"+", "
            headVariables += "TA"+str(i)+"W"+", "
            headVariables += "TA"+str(i)+"H"+", "

            query += "TA"+str(i)+"X"+", "
            query += "TA"+str(i)+"Y"+", "
            query += "TA"+str(i)+"W"+", "
            query += "TA"+str(i)+"H"+", "
        for i in range(0, 4*tableNumber):
            headVariables += "C"+str(i)+"X"+", "
            headVariables += "C"+str(i)+"Y"+", "
            headVariables += "C"+str(i)+"W"+", "
            headVariables += "C"+str(i)+"H"+", "

            query += "C"+str(i)+"X"+", "
            query += "C"+str(i)+"Y"+", "
            query += "C"+str(i)+"W"+", "
            query += "C"+str(i)+"H"+", "
        for i in range(0, sofaNumber):
            headVariables += "SO"+str(i)+"X"+", "
            headVariables += "SO"+str(i)+"Y"+", "
            headVariables += "SO"+str(i)+"W"+", "
            headVariables += "SO"+str(i)+"H"+", "

            query += "SO"+str(i)+"X"+", "
            query += "SO"+str(i)+"Y"+", "
            query += "SO"+str(i)+"W"+", "
            query += "SO"+str(i)+"H"+", "
        for i in range(0, cupboardNumber):
            headVariables += "CB"+str(i)+"X"+", "
            headVariables += "CB"+str(i)+"Y"+", "
            headVariables += "CB"+str(i)+"W"+", "
            headVariables += "CB"+str(i)+"H"+", "

            query += "CB"+str(i)+"X"+", "
            query += "CB"+str(i)+"Y"+", "
            query += "CB"+str(i)+"W"+", "
            query += "CB"+str(i)+"H"+", "

        predicateHead = predicateHead + headVariables
        predicateHead = predicateHead[:-2]
        predicateHead += ") "

        query = query[:-2]
        query += ")"

        predicateBody = ":- repeat, "

        predicateBody += "Rwidthbound is RoomWidth + ZeroX, Rheightbound is RoomHeight + ZeroY, "

        # Generazione tavolo sala
        predicateBody += "random("+str(0.7*self.multiplier)+", "+str(1.0*self.multiplier)+", ChairSize), "
        for i in range(0, tableNumber):
            predicateBody += "random("+str(2.5*self.multiplier)+", "+str(6.0*self.multiplier)+", TA"+str(i)+"W), random("+str(2.5*self.multiplier)+", "+str(6.0*self.multiplier)+", TA"+str(i)+"H), "
            predicateBody += "{TA"+str(i)+"W * TA"+str(i)+"H >= "+str(8.0*self.multiplier**2)+", TA"+str(i)+"W * TA"+str(i)+"H =< "+str(15.0*self.multiplier**2)+"}, "

            chairStartIndex = i*4
            for k in range(chairStartIndex, chairStartIndex+4):
                predicateBody += "C"+str(k)+"W is ChairSize, C"+str(k)+"H is C"+str(k)+"W, "

            predicateBody += "TA"+str(i)+"XInf is ZeroX + ChairSize, TA"+str(i)+"XSup is Rwidthbound - ChairSize - TA"+str(i)+"W, TA"+str(i)+"YInf is ZeroY + ChairSize, TA"+str(i)+"YSup is Rheightbound - TA"+str(i)+"H - ChairSize, random(TA"+str(i)+"XInf, TA"+str(i)+"XSup, TA"+str(i)+"X), random(TA"+str(i)+"YInf, TA"+str(i)+"YSup, TA"+str(i)+"Y), "



            predicateBody += "C"+str(chairStartIndex)+"X is TA"+str(i)+"X + ((TA"+str(i)+"W - ChairSize)/2), C"+str(chairStartIndex)+"Y is TA"+str(i)+"Y + TA"+str(i)+"H, "
            predicateBody += "C"+str(chairStartIndex+1)+"X is TA"+str(i)+"X + TA"+str(i)+"W, C"+str(chairStartIndex+1)+"Y is TA"+str(i)+"Y + ((TA"+str(i)+"H - ChairSize)/2), "
            predicateBody += "C"+str(chairStartIndex+2)+"X is TA"+str(i)+"X + ((TA"+str(i)+"W - ChairSize)/2), C"+str(chairStartIndex+2)+"Y is TA"+str(i)+"Y - ChairSize, "
            predicateBody += "C"+str(chairStartIndex+3)+"X is TA"+str(i)+"X - ChairSize, C"+str(chairStartIndex+3)+"Y is TA"+str(i)+"Y + ((TA"+str(i)+"H - ChairSize)/2), "

        # generazione delle madie -----------------------------------------------------------------------
        for i in range(0, cupboardNumber):
            predicateBody += "{CB"+str(i)+"X + CB"+str(i)+"W =< Rwidthbound, CB"+str(i)+"Y + CB"+str(i)+"H =< Rheightbound}, "

        cupboardInfo = []
        for i in range(0, cupboardNumber):
            cupboardInfo.append(random.randint(1,4))
        for i in range(0, cupboardNumber):
            if cupboardInfo[i] == 1:
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", CB"+str(i)+"W" + "), "
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(12.0*self.multiplier)+", CB"+str(i)+"H" + "), "
                predicateBody += "{CB"+str(i)+"X = ZeroX}, random(ZeroY, Rheightbound, CB"+str(i)+"Y"+"), "
            elif cupboardInfo[i] == 2:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(12.0*self.multiplier)+", CB"+str(i)+"W" + "), "
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", CB"+str(i)+"H" + "), "
                predicateBody += "{CB"+str(i)+"Y + CB"+str(i)+"H = Rheightbound}, random(ZeroX, Rwidthbound, CB"+str(i)+"X"+"), "
            elif cupboardInfo[i] == 3:
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", CB"+str(i)+"W" + "), "
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(12.0*self.multiplier)+", CB"+str(i)+"H" + "), "
                predicateBody += "{CB"+str(i)+"X + CB"+str(i)+"W = Rwidthbound}, random(ZeroY, Rheightbound, CB"+str(i)+"Y"+"), "
            elif cupboardInfo[i] == 4:
                predicateBody += "random("+str(3.0*self.multiplier)+", "+str(12.0*self.multiplier)+", CB"+str(i)+"W" + "), "
                predicateBody += "random("+str(1.5*self.multiplier)+", "+str(2.0*self.multiplier)+", CB"+str(i)+"H" + "), "
                predicateBody += "{CB"+str(i)+"Y = ZeroY}, random(ZeroX, Rwidthbound, CB"+str(i)+"X"+"), "

        # generazione dei sofa -----------------------------------------------------------------------
        sofaInfo = []
        directions = [1,2,3,4]
        for i in range(0, sofaNumber):
            sofaInfo.append(directions.pop(random.randint(0, len(directions)-1))) #1 guarda EST, 2 guarda NORD, 3 guarda OVEST, 4 guarda SUD
        for i in range(0, sofaNumber):
            if sofaInfo[i] == 1 or sofaInfo[i] == 3:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.0*self.multiplier)+", SO"+str(i)+"W), random("+str(6.0*self.multiplier)+", "+str(8.0*self.multiplier)+", SO"+str(i)+"H), "
            else:
                predicateBody += "random("+str(2.5*self.multiplier)+", "+str(3.0*self.multiplier)+", SO"+str(i)+"H), random("+str(6.0*self.multiplier)+", "+str(8.0*self.multiplier)+", SO"+str(i)+"W), "

            if sofaInfo[i] == 1:
                predicateBody += "SO"+str(i)+"HSUB is Rheightbound - SO"+str(i)+"H, random(ZeroY, SO"+str(i)+"HSUB, SO"+str(i)+"Y), SO"+str(i)+"WSUB is ZeroX + RoomWidth/2 - SO"+str(i)+"W, random(ZeroX, SO"+str(i)+"WSUB, SO"+str(i)+"X), "
            if sofaInfo[i] == 2:
                predicateBody += "SO"+str(i)+"HSUB1 is ZeroY + RoomHeight/2, SO"+str(i)+"HSUB2 is Rheightbound - SO"+str(i)+"H, random(SO"+str(i)+"HSUB1, SO"+str(i)+"HSUB2, SO"+str(i)+"Y), SO"+str(i)+"WSUB is Rwidthbound - SO"+str(i)+"W, random(ZeroX, SO"+str(i)+"WSUB, SO"+str(i)+"X), "
            if sofaInfo[i] == 3:
                predicateBody += "SO"+str(i)+"HSUB is Rheightbound - SO"+str(i)+"H, random(ZeroY, SO"+str(i)+"HSUB, SO"+str(i)+"Y), SO"+str(i)+"WSUB1 is ZeroX + RoomWidth/2, SO"+str(i)+"WSUB2 is Rwidthbound - SO"+str(i)+"W, random(SO"+str(i)+"WSUB1, SO"+str(i)+"WSUB2, SO"+str(i)+"X), "
            if sofaInfo[i] == 4:
                predicateBody += "SO"+str(i)+"HSUB is ZeroY + RoomHeight/2 - SO"+str(i)+"H, random(ZeroY, SO"+str(i)+"HSUB, SO"+str(i)+"Y), SO"+str(i)+"WSUB is Rwidthbound - SO"+str(i)+"W, random(ZeroX, SO"+str(i)+"WSUB, SO"+str(i)+"X), "


        # -- Sofa x Cupboard --
        for j in range(0, sofaNumber):
            for i in range(0, cupboardNumber):
                predicateBody += "{(CB"+str(i)+"X + CB"+str(i)+"W =< SO"+str(j)+"X - "+str(sofaDistanceThreshold*self.multiplier)+"; SO"+str(j)+"X + SO"+str(j)+"W =< CB"+str(i)+"X - "+str(sofaDistanceThreshold*self.multiplier)+") ; (CB"+str(i)+"Y + CB"+str(i)+"H =< SO"+str(j)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+" ; SO"+str(j)+"Y + SO"+str(j)+"H =< CB"+str(i)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+")}, "

        # -- Sofa x Door --
        for j in range(0, sofaNumber):
            if hall.door.width == 0:
                predicateBody += "{("+str(hall.door.x + hall.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< SO"+str(j)+"X ; SO"+str(j)+"X + SO"+str(j)+"W =< "+str(hall.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(hall.door.y + hall.door.height)+" =< SO"+str(j)+"Y ; SO"+str(j)+"Y + SO"+str(j)+"H =< "+str(hall.door.y)+")}, "
            else:
                predicateBody += "{("+str(hall.door.x + hall.door.width)+" =< SO"+str(j)+"X ; SO"+str(j)+"X + SO"+str(j)+"W =< "+str(hall.door.x)+") ; ("+str(hall.door.y + hall.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< SO"+str(j)+"Y ; SO"+str(j)+"Y + SO"+str(j)+"H =< "+str(hall.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Cupboard x Cupboard --
        for i in range(0, cupboardNumber):
            for j in range(i+1, cupboardNumber):
                predicateBody += "{(CB"+str(i)+"X + CB"+str(i)+"W =< CB"+str(j)+"X ; CB"+str(j)+"X + CB"+str(j)+"W =< CB"+str(i)+"X) ; (CB"+str(i)+"Y + CB"+str(i)+"H =< CB"+str(j)+"Y ; CB"+str(j)+"Y + CB"+str(j)+"H =< CB"+str(i)+"Y)}, "

        # -- Cupboard x Door --
        for j in range(0, cupboardNumber):
            if hall.door.width == 0:
                predicateBody += "{("+str(hall.door.x + hall.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< CB"+str(j)+"X ; CB"+str(j)+"X + CB"+str(j)+"W =< "+str(hall.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(hall.door.y + hall.door.height)+" =< CB"+str(j)+"Y ; CB"+str(j)+"Y + CB"+str(j)+"H =< "+str(hall.door.y)+")}, "
            else:
                predicateBody += "{("+str(hall.door.x + hall.door.width)+" =< CB"+str(j)+"X ; CB"+str(j)+"X + CB"+str(j)+"W =< "+str(hall.door.x)+") ; ("+str(hall.door.y + hall.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< CB"+str(j)+"Y ; CB"+str(j)+"Y + CB"+str(j)+"H =< "+str(hall.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Sofa x Sofa (basato su fake collision meter) --
        for i in range(0, sofaNumber):
            for j in range(i+1, sofaNumber):
                predicateBody += "{(SO"+str(i)+"X + SO"+str(i)+"W =< SO"+str(j)+"X - "+str(sofaDistanceThreshold*self.multiplier)+"; SO"+str(j)+"X + SO"+str(j)+"W =< SO"+str(i)+"X - "+str(sofaDistanceThreshold*self.multiplier)+") ; (SO"+str(i)+"Y + SO"+str(i)+"H =< SO"+str(j)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+"; SO"+str(j)+"Y + SO"+str(j)+"H =< SO"+str(i)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+")}, "

        # -- Sofa x Table --
        for j in range(0, sofaNumber):
            for i in range(0, tableNumber):
                predicateBody += "{(TA"+str(i)+"X + TA"+str(i)+"W + ChairSize =< SO"+str(j)+"X - "+str(sofaDistanceThreshold*self.multiplier)+"; SO"+str(j)+"X + SO"+str(j)+"W =< TA"+str(i)+"X - ChairSize - "+str(sofaDistanceThreshold*self.multiplier)+") ; (TA"+str(i)+"Y + TA"+str(i)+"H + ChairSize =< SO"+str(j)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+" ; SO"+str(j)+"Y + SO"+str(j)+"H =< TA"+str(i)+"Y - ChairSize - "+str(sofaDistanceThreshold*self.multiplier)+")}, "

        # -- Table x Door --
        for j in range(0, tableNumber):
            if hall.door.width == 0:
                predicateBody += "{("+str(hall.door.x + hall.door.width + self.doorFakeCollisionMeter*self.multiplier)+" =< TA"+str(j)+"X - ChairSize; TA"+str(j)+"X + TA"+str(j)+"W + ChairSize =< "+str(hall.door.x - self.doorFakeCollisionMeter*self.multiplier)+") ; ("+str(hall.door.y + hall.door.height)+" =< TA"+str(j)+"Y - ChairSize ; TA"+str(j)+"Y + TA"+str(j)+"H + ChairSize =< "+str(hall.door.y)+")}, "
            else:
                predicateBody += "{("+str(hall.door.x + hall.door.width)+" =< TA"+str(j)+"X - ChairSize; TA"+str(j)+"X + TA"+str(j)+"W + ChairSize =< "+str(hall.door.x)+") ; ("+str(hall.door.y + hall.door.height + self.doorFakeCollisionMeter*self.multiplier)+" =< TA"+str(j)+"Y - ChairSize ; TA"+str(j)+"Y + TA"+str(j)+"H + ChairSize =< "+str(hall.door.y - self.doorFakeCollisionMeter*self.multiplier)+")}, "

        # -- Cupboard x Table --
        for j in range(0, cupboardNumber):
            for i in range(0, tableNumber):
                predicateBody += "{(TA"+str(i)+"X + TA"+str(i)+"W + ChairSize =< CB"+str(j)+"X - "+str(sofaDistanceThreshold*self.multiplier)+"; CB"+str(j)+"X + CB"+str(j)+"W =< TA"+str(i)+"X - ChairSize - "+str(sofaDistanceThreshold*self.multiplier)+") ; (TA"+str(i)+"Y + TA"+str(i)+"H + ChairSize =< CB"+str(j)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+" ; CB"+str(j)+"Y + CB"+str(j)+"H =< TA"+str(i)+"Y - ChairSize - "+str(sofaDistanceThreshold*self.multiplier)+")}, "

        # -- Table x Table --
        for i in range(0, tableNumber):
            for j in range(i+1, tableNumber):
                predicateBody += "{(TA"+str(i)+"X + TA"+str(i)+"W + ChairSize*2 =< TA"+str(j)+"X - "+str(sofaDistanceThreshold*self.multiplier)+" ; TA"+str(j)+"X + TA"+str(j)+"W =< TA"+str(i)+"X - ChairSize*2 - "+str(sofaDistanceThreshold*self.multiplier)+") ; (TA"+str(i)+"Y + TA"+str(i)+"H + ChairSize*2 =< TA"+str(j)+"Y - "+str(sofaDistanceThreshold*self.multiplier)+" ; TA"+str(j)+"Y + TA"+str(j)+"H =< TA"+str(i)+"Y - ChairSize*2 - "+str(sofaDistanceThreshold*self.multiplier)+")}, "



        predicateBody = predicateBody[:-2]
        predicateBody += ", !"
        # no il punto . dopo il predicato

        # print(predicateHead + predicateBody)
        self.prolog.assertz(predicateHead + predicateBody)
        print("La query per la hall "+str(hall.index)+" è : " + predicateHead + predicateBody)
        for sol in self.prolog.query(query):
            for i in range(0, cupboardNumber):
                cupboardSprite = pygame.sprite.Sprite()
                cupboardSprite.image = self.WARDROBE_IMAGE
                spriteOrientation = "S"
                if cupboardInfo[i] == 2 or cupboardInfo[i] == 4:
                    cupboardSprite.image = pygame.transform.rotate(cupboardSprite.image, 90)
                    spriteOrientation = "E"
                cupboardSprite.image = pygame.transform.scale(cupboardSprite.image, (int(sol["CB"+str(i)+"W"]), int(sol["CB"+str(i)+"H"])))
                cupboardSprite.rect = pygame.Rect(sol["CB"+str(i)+"X"], sol["CB"+str(i)+"Y"], sol["CB"+str(i)+"W"], sol["CB"+str(i)+"H"])
                cupboard = Gameobject(sol["CB"+str(i)+"X"], sol["CB"+str(i)+"Y"], sol["CB"+str(i)+"W"], sol["CB"+str(i)+"H"], cupboardSprite, CUPBOARD)
                cupboard.orientation = spriteOrientation
                hall.children.append(cupboard)
            for i in range(0, sofaNumber):
                sofaSprite = pygame.sprite.Sprite()
                sofaSprite.image = self.SOFA_IMAGE
                spriteOrientation = "S"
                if sofaInfo[i] == 1:
                    sofaSprite.image = pygame.transform.rotate(sofaSprite.image, 90)
                    spriteOrientation = "E"
                elif sofaInfo[i] == 2:
                    sofaSprite.image = pygame.transform.rotate(sofaSprite.image, 180)
                    spriteOrientation = "N"
                elif sofaInfo[i] == 3:
                    sofaSprite.image = pygame.transform.rotate(sofaSprite.image, -90)
                    spriteOrientation = "W"
                sofaSprite.image = pygame.transform.scale(sofaSprite.image, (int(sol["SO"+str(i)+"W"]), int(sol["SO"+str(i)+"H"])))
                sofaSprite.rect = pygame.Rect(sol["SO"+str(i)+"X"], sol["SO"+str(i)+"Y"], sol["SO"+str(i)+"W"], sol["SO"+str(i)+"H"])
                sofa = Gameobject(sol["SO"+str(i)+"X"], sol["SO"+str(i)+"Y"], sol["SO"+str(i)+"W"], sol["SO"+str(i)+"H"], sofaSprite, SOFA)
                sofa.orientation = spriteOrientation
                hall.children.append(sofa)
            for i in range(0, tableNumber):
                tableSprite = pygame.sprite.Sprite()
                tableSprite.image = self.HALL_TABLE_IMAGE
                tableSprite.image = pygame.transform.scale(tableSprite.image, (int(sol["TA"+str(i)+"W"]), int(sol["TA"+str(i)+"H"])))
                tableSprite.rect = pygame.Rect(sol["TA"+str(i)+"X"], sol["TA"+str(i)+"Y"], sol["TA"+str(i)+"W"], sol["TA"+str(i)+"H"])
                table = Gameobject(sol["TA"+str(i)+"X"], sol["TA"+str(i)+"Y"], sol["TA"+str(i)+"W"], sol["TA"+str(i)+"H"], tableSprite, HALL_TABLE)
                for j in range(i*4, i*4+4):
                    chairSprite = pygame.sprite.Sprite()
                    chairSprite.image = self.CHAIR_IMAGE
                    chairSprite.image = pygame.transform.rotate(chairSprite.image, ((j+2) % 4)*(90))
                    chairSprite.image = pygame.transform.scale(chairSprite.image, (int(sol["C"+str(j)+"W"]), int(sol["C"+str(j)+"H"])))
                    chairSprite.rect = pygame.Rect(sol["C"+str(j)+"X"], sol["C"+str(j)+"Y"], sol["C"+str(j)+"W"], sol["C"+str(j)+"H"])
                    chair = Gameobject(sol["C"+str(j)+"X"], sol["C"+str(j)+"Y"], sol["C"+str(j)+"W"], sol["C"+str(j)+"H"], chairSprite, CHAIR)
                    if j == i*4:
                        chair.orientation = "S"
                    elif j == i*4+1:
                        chair.orientation = "E"
                    elif j == i*4 + 2:
                        chair.orientation = "N"
                    else:
                        chair.orientation = "W"
                    table.children.append(chair)
                hall.children.append(table)
        self.prolog.retract(predicateHead + predicateBody)

    def getHalls(self):
        results = []
        for x in (y for y in self.rooms if y.type == HALL):
            results.append(x)
        return results

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

