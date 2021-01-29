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
    glfw.set_key_callback(window, on_key)
    # Estableciendo color de pantalla
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Estableciendo pipelines
    backgroundPipeline = es.SimpleTextureTransformShaderProgram()
    bodiesPipeline = es.SimpleTransformShaderProgram()

    gpuBG = es.toGPUShape(bs.createTextureQuad('skybox.jpg'), GL_REPEAT, GL_NEAREST)

    # Obteniendo información de bodies.json
    with open('bodies.json') as f:
        data = json.load(f)
    planetas = data[0]['Satellites']
    data[0]['Radius'] *= proportion
    gpuStar = es.toGPUShape(
        my.createCircle(15, data[0]['Color'][0], data[0]['Color'][1], data[0]['Color'][2], data[0]['Radius']))

    for planeta in planetas:
        planeta['angulo'] = np.random.uniform(-1, 1) * np.pi * 2

        # Almacenando figuras en memoria GPU
        r = planeta['Color'][0]
        g = planeta['Color'][1]
        b = planeta['Color'][2]
        planeta['Radius'] *= proportion
        planeta['Distance'] *= proportion
        gpuPlaneta = es.toGPUShape(my.createCircle(15, r, g, b, planeta['Radius']))
        planeta['GPUShape'] = gpuPlaneta

        gpuPlanetTrail = es.toGPUShape(my.createTrail(planeta['Distance'], 25))
        planeta['gpuTrail'] = gpuPlanetTrail

        if planeta['Satellites'] != 'Null':
            # Creando sceneGraph de planeta
            scenePlanet = sg.SceneGraphNode('planet')
            scenePlanet.childs += [gpuPlaneta]
            planeta['sceneGraph'] = scenePlanet

            # Creando sceneGraph de planeta + satelite
            system = sg.SceneGraphNode('system')
            system.childs += [scenePlanet]
            for satelite in planeta['Satellites']:
                satelite['angulo'] = np.random.uniform(-1, 1) * np.pi * 2
                # Almacenando figuras en memoria GPU
                r = satelite['Color'][0]
                g = satelite['Color'][1]
                b = satelite['Color'][2]
                satelite['Radius'] *= proportion
                satelite['Distance'] *= proportion
                gpuSatellite = es.toGPUShape(my.createCircle(15, r, g, b, satelite['Radius']))
                satelite['GPUShape'] = gpuSatellite

                gpuSatelliteTrail = es.toGPUShape(my.createTrail(satelite['Distance'], 25))
                satelite['gpuTrail'] = gpuSatelliteTrail

                # Creando sceneGraph de trail del Satelite
                satelliteOrbit = sg.SceneGraphNode('satelliteOrbit')
                satelliteOrbit.childs += [gpuSatelliteTrail]
                satelite['trailSceneGraph'] = satelliteOrbit
                # Ensamblando SceneGraph de orbita
                systemOrbit = sg.SceneGraphNode('systemOrbit')
                systemOrbit.childs += [satelliteOrbit]
                satelite['systemTrailSceneGraph'] = systemOrbit

                # Creando sceneGraph de satelite
                sceneSatellite = sg.SceneGraphNode('satellite')
                sceneSatellite.childs += [gpuSatellite]
                satelite['sceneGraph'] = sceneSatellite

                system.childs += [sceneSatellite]
            planeta['systemSceneGraph'] = system
    t0 = glfw.get_time()
    while not glfw.window_should_close(window):
        glfw.poll_events()  # Se buscan eventos de entrada, mouse, teclado

        # Diferencia de tiempo con la iteración anterior
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        # Se rellenan triangulos
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        # Textura de fondo
        glUseProgram(backgroundPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(backgroundPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                           tr.uniformScale(proportion * 2))
        backgroundPipeline.drawShape(gpuBG)

        glUseProgram(bodiesPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                           tr.identity())
        bodiesPipeline.drawShape(gpuStar)

        for planeta in planetas:
            planeta['angulo'] += planeta['Velocity'] * dt
            planeta['posx'] = planeta['Distance'] * np.cos(planeta['angulo'])
            planeta['posy'] = planeta['Distance'] * np.sin(planeta['angulo'])
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glUseProgram(bodiesPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                               tr.identity())
            bodiesPipeline.drawShape(planeta['gpuTrail'])
            if planeta['Satellites'] != 'Null':
                for satelite in planeta['Satellites']:
                    satelite['angulo'] += satelite['Velocity'] * dt
                    satelite['posx'] = -np.cos(satelite['angulo']) * satelite['Distance']
                    satelite['posy'] = -np.sin(satelite['angulo']) * satelite['Distance']
                    satelite['systemTrailSceneGraph'].transform = tr.translate(planeta['posx'], planeta['posy'], 0)
                    sg.drawSceneGraphNode(satelite['systemTrailSceneGraph'], bodiesPipeline, 'transform')

                    satelite['sceneGraph'].transform = tr.translate(satelite['posx'], satelite['posy'], 0)

                planeta['systemSceneGraph'].transform = tr.translate(planeta['posx'], planeta['posy'], 0)

                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                sg.drawSceneGraphNode(planeta['systemSceneGraph'], bodiesPipeline, 'transform')
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                                   tr.translate(planeta['posx'], planeta['posy'], 0))
                bodiesPipeline.drawShape(planeta['GPUShape'])
        glfw.swap_buffers(window)

    glfw.terminate()
