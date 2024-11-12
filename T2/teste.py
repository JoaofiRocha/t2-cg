
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objeto3D import *

o:Objeto3D

def init():
    global o
    glClearColor(0.5, 0.5, 0.9, 1.0)
    glClearDepth(1.0)

    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    o = Objeto3D()
    o.LoadFile('untitled.obj')

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
    gluPerspective(60, 16/9, 0.01, 50)  # Projecao perspectiva
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #Especifica a matriz de transformação da visualização
    # As três primeiras variáveis especificam a posição do observador nos eixos x, y e z
    # As três próximas especificam o ponto de foco nos eixos x, y e z
    # As três últimas especificam o vetor up
    # https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    gluLookAt(-2, 6, -8, 0, 0, 0, 0, 1.0, 0)


def calcular_centroide(vertices, face):
    x = sum(vertices[i][0] for i in face) / len(face)
    y = sum(vertices[i][1] for i in face) / len(face)
    z = sum(vertices[i][2] for i in face) / len(face)
    return (x, y, z)

def associar_faces_varios_para_um(vertices1, faces1, vertices2, faces2):
    associacoes = []
    centroides1 = [calcular_centroide(vertices1, face) for face in faces1]
    centroides2 = [calcular_centroide(vertices2, face) for face in faces2]
    
    # Caso 1-1: número igual de triângulos nos dois objetos
    if len(faces1) == len(faces2):
        for i in range(len(faces1)):
            associacoes.append((i, i))  # Associação 1-1
    elif len(faces1) < len(faces2):
        # Mais triângulos no Objeto 2
        num_associacoes = len(faces2) // len(faces1)
        sobra = len(faces2) % len(faces1)

        for i, c1 in enumerate(centroides1):
            # Associa múltiplos triângulos de faces2 para cada face de faces1
            for j in range(num_associacoes + (1 if i < sobra else 0)):
                index = i * num_associacoes + j + min(i, sobra)
                associacoes.append((i, index))
    else:
        # Mais triângulos no Objeto 1, associando o contrário
        num_associacoes = len(faces1) // len(faces2)
        sobra = len(faces1) % len(faces2)

        for j, c2 in enumerate(centroides2):
            for i in range(num_associacoes + (1 if j < sobra else 0)):
                index = j * num_associacoes + i + min(j, sobra)
                associacoes.append((index, j))
                
    return associacoes


def interpolar_vertices(vertices1, vertices2, t):
    """Interpola os vértices de vertices1 para vertices2 com um fator t (0 a 1)."""
    return [(v1[0] * (1 - t) + v2[0] * t,
             v1[1] * (1 - t) + v2[1] * t,
             v1[2] * (1 - t) + v2[2] * t) for v1, v2 in zip(vertices1, vertices2)]

def DesenhaMorph(obj1, obj2, t):
    """Desenha a interpolação entre obj1 e obj2, com base no fator t."""
    associacoes = associar_faces_varios_para_um(obj1.vertices, obj1.faces, obj2.vertices, obj2.faces)
    
    # Para cada par de faces associadas, faça a interpolação
    for i, j in associacoes:
        vertices1 = [obj1.vertices[idx] for idx in obj1.faces[i]]
        vertices2 = [obj2.vertices[idx] for idx in obj2.faces[j]]
        
        # Interpolação entre as faces associadas
        vertices_morfados = interpolar_vertices(vertices1, vertices2, t)
        
        # Desenhe a face interpolada
        glBegin(GL_POLYGON)
        for vertice in vertices_morfados:
            glVertex3fv(vertice)
        glEnd()


t = 0.0  # Fator de morphing inicial
direcao = 0.01  # Controle de incremento para t

def atualizaMorph(value):
    global t, direcao
    t += direcao
    if t >= 1.0 or t <= 0.0:
        direcao = -direcao  # Inverte a direção da interpolação

    glutPostRedisplay()
    glutTimerFunc(16, atualizaMorph, 0)

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

def desenha():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    DesenhaPiso()
    #DesenhaCubo()    
    o.Desenha()
    o.DesenhaWireframe()
    o.DesenhaVertices()

    DesenhaMorph(o1, o2, t)

    glutSwapBuffers()
    pass

def teclado(key, x, y):
    o.rotation = (1, 0, 0, o.rotation[3] + 2)    

    glutPostRedisplay()
    pass

def main():

    glutInit(sys.argv)

    # Define o modelo de operacao da GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)



    glutInitWindowSize(640, 480)
    glutInitWindowPosition(100, 50)
    window1 = glutCreateWindow('Trabalho 2 - CG - obj1')
    init()
    glutDisplayFunc(desenha)


    glutInitWindowSize(640, 480)
    glutInitWindowPosition(800, 50)
    window2 = glutCreateWindow('Trabalho 2 - CG - obj2')
    init()
    glutDisplayFunc(desenha)



    glutInitWindowSize(640, 480)
    glutInitWindowPosition(350, 600)
    windowsMorph = glutCreateWindow('Trabalho 2 - CG - Morph')
    init()
    glutDisplayFunc(desenha)



    # Registra a funcao callback de redesenho da janela de visualizacao
    

    # Registra a funcao callback para tratamento das teclas ASCII
    glutKeyboardFunc(teclado)

    try:
        # Inicia o processamento e aguarda interacoes do usuario
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()