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


class Controller:
    def __init__(self):
        self.bodyID = -1
        self.maxBodyID = 1
        self.toggleDisplay = False

controller = Controller()


def on_key(window, key, scancode, action, mods):
    if action != glfw.PRESS:
        return

    global controller

    if key == glfw.KEY_ENTER:
        controller.toggleDisplay = not controller.toggleDisplay

    elif key == glfw.KEY_LEFT:
        if controller.bodyID >= controller.maxBodyID or controller.bodyID == -1:
            controller.bodyID = controller.maxBodyID - 1
        elif controller.bodyID < 0:
            controller.bodyID = controller.maxBodyID - 1
        else:
            controller.bodyID -= 1
    elif key == glfw.KEY_RIGHT:
        if controller.bodyID >= controller.maxBodyID or controller.bodyID == -1:
            controller.bodyID = 0
        elif controller.bodyID < 0:
            controller.bodyID = controller.maxBodyID - 1
        else:
            controller.bodyID += 1
    elif key == glfw.KEY_ESCAPE:
        sys.exit()


if __name__ == '__main__':
    # Initialize glfw
    if not glfw.init():
        sys.exit()
    width = 800
    height = 800
    proportion = width / height
    window = glfw.create_window(width, height, 'Sistema planetario 2D', None, None)
    if not window:
        glfw.terminate()
        sys.exit()
    glfw.make_context_current(window)
    glfw.set_key_callback(window, on_key)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Estableciendo color de pantalla
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Estableciendo pipelines
    texturePipeline = es.SimpleTextureTransformShaderProgram()
    bodiesPipeline = es.SimpleTransformShaderProgram()

    gpuBG = es.toGPUShape(bs.createTextureQuad('skybox.jpg'), GL_REPEAT, GL_NEAREST)
    gpuInfoTexture = es.toGPUShape(bs.createTextureQuad('planetInfo.jpg'), GL_REPEAT, GL_NEAREST)
    gpuFrameAnim = es.toGPUShape(bs.createTextureQuad('frameAnim.jpg'), GL_CLAMP_TO_EDGE, GL_NEAREST)
    gpuBars = es.toGPUShape(bs.createTextureQuad('bars.png'), GL_REPEAT, GL_NEAREST)
    gpuFigureAnim = es.toGPUShape(bs.createTextureQuad("frameAnim.jpg"), GL_REPEAT, GL_LINEAR)
    # Obteniendo información de bodies.json
    with open('bodies.json') as f:
        data = json.load(f)
    planetas = data[0]['Satellites']
    data[0]['Radius'] *= proportion
    gpuStar = es.toGPUShape(
        my.createCircle(15, data[0]['Color'][0], data[0]['Color'][1], data[0]['Color'][2], data[0]['Radius']))

    gpuSelectStar = es.toGPUShape(my.createCircle(15, 1, 1, 1, data[0]['Radius'] * 1.3))

    sceneText = sg.SceneGraphNode('infoStar')
    sceneText.childs += [gpuInfoTexture]

    sceneBars = sg.SceneGraphNode('bars')
    sceneBars.childs += [gpuBars]
    sceneSystemBars = sg.SceneGraphNode('systemBars')
    sceneSystemBars.childs += [sceneBars]

    sceneFrameAnim = sg.SceneGraphNode('frameAnim')
    sceneFrameAnim.childs += [gpuFrameAnim]

    sceneInfo = sg.SceneGraphNode('info')
    sceneInfo.childs += [sceneText,sceneFrameAnim,sceneSystemBars]

    sceneStar = sg.SceneGraphNode('star')
    sceneStar.childs += [gpuStar]
    sceneInfoBodies = sg.SceneGraphNode('infoBodies')
    sceneInfoBodies.childs += [sceneStar]
    bodyID = 1
    for planeta in planetas:
        planeta['bodyID'] = bodyID
        bodyID += 1

        planeta['angulo'] = np.random.uniform(-1, 1) * np.pi * 2

        # Almacenando figuras en memoria GPU
        r = planeta['Color'][0]
        g = planeta['Color'][1]
        b = planeta['Color'][2]
        planeta['Radius'] *= proportion
        planeta['Distance'] *= proportion
        planeta['posx'] = 0
        planeta['posy'] = 0
        gpuPlaneta = es.toGPUShape(my.createCircle(15, r, g, b, planeta['Radius']))
        planeta['GPUShape'] = gpuPlaneta

        #Trail de planeta
        gpuPlanetTrail = es.toGPUShape(my.createTrail(planeta['Distance'], 25))
        planeta['gpuTrail'] = gpuPlanetTrail

        #Selección de planeta
        gpuSelect = es.toGPUShape(my.createCircle(15, 1, 1, 1, planeta['Radius'] * 1.3))
        planeta['gpuSelect'] = gpuSelect

        sceneInfoPlanet = sg.SceneGraphNode('info')
        sceneInfoPlanet.childs += [gpuPlaneta]
        planeta['sceneInfo'] = sceneInfoPlanet
        sceneInfoBodies.childs += [sceneInfoPlanet]
        #Info de planeta
        #sceneInfoPlanet = sg.SceneGraphNode('infoPlaneta')
        #sceneInfoPlanet.childs += [gpuFigureAnim,gpuPlaneta]
        #planeta['sceneInfo'] = sceneInfoPlanet
        if planeta['Satellites'] != 'Null':
            # Creando sceneGraph de planeta
            scenePlanet = sg.SceneGraphNode('planet')
            scenePlanet.childs += [gpuPlaneta]
            planeta['sceneGraph'] = scenePlanet

            sceneSelectPlanet = sg.SceneGraphNode('selectPlanet')
            sceneSelectPlanet.childs += [gpuSelect]
            planeta['selectSceneGraph'] = sceneSelectPlanet

            # Creando sceneGraph de planeta + satelite
            system = sg.SceneGraphNode('system')
            system.childs += [sceneSelectPlanet, scenePlanet]
            for satelite in planeta['Satellites']:
                satelite['bodyID'] = bodyID
                bodyID += 1

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

                gpuSelect = es.toGPUShape(my.createCircle(15, 1, 1, 1, satelite['Radius'] * 1.3))
                satelite['gpuSelect'] = gpuSelect

                #Info de Satelite
                #sceneInfoSatellite = sg.SceneGraphNode('infoSatellite')
                #sceneInfoSatellite.childs += [gpuFigureAnim, gpuSatellite]
                #satelite['sceneInfo'] = sceneInfoSatellite

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

                # Creando sceneGraph de satelite select
                sceneSelectSatellite = sg.SceneGraphNode('selectSatellite')
                sceneSelectSatellite.childs += [gpuSelect]
                satelite['selectSceneGraph'] = sceneSelectSatellite
                system.childs += [sceneSelectSatellite, sceneSatellite]

                sceneInfoSatellite = sg.SceneGraphNode('infoSat')
                sceneInfoSatellite.childs += [gpuSatellite]
                satelite['sceneInfo'] = sceneInfoSatellite
                sceneInfoBodies.childs += [sceneInfoSatellite]
                
            planeta['systemSceneGraph'] = system
    controller.maxBodyID = bodyID
    t0 = glfw.get_time()
    cam_theta = 0
    camX = 0
    camY = 0
    zoom = 1
    i=0.05
    barsY = (1/proportion)*0.5

    while not glfw.window_should_close(window):
        glfw.poll_events()  # Se buscan eventos de entrada, mouse, teclado

        # Diferencia de tiempo con la iteración anterior
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camX -= 0.5 * dt

        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            camX += 0.5 * dt

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camY += 0.5 * dt

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camY -= 0.5 * dt

        if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
            zoom -= 0.5 * dt

        if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
            zoom += 0.5 * dt

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        # Se rellenan triangulos
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Textura de fondo
        glUseProgram(texturePipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                           tr.uniformScale(proportion * 2))
        texturePipeline.drawShape(gpuBG)

        glUseProgram(bodiesPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                           tr.matmul([tr.translate(camX * zoom, camY * zoom, 0), tr.uniformScale(zoom)]))
        if controller.bodyID == 0:
            bodiesPipeline.drawShape(gpuSelectStar)
        if controller.toggleDisplay and controller.bodyID==0:
            sceneStar.transform = tr.identity()
        else:
            sceneStar.transform = tr.uniformScale(0)

        bodiesPipeline.drawShape(gpuStar)

        for planeta in planetas:

            planeta['angulo'] += planeta['Velocity'] * dt
            planeta['posx'] = (planeta['Distance'] * np.cos(planeta['angulo'])) + camX
            planeta['posy'] = (planeta['Distance'] * np.sin(planeta['angulo'])) + camY

            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glUseProgram(bodiesPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                               tr.matmul([tr.translate(camX * zoom, camY * zoom, 0), tr.uniformScale(zoom)]))
            bodiesPipeline.drawShape(planeta['gpuTrail'])
            if planeta['Satellites'] != 'Null':
                for satelite in planeta['Satellites']:
                    satelite['angulo'] += satelite['Velocity'] * dt
                    satelite['posx'] = -np.cos(satelite['angulo']) * satelite['Distance']
                    satelite['posy'] = -np.sin(satelite['angulo']) * satelite['Distance']
                    satelite['systemTrailSceneGraph'].transform = tr.matmul(
                        [tr.translate(planeta['posx'] * zoom, planeta['posy'] * zoom, 0), tr.uniformScale(zoom)])
                    sg.drawSceneGraphNode(satelite['systemTrailSceneGraph'], bodiesPipeline, 'transform')

                    if controller.bodyID == satelite['bodyID']:
                        satelite['selectSceneGraph'].transform = tr.translate(satelite['posx'], satelite['posy'], 0)
                    else:
                        satelite['selectSceneGraph'].transform = tr.uniformScale(0)
                    if controller.toggleDisplay and controller.bodyID == satelite['bodyID']:
                        satelite['sceneInfo'].transform = tr.identity()
                    else:
                        satelite['sceneInfo'].transform = tr.uniformScale(0)

                    satelite['sceneGraph'].transform = tr.translate(satelite['posx'], satelite['posy'], 0)
                planeta['systemSceneGraph'].transform = tr.matmul(
                    [tr.translate(planeta['posx'] * zoom, planeta['posy'] * zoom, 0), tr.uniformScale(zoom)])
                if controller.bodyID == planeta['bodyID']:
                    planeta['selectSceneGraph'].transform = tr.identity()
                else:
                    planeta['selectSceneGraph'].transform = tr.uniformScale(0)
                if controller.toggleDisplay and controller.bodyID == planeta['bodyID']:
                    planeta['sceneInfo'].transform = tr.identity()
                else:
                    planeta['sceneInfo'].transform = tr.uniformScale(0)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                sg.drawSceneGraphNode(planeta['systemSceneGraph'], bodiesPipeline, 'transform')

            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                                   tr.matmul([tr.translate(planeta['posx'] * zoom, planeta['posy'] * zoom, 0),
                                              tr.uniformScale(zoom)]))
                if controller.bodyID == planeta['bodyID']:
                    bodiesPipeline.drawShape(planeta['gpuSelect'])
                if controller.toggleDisplay and controller.bodyID == planeta['bodyID']:
                    planeta['sceneInfo'].transform = tr.identity()
                else:
                    planeta['sceneInfo'].transform = tr.uniformScale(0)

                bodiesPipeline.drawShape(planeta['GPUShape'])
        if controller.toggleDisplay and controller.bodyID!=-1 and controller.bodyID!=controller.maxBodyID:
            if i>=0.3*proportion:
                i=-i
            i+=0.005
            glUseProgram(texturePipeline.shaderProgram)
            sceneBars.transform = tr.translate(proportion*0.5,0.5,0)
            sceneSystemBars.transform =tr.matmul([tr.translate(proportion*0.55,proportion*0.3,0),tr.scale(proportion*0.25,abs(i),0)])
            sceneFrameAnim.transform = tr.matmul( [tr.translate(0.5 * proportion, 0.35 * proportion, 0),tr.uniformScale(proportion/1.5)])
            sceneText.transform = tr.matmul([tr.translate(0.5*proportion,-0.35*proportion,0),tr.uniformScale(proportion/1.5)])
            sg.drawSceneGraphNode(sceneInfo, texturePipeline, 'transform')

            glUseProgram(bodiesPipeline.shaderProgram)
            sceneInfoBodies.transform = tr.matmul([tr.translate(proportion*0.35,proportion*0.4 , 0),
                                          tr.uniformScale(proportion*1.01)])
            sg.drawSceneGraphNode(sceneInfoBodies,bodiesPipeline,'transform')
        # if controller.bodyID == 0:
        #     glUseProgram(bodiesPipeline.shaderProgram)
        #     glUniformMatrix4fv(glGetUniformLocation(bodiesPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
        #                        tr.matmul([tr.translate(proportion*0.35,proportion*0.4 , 0),
        #                                   tr.uniformScale(proportion*1.01)]))
        #     bodiesPipeline.drawShape(gpuStar)

        glfw.swap_buffers(window)

    glfw.terminate()
