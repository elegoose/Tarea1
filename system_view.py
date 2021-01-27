import glfw
from OpenGL.GL import *
import sys
import scene_graph as sg
import numpy as np
import my_shapes as my
import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import json



def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return
    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 900
    height = 900
    proportion = width / height
    window = glfw.create_window(width, height, 'Sistema planetario 2D', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    texturePipeline = es.SimpleTextureTransformShaderProgram()
    planetsPipeline = es.SimpleTransformShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    #Distancia de planeta al centro
    R = 0.5

    #Distancia de satelite al centro
    r_sat = 2

    #Distancia entre planeta y satelite
    R_orbita_sat = r_sat - R

    # Creando figuras en la memoria de la GPU
    gpuBG = es.toGPUShape(bs.createTextureQuad('skybox.jpg'),GL_REPEAT, GL_NEAREST) #Background
    gpuSun = es.toGPUShape(my.createCircle(15,1,1,0))

    gpuPlanet = es.toGPUShape(my.createCircle(15,1,0,0))
    gpuSatellite = es.toGPUShape(my.createCircle(15,0,1,0))

    gpuPlanetTrail = es.toGPUShape(my.createTrail(R,25))
    gpuSatelliteTrail = es.toGPUShape(my.createTrail(R_orbita_sat,25))

    #SceneGraph orbitas
    #planetOrbit = sg.SceneGraphNode('planetOrbit')
    #planetOrbit.childs += [gpuPlanetTrail]

    satelliteOrbit = sg.SceneGraphNode('satelliteOrbit')
    satelliteOrbit.childs += [gpuSatelliteTrail]
    satelliteOrbit.transform = tr.matmul([tr.uniformScale(proportion * 0.05),tr.translate(0, proportion*2, 0)])

    #Ensamblando SceneGraph
    systemOrbit = sg.SceneGraphNode('systemOrbit')
    systemOrbit.childs += [satelliteOrbit]

    #SceneGraph Planet+Satellite test
    planet = sg.SceneGraphNode('planet')
    planet.childs += [gpuPlanet]
    R_planet = 0.1
    planet.transform = tr.uniformScale(proportion * R_planet)

    satellite = sg.SceneGraphNode('satellite')
    satellite.childs += [gpuSatellite]
    satellite.transform = tr.matmul([tr.uniformScale(proportion * 0.05),tr.translate(0, proportion*2, 0)])

    #Ensamblando SceneGraph
    system = sg.SceneGraphNode('system')
    system.childs += [planet,satellite]

    #Creando un nodo de sceneGraph
    # planet = sg.SceneGraphNode('planet')
    # movingPlanet = sg.SceneGraphNode('movingPlanet')
    # bg = sg.SceneGraphNode('background')
    #Escalando figura
    # planet.transform = tr.uniformScale(0.5)
    # planet.childs += [gpuPlanet]
    #
    # bg.transform = tr.uniformScale(2.2)
    # bg.childs += [gpuBG]

    t0 = glfw.get_time()
    angulo=0
    angulo_satellite=0
    while not glfw.window_should_close(window):
        glfw.poll_events()  # Se buscan eventos de entrada, mouse, teclado

        # Diferencia de tiempo con la iteración anterior
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        #Se rellenan triangulos
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #Textura de fondo
        glUseProgram(texturePipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, 'transform'), 1, GL_TRUE, tr.uniformScale(proportion*2))
        texturePipeline.drawShape(gpuBG)


        #Planetas

        angulo += 1 * dt
        posx = R * np.cos(angulo)
        posy = R * np.sin(angulo)

        angulo_satellite += 2 * dt
        posx_sat = -np.cos(angulo_satellite) * r_sat
        posy_sat = -np.sin(angulo_satellite) * r_sat

        glUseProgram(planetsPipeline.shaderProgram)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glUniformMatrix4fv(glGetUniformLocation(planetsPipeline.shaderProgram, 'transform'), 1, GL_TRUE,tr.identity())
        planetsPipeline.drawShape(gpuPlanetTrail)

        satelliteOrbit.transform = tr.uniformScale(proportion * R_planet/R_orbita_sat)
        systemOrbit.transform = tr.translate(posx, posy, 0)
        sg.drawSceneGraphNode(systemOrbit,planetsPipeline,'transform')

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        satellite.transform = tr.matmul([tr.uniformScale(proportion * 0.05),tr.translate(posx_sat, posy_sat, 0)])
        system.transform=tr.translate(posx, posy, 0)
        sg.drawSceneGraphNode(system,planetsPipeline,'transform')


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()
