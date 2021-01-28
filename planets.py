import numpy as np
import json
import my_shapes as my
import easy_shaders as es
from OpenGL.GL import *
import transformations as tr
import scene_graph as sg
class Planet:
    def __init__(self,planetData,proportion = 800/800):
        self.proportion = proportion

        #Diccionario con información del planeta
        self.planetData = planetData
        self.r = self.planetData["Color"][0]
        self.g = self.planetData["Color"][1]
        self.b = self.planetData["Color"][2]

        self.radius = self.planetData["Radius"]

        self.distance = self.planetData["Distance"]

        self.velocity = self.planetData["Velocity"]

        self.satellites = self.planetData["Satellites"]

        self.satelliteArray = self.getSatellites()
        # Generando posición aleatoria
        self.angle = np.random.uniform(-1, 1) * np.pi * 2
        self.posx = self.radius * np.cos(self.angle)
        self.posy = self.radius * np.sin(self.angle)

        self.GPUShape = self.toGPUShape()

        self.sceneGraph = self.sceneGraphSystem()


    def hasSatellites(self):
        if self.satellites  == "Null":
            return False
        else:
            return True

    def getSatellites(self):
        satelliteArray = []
        if self.hasSatellites():
            for satellite in self.satellites:
                satelliteArray.append(Satellite(satellite,self.planetData))
        return satelliteArray

    def toGPUShape(self):
        return es.toGPUShape(my.createCircle(15, self.r, self.g, self.b))

    def setProportion(self,proportion):
        self.proportion = proportion

    def sceneGraphSystem(self):
        planet = sg.SceneGraphNode('planet')
        planet.childs += [self.GPUShape]
        planet.transform = tr.uniformScale(self.proportion * self.radius)
        sceneGraphSatellites = []
        i=0
        for satellite in self.satelliteArray:
            sceneGraphSatellites.append(sg.SceneGraphNode('satellite'))
            sceneGraphSatellites[i].childs += [satellite.GPUShape]

        # Ensamblando SceneGraph
        system = sg.SceneGraphNode('system')
        system.childs = [planet]
        for sceneGraphSatellite in sceneGraphSatellites:
            system.childs += [sceneGraphSatellite]
        return system

    def drawSystem(self,pipeline):
        for satellite in self.satelliteArray:
            print(self.sceneGraph.childs[0].name)
            self.sceneGraph.childs[0].transform = tr.matmul([tr.uniformScale(self.proportion * 0.05), tr.translate(satellite.posx, satellite.posy, 0)])
        self.sceneGraph.transform = tr.translate(self.posx, self.posy, 0)
        sg.drawSceneGraphNode(self.sceneGraph, pipeline, 'transform')

    def update(self,dt):
        self.angle += self.velocity * dt
        self.posx = self.distance * np.cos(self.angle)
        self.posy = self.distance * np.sin(self.angle)
        for satellite in self.satelliteArray:
            satellite.update(dt)



class planetTrail:
    def __init__(self,Planet):
        self.radius = Planet.distance
        self.GPUShape = self.toGPUShape()

    def toGPUShape(self):
        return es.toGPUShape(my.createTrail(self.radius,30))

    def draw(self,pipeline,gpuPlanetTrail):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'transform'), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(gpuPlanetTrail)

class satelliteTrail:
    def __init__(self,Planet):
        self.planetData = Planet
        self.orbitRadiusArray = []
        for satellite in Planet.satelliteArray:
            self.orbitRadiusArray.append(satellite.distance)
        self.planetRadius = Planet.radius
        self.orbitScaleValueArray = []
        for orbitRadius in self.orbitRadiusArray:
            self.orbitScaleValueArray.append(self.planetRadius/orbitRadius)
        self.proportion = Planet.proportion
        self.GPUShapeArray = self.toGPUShape()
        self.sceneGraphArray = self.sceneGraph()
    def toGPUShape(self):
        shapesArray = []
        for orbitRadius in self.orbitRadiusArray:
            shapesArray.append(es.toGPUShape(my.createTrail(orbitRadius,30)))
        return shapesArray

    def sceneGraph(self):
        systemOrbitArray = []
        for gpuSatelliteTrail in self.GPUShapeArray:
            satelliteOrbit = sg.SceneGraphNode('satelliteOrbit')
            satelliteOrbit.childs += [gpuSatelliteTrail]
            systemOrbit = sg.SceneGraphNode('systemOrbit')
            systemOrbit.childs += [satelliteOrbit]
            systemOrbitArray.append(systemOrbit)
        return systemOrbitArray
    def draw(self,systemOrbitArray,pipeline):
        i=0
        for systemOrbit in systemOrbitArray:
            systemOrbit.childs[0].transform = tr.uniformScale(self.proportion *self.orbitScaleValueArray[i])
            systemOrbit.transform = tr.translate(self.planetData.posx,self.planetData.posy,0)
            sg.drawSceneGraphNode(systemOrbit,pipeline,'transform')
            i+=1



class Satellite:
    def __init__(self,satelliteData,planetData):
        self.satelliteData = satelliteData
        self.parent = planetData
        # Generando posición aleatoria
        self.angle = np.random.uniform(-1, 1) * np.pi * 2

        self.r = self.satelliteData["Color"][0]
        self.g = self.satelliteData["Color"][1]
        self.b = self.satelliteData["Color"][2]

        self.radius = self.satelliteData["Radius"]

        self.distance = self.satelliteData["Distance"]

        self.velocity = self.satelliteData["Velocity"]

        self.satellites = self.satelliteData["Satellites"]

        self.satelliteArray = self.getSatelliteArray()

        self.GPUShape = self.toGPUShape()

        self.posx = -np.cos(self.angle) * self.distance
        self.posy = -np.sin(self.angle) * self.distance
    def hasSatellites(self):
        if self.satellites  == "Null":
            return False
        else:
            return False

    def getSatelliteArray(self):
        satelliteArray = []
        if self.hasSatellites():
            for satellite in self.satellites:
                satelliteArray.append(Satellite(satellite,self.parent))
        return satelliteArray

    def toGPUShape(self):
        return es.toGPUShape(my.createCircle(15, self.r,self.g,self.b))

    def update(self,dt):
        self.angle += self.velocity * dt
        self.posx = -np.cos(self.angle) * self.distance
        self.posy = -np.sin(self.angle) * self.distance



def getStarData(file):
    star = 0
    with open(file) as f:
        starData = json.load(f)
    return starData[star]

def getPlanetArray(file):
    star = 0
    with open(file) as f:
        planetData = json.load(f)
    planetArray = []
    for planet in planetData[star]['Satellites']:
        print(planet['Color'])
        planetArray.append(Planet(planet))
    return planetArray



