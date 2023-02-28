import math
import pygame

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
                print("activation avoidance")
        if self.agent.sprite.rect.colliderect(self.objective.sprite.rect):
            self.resetObjective()
            score += 1
        pygame.display.update()
        clock.tick(100)
        frames -= 1
        if frames == 0:
            running = False
            print((f"score achieved: {str(score)}" ))
    pygame.quit()    
