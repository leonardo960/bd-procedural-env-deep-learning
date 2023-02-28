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

    print("The predicate to generate the bathroom is: ")
    print((predicateHead + predicateBody))
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


