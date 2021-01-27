import numpy as np
import json
import my_shapes as my
import easy_shaders as es
from OpenGL.GL import *
import transformations as tr
class Planet:
    def __init__(self,planetData):
        #Diccionario con información del planeta
        self.planetData = planetData

        self.r = self.planetData["Color"][0]
        self.g = self.planetData["Color"][1]
        self.b = self.planetData["Color"][2]

        self.radius = self.planetData["Radius"]

        self.distance = self.planetData["Distance"]

        self.velocity = self.planetData["Velocity"]

        self.satellites = self.planetData["Satellites"]

        # Generando posición aleatoria
        self.initial_angle = np.random.uniform(-1, 1) * np.pi * 2
        self.posx = self.radius * np.cos(self.initial_angle)
        self.posy = self.radius * np.sin(self.initial_angle)

    def hasSatellites(self):
        if self.satellites  == "Null":
            return False
        else:
            return True

    def getSatellites(self):


    def toGPUShape(self):
        es.toGPUShape(my.createCircle(15, self.r, self.g, self.b))

class planetTrail:
    def __init__(self,Planet):
        self.radius = Planet.distance

    def toGPUShape(self):
        es.toGPUShape(my.createTrail(self.radius,30))

    def draw(self,pipeline,gpuPlanetTrail):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'transform'), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(gpuPlanetTrail)

class satelliteTrail:
    def __init__(self,Satellite):
        self.a = Satellite.satelliteData



class Satellite:
    def __init__(self,satelliteData):
        self.satelliteData = satelliteData

        # Generando posición aleatoria
        self.initial_angle = np.random.uniform(-1, 1) * np.pi * 2

        self.r = self.satelliteData["Color"][0]
        self.g = self.satelliteData["Color"][1]
        self.b = self.satelliteData["Color"][2]

        self.radius = self.satelliteData["Radius"]

        self.distance = self.satelliteData["Distance"]

        self.velocity = self.satelliteData["Velocity"]

        self.satellites = self.satelliteData["Satellites"]

    def hasSatellites(self):
        if self.satellites  == "Null":
            return False
        else:
            return False

    def getSatellites(self):
        satelliteArray = []
        if self.hasSatellites():
            for satellite in self.satellites:
                satelliteArray.append(satellite)
        return satelliteArray



def getStarData(file):
    star = 0
    with open(file) as f:
        starData = json.load(f)
    return starData[star]

def getBodyArray(file):
    star = 0
    with open(file) as f:
        bodyData = json.load(f)
    bodyArray = []
    for body in bodyData[star]:
        bodyArray.append(body)

def getPlanetAndSatellites(bodyArray):
    systemArray = []
    systemDictionary = []
    for body in bodyArray:
        planet = Planet(body)

        if planet.hasSatellites():
            satellites = Satellite(planet.satellites)


