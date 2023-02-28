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

    print(("Predicete to generate bedroom "+str(bedroom.index)+" è:"))
    print((predicateHead + predicateBody))
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

