import numpy
import pygame
from SLAMRobot import SLAMAgent


def runTraining(self):
    state_size = 40
    slamAgent = SLAMAgent(state_size, 3)
    #slamAgent.load("test", 0.19) 
    speed = 2
    #frames = 1500
    #frames = 3000
    #frames = 4500
    frames = 6000
    #for i in range(1,10001): #10k episodi
    for i in range(1,101): #1k episodi
        self.screen = pygame.display.set_mode((int(self.env_width), int(self.env_height)))
        #pygame.init()
        #self.reset()
        #self.generateEnvironment(2, 2, 2, 2)
        #self.drawModel()
        #pygame.display.set_caption("Agent Training Episode {}/{}".format(i,10000))
        done = False
        frameCount = 0
        self.reset_agent()
        self.reset_objective()
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
                self.draw_model()
                pygame.display.update()
                if self.isAgentColliding():
                    currentMinDistance = state[0][0][1]
                    print(f"len(state[0]): {str(len(state[0]))}")
                    for k in range(len(state[0])):
                        if state[0][k][1] < currentMinDistance and not state[0][k][2]:
                            print(f"state[0][k][1]: {str(state[0][k][1])}")
                            currentMinDistance = state[0][k][1]
                    print(("currentMinDistance: " + str(currentMinDistance)))
                    print(("distanze: " + str(state)))
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
                    self.reset_objective()
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
        print(("Episod {}/{}: end frame {}/{}, score: {}, random: {}%".format(i,10000,frameCount,frames, score, int((randomActions * 100)/frameCount))))
        print("Start replay agent.")
        slamAgent.replay(500)
        print("Replay agent completed.")
    print("Saving weights...")
    slamAgent.save("test")
    print("Weights saved.")
    pygame.quit()
        
