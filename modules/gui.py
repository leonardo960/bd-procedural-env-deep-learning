import pygame
from guizero import App, ListBox, PushButton, Box, Text, info, Slider

from os import listdir
from os.path import isfile, join


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

def testGuizero(self):
    app = App(title="Procedural Environment Neuro-symbolic Agent", width = 800, height = 600)

    menuBox = Box(app, layout="grid", width=800, height=250)
    def goToSightEnvironments_cmd():
        menuBox.hide()
        vistaAmbientiBox.show()
    def goToSightGeneration_cmd():
        menuBox.hide()
        vistaGenerazioneAmbientiBox.show()
        generazioneAmbientiBox1.show()
        generazioneAmbientiBox2.show()
        generazioneAmbientiButtonBox.show()
    def goToTrainAgent_cmd():
        menuBox.hide()
        vistaAddestramentoBox.show()
            
    Box(menuBox, height=50, width=800, grid=[0,0])
    Box(menuBox, height=20, grid=[0,2])
    Box(menuBox, height=20, grid=[0,4])
    PushButton(menuBox, command=goToSightEnvironments_cmd, text="Visualize environments generated", width=30, height=1, grid=[0, 1])
    PushButton(menuBox, command=goToSightGeneration_cmd, text="Generate new environments", width=30, height=1, grid=[0, 3])
    PushButton(menuBox, command=goToTrainAgent_cmd, text="Train the Agent", width=30, height=1, grid=[0, 5])

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
    PushButton(visualizzaButtonBox, command=visualizza_cmd, text = "Visualize", grid=[0,0])
    PushButton(visualizzaButtonBox, command=vistaAmbientiBack_cmd, text="Back", grid=[1,0])

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
        info("Use the Generator", "- During the environments generation, press key \n'S' to save an environment and generate the next.\n\n- Press key 'N' to generate a new environment\n discrding the previous.\n\n- Close PyGame to comeback to the menu.")
        #avvia generazione ambienti
        self.generateEnvironment(self.sliderBAR.value, self.sliderBR.value, self.sliderKI.value, self.sliderHA.value)
        self.drawModel()
        self.displayEnvironment(mode="generate")

    Box(vistaGenerazioneAmbientiBox, height=40, grid=[0,0])
    Text(generazioneAmbientiBox1, text="Number of bedrooms:", grid=[0,0], size=10, bg=LIGHT_GREEN)
    self.sliderBR = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,0])
    self.sliderBR.__setattr__("bg", LIGHT_GREEN)

    Text(generazioneAmbientiBox2, text="MAX beds:", grid=[0,0], size=10, bg=LIGHT_GREEN)
    self.sliderBR_B = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,0])
    Text(generazioneAmbientiBox2, text="MAX cabinets:", grid=[0,1], size=10, bg=LIGHT_GREEN)
    self.sliderBR_W = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,1])

    Box(generazioneAmbientiBox1, height=40, grid=[0,1])

    Text(generazioneAmbientiBox1, text="Number of bathrooms:", grid=[0,2], size=10, bg=PINK)
    self.sliderBAR = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,2])
    self.sliderBAR.__setattr__("bg", PINK)
    Text(generazioneAmbientiBox2, text="MAX water:", grid=[0,2], size=10, bg=PINK)
    self.sliderBAR_T = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,2])
    Text(generazioneAmbientiBox2, text="MAX showers:", grid=[0,3], size=10, bg=PINK)
    self.sliderBAR_S = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,3])
    Text(generazioneAmbientiBox2, text="MAX sinks:", grid=[0,4], size=10, bg=PINK)
    self.sliderBAR_SI = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,4])

    Box(generazioneAmbientiBox1, height=40, grid=[0,3])

    Text(generazioneAmbientiBox1, text="Number of kitchens:", grid=[0,4], size=10, bg=BANANA)
    self.sliderKI = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,4])
    self.sliderKI.__setattr__("bg", BANANA)

    Text(generazioneAmbientiBox2, text="MAX tables:", grid=[0,5], size=10, bg=BANANA)
    self.sliderKI_KTA = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,5])
    Text(generazioneAmbientiBox2, text="MAX banconies:", grid=[0,6], size=10, bg=BANANA)
    self.sliderKI_D = Slider(generazioneAmbientiBox2, horizontal=True, end=3, grid=[1,6])

    Box(generazioneAmbientiBox1, height=40, grid=[0,5])

    Text(generazioneAmbientiBox1, text="Numero halls:", grid=[0,6], size=10, bg=ORANGE)
    self.sliderHA = Slider(generazioneAmbientiBox1, horizontal=True, end=2, grid=[1,6])
    self.sliderHA.__setattr__("bg", ORANGE)

    Text(generazioneAmbientiBox2, text="MAX tables:", grid=[0,7], size=10, bg=ORANGE)
    self.sliderHA_HT = Slider(generazioneAmbientiBox2, horizontal=True, end=1, grid=[1,7])
    Text(generazioneAmbientiBox2, text="MAX divani:", grid=[0,8], size=10, bg=ORANGE)
    self.sliderHA_SO = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,8])
    Text(generazioneAmbientiBox2, text="MAX scaffali:", grid=[0,9], size=10, bg=ORANGE)
    self.sliderHA_CB = Slider(generazioneAmbientiBox2, horizontal=True, end=2, grid=[1,9])

    Box(vistaGenerazioneAmbientiBox, height=40, grid=[0,2])

    PushButton(generazioneAmbientiButtonBox, command=generate_cmd, text = "Generate Environments", grid=[0,0])
    PushButton(generazioneAmbientiButtonBox, command=vistaGenerazioneAmbientiBack_cmd, text = "Back", grid=[1,0])

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
    PushButton(visualizzaButtonBox2, command=addestra_cmd, text = "Train", grid=[0,0])
    PushButton(visualizzaButtonBox2, command=vistaAddestramentoBack_cmd, text="Back", grid=[1,0])
        
    app.display()
