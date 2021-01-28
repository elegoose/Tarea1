import glfw
from OpenGL.GL import *
import sys
import scene_graph as sg
import numpy as np

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import json

SIZE_IN_BYTES = 4
class GPUShape:
    vao = 0
    vbo = 0
    ebo = 0
    size = 0


def createCircle(N,r,g,b):
    # Here the new shape will be stored
    gpuShape = GPUShape()

    # First vertex at the center, white color
    vertices = [0, 0, 0, r, g, b] #Primer vertice
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,

            r,g,b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i + 1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    return bs.Shape(vertices,indices)

def createTrail(radio,N,r,g,b):
    length=radio
    # First vertex at the center, white color
    #vertices = [0, 0, 0, r, g, b]  # Primer vertice
    vertices =[]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            radio * np.cos(theta), radio * np.sin(theta), 0,

            # color generates varying between 0 and 1
            r, g, b]

        # A triangle is created using the center, this and the next vertex
        if i==0:
            indices+=[0,0,1]
        elif i == N - 1:
            pass
        else:
            indices += [i,i,i+1]

    #Uniendo circunferencia
    indices+=[N-1,N-1,0]

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    return bs.Shape(vertices, indices)


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

    window = glfw.create_window(width, height, 'Sistema planetario 2D', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    texturePipeline = es.SimpleTextureTransformShaderProgram()
    planetsPipeline = es.SimpleTransformShaderProgram()
    #pipeline = es.SimpleShaderProgram()
    # Telling OpenGL to use our shader program
    #glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Creando figuras en la memoria de la GPU
    gpuBG = es.toGPUShape(bs.createTextureQuad('skybox.jpg'),GL_REPEAT, GL_NEAREST) #Background
    gpuPlanet = es.toGPUShape(createCircle(15,1,1,0))
    gpuMovingPlanet = es.toGPUShape(createCircle(15,1,0,0))
    gpuPlanetTrail = es.toGPUShape(createTrail(0.5,25,0.91,0.93,0.85))

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
    x=0
    y=0
    angulo=0
    proportion = width/height
    R = 0.5
    while not glfw.window_should_close(window):
        glfw.poll_events()  # Se buscan eventos de entrada, mouse, teclado

        # Diferencia de tiempo con la iteración anterior
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        #Textura de fondo
        glUseProgram(texturePipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, 'transform'), 1, GL_TRUE, tr.uniformScale(proportion*2))
        texturePipeline.drawShape(gpuBG)

        angulo += 2*dt
        posx = R * np.cos(angulo)
        posy = R * np.sin(angulo)

        #Planetas
        glUseProgram(planetsPipeline.shaderProgram)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glUniformMatrix4fv(glGetUniformLocation(planetsPipeline.shaderProgram, 'transform'), 1, GL_TRUE,
                           tr.identity())
        planetsPipeline.drawShape(gpuPlanetTrail)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glUniformMatrix4fv(glGetUniformLocation(planetsPipeline.shaderProgram, 'transform'), 1, GL_TRUE,tr.matmul([tr.translate(posx, posy, 0), tr.uniformScale(proportion*0.05)]))
        planetsPipeline.drawShape(gpuMovingPlanet)
        # sg.drawSceneGraphNode(bg,texturePipeline,'transform')
        #glUseProgram(planetsPipeline.shaderProgram)
        # sg.drawSceneGraphNode(planet, planetsPipeline, 'transform')


        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()