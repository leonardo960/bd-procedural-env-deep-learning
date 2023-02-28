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
    door = Gameobject(0, 0, 0, 0, 0, "door")

    def __init__(self, x, y, width, height, index, sprite, type):
        Gameobject.__init__(self, x, y, width, height, sprite, type)
        self.index = index
        