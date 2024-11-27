
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objeto3D import *

import numpy as np

o:Objeto3D
d:Objeto3D
morph:Objeto3D

transformacao_iniciada:bool = False




def init():
    global o, d, morph, camera_pos, camera_focus, camera_up

    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    camera_pos = [-1.24711209, 4.51113749, -11.04963121]
    camera_focus = [0, 0, 0]
    camera_up = [0, 1, 0]


    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    origin_name = 'models/hard3.obj'
    dest_name = 'models/easy3.obj'

    o = Objeto3D()
    o.LoadFile(origin_name)

    d = Objeto3D()
    d.LoadFile(dest_name)

    morph = Objeto3D()
    morph.LoadFile(origin_name)

    DefineLuz()
    PosicUser()


def DefineLuz():
    # Define cores para um objeto dourado
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.9, 0.9, 0.9]
    posicao_luz = [2.0, 3.0, 0.0]  # PosiÃ§Ã£o da Luz
    especularidade = [1.0, 1.0, 1.0]

    # ****************  Fonte de Luz 0

    glEnable(GL_COLOR_MATERIAL)

    #Habilita o uso de iluminaÃ§Ã£o
    glEnable(GL_LIGHTING)

    #Ativa o uso da luz ambiente
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    # Define os parametros da luz nÃºmero Zero
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)

    # Ativa o "Color Tracking"
    glEnable(GL_COLOR_MATERIAL)

    # Define a reflectancia do material
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)

    # Define a concentraÃ§Ã£oo do brilho.
    # Quanto maior o valor do Segundo parametro, mais
    # concentrado serÃ¡ o brilho. (Valores vÃ¡lidos: de 0 a 128)
    glMateriali(GL_FRONT, GL_SHININESS, 51)

def PosicUser():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Configura a matriz da projeção perspectiva (FOV, proporção da tela, distância do mínimo antes do clipping, distância máxima antes do clipping
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    gluPerspective(70, 16/9, 0.01, 50)  # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #Especifica a matriz de transformação da visualização
    # As três primeiras variáveis especificam a posição do observador nos eixos x, y e z
    # As três próximas especificam o ponto de foco nos eixos x, y e z
    # As três últimas especificam o vetor up
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    #gluLookAt(-2, 8, -12, 0, 7, 0, 0, 1.0, 0)

    #glRotatef(angulo_rotacao, 0, 1, 0)

    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
        camera_focus[0], camera_focus[1], camera_focus[2],
        camera_up[0], camera_up[1], camera_up[2])

def DesenhaLadrilho():
    glColor3f(0.5, 0.5, 0.5)  # desenha QUAD preenchido
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)  # desenha a borda da QUAD
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def DesenhaPiso():
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            DesenhaLadrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

def DesenhaCubo():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslated(0, 0.5, 0)
    glutSolidCube(1)

    glColor3f(0.5, 0.5, 0)
    glTranslated(0, 0.5, 0)
    glRotatef(90, -1, 0, 0)
    glRotatef(45, 0, 0, 1)
    glutSolidCone(1, 1, 4, 4)
    glPopMatrix()


def desenha(obj:Objeto3D, d:Objeto3D = None):
    def des():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)

        DesenhaPiso()
        #DesenhaCubo()    
        obj.Desenha()
        obj.DesenhaWireframe()
        obj.DesenhaVertices()
        if d != None:
            d.DesenhaVertices(1,0,0)
        glutSwapBuffers()
    return des

    

radius = 12.0 # distancia
theta = 4.5  # lado
phi = np.pi / 4 + 0.4 # cima e baixo

def update_camera_position():
    global camera_pos, camera_focus, radius, theta, phi
    camera_pos = np.array([
        radius * np.sin(phi) * np.cos(theta),
        radius * np.cos(phi),
        radius * np.sin(phi) * np.sin(theta)
    ])
    
    print(f"Posicao camera: {camera_pos}")
    
    

def teclado(key, x, y):


    global transformacao_iniciada, morph, d, radius, theta, phi

    if transformacao_iniciada == False and key == b' ': #inicia transformacao
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(350, 550)
        windowsMorph = glutCreateWindow('Trabalho 2 - CG - Morph')
        init()
        glutDisplayFunc(desenha(morph))
        
        
        morph.Transforma(d)
        glutKeyboardFunc(teclado)
        
        transformacao_iniciada = True
        return
    
    
    #movimento camera
    passo = 0.1 
    passo_zoom = 0.5

    if key == b'w':  # Zoom in
        radius -= passo_zoom
    elif key == b's':  # Zoom out
        radius += passo_zoom
    elif key == b'a':  # direita
        theta -= passo
    elif key == b'd':  # esquerda
        theta += passo
    elif key == b'q':  # cima
        phi -= passo
    elif key == b'e':  # baixo
        phi += passo

    phi = np.clip(phi, 0.01, np.pi - 0.01)

    update_camera_position()

            
    PosicUser()
        

    if key == b'+': #aproxima
        passo = (max(len(d.faces), len(o.faces)) - min(len(d.faces), len(o.faces))) * 0.00005
        morph.Aproxima(d, passo)    
    
    glutPostRedisplay()
    pass


def main():
    global o, d, morph

    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)



    glutInitWindowSize(640, 480)
    glutInitWindowPosition(100, 50)
    window1 = glutCreateWindow('Trabalho 2 - CG - obj1')
    init()
    glutDisplayFunc(desenha(o))


    glutInitWindowSize(640, 480)
    glutInitWindowPosition(800, 50)
    window2 = glutCreateWindow('Trabalho 2 - CG - obj2')
    init()
    glutDisplayFunc(desenha(d))

    

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)
    
    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()