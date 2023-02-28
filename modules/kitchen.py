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
    print((predicateHead + predicateBody))
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
