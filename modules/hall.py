import random
import pygame
from modules.utils import Vertex, Gameobject, Agent, Room

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
    print(("La query per la hall "+str(hall.index)+" è : " + predicateHead + predicateBody))
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
