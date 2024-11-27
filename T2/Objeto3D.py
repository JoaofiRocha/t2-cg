from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *
import random
remover_vertices = True
class Event:
    def __init__(self, time: float,index, executed: bool = False):
        self.time = time
        self.index = index
        self.executed = executed
    def should_execute(self, current_time):
        if self.executed:
            return False
        if current_time >= self.time:
            self.executed = True
            return True
        return False

class Face:
    # preciso que cada face tenha o controle de vertices que devem ser removidos e adicionados. Cada face deve ter uma timeline de eventos 
    def __init__(self, vertices: list, active: bool = True):
        self.active = active
        self.vertices = vertices
        self.target_vertices = []
        self.centroid = None

    def print(self):
        print(f'Face:')
        for v in self.vertices:
            print(f'{v.x} {v.y} {v.z}')

    def activate(self):
        self.active = True
    
    def deactivate(self):
        print(f"Desativando face com {len(self.vertices)} vértices")
        self.active = False
        self.vertices = []


    def set_dest(self, dest):
        self.target_vertices = [Ponto(v.x, v.y, v.z) for v in dest.vertices]
        
        # Ensure the number of vertices is the same
        while len(self.target_vertices) < len(self.vertices):
            self.target_vertices.append(Ponto(self.target_vertices[-1].x, self.target_vertices[-1].y, self.target_vertices[-1].z))
        
        while len(self.vertices) < len(self.target_vertices):
            self.vertices.append(Ponto(self.vertices[-1].x, self.vertices[-1].y, self.vertices[-1].z))
        
        self.update_centroid()

    def update_centroid(self):
        x = sum([v.x for v in self.vertices]) / len(self.vertices)
        y = sum([v.y for v in self.vertices]) / len(self.vertices)
        z = sum([v.z for v in self.vertices]) / len(self.vertices)
        self.centroid = Ponto(x, y, z)
        return self.centroid
    
    def move_to_dest(self,passo):
        for i in range(len(self.vertices)):
            self.vertices[i].x += (self.target_vertices[i].x - self.vertices[i].x) * passo
            self.vertices[i].y += (self.target_vertices[i].y - self.vertices[i].y) * passo
            self.vertices[i].z += (self.target_vertices[i].z - self.vertices[i].z) * passo

        self.update_centroid()
        pass

class Objeto3D:
        
    def __init__(self):
        self.faces    = []
        self.position = Ponto(0,0,0)
        self.rotation = (0,0,0,0)
        self.vertices_dest = []
        self.vertices = []
        self.events = []
        self.morph_timeline = 0
        self.max_timeline = 0
        pass

    def LoadFile(self, file:str):
        f = open(file, "r")

        lines = f.readlines()
        vertices = []

        # leitor de .obj baseado na descrição em https://en.wikipedia.org/wiki/Wavefront_.obj_file    
        for line in lines:
            values = line.split(' ')
            # dividimos a linha por ' ' e usamos o primeiro elemento para saber que tipo de item temos
            if values[0] == 'v': 
                # item é um vértice, os outros elementos da linha são a posição dele
                vertices.append(Ponto(float(values[1]),
                                           float(values[2]),
                                           float(values[3])))
                # adicionamos o vértice à lista de vértices
                self.vertices.append(Ponto(float(values[1]),
                                           float(values[2]),
                                           float(values[3])))
        for line in lines:
            values = line.split(' ')
            if values[0] == 'f':
                # item é uma face, os outros elementos da linha são dados sobre os vértices dela
                self.faces.append(Face([]))
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    # dividimos cada elemento por '/'
                     
                    vertice = vertices[int(fInfo[0]) - 1]
                    self.faces[-1].vertices.append(Ponto(vertice.x,vertice.y,vertice.z)) # primeiro elemento é índice do vértice da face
                    # ignoramos textura e normal
                
            # ignoramos outros tipos de items, no exercício não é necessário e vai só complicar mais
        for face in self.faces:
            face.update_centroid()
        pass

    def DesenhaVertices(self, r=.1,g=.1,b=.8):
        if remover_vertices:
            return
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(r,g,b)
        glPointSize(8)

        glBegin(GL_POINTS)
        for f in self.faces:
            if f.active:
                for v in f.vertices: 
                    glVertex(v.x, v.y, v.z)
        glEnd()
        
        glPopMatrix()
        pass

    def DesenhaWireframe(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)        
        
        for f in self.faces:
            glBegin(GL_LINE_LOOP)
            if f.active:   
                for v in f.vertices:
                    glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass

    def Desenha(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_TRIANGLE_FAN)
            if f.active:
                for v in f.vertices:
                    glVertex(v.x, v.y, v.z)
                    
            glEnd()
            
        
        glPopMatrix()
        pass


    def Transforma(self, dest):
        timeline = 0
        # calculo dos centroides das faces de destino
        print(f"FacesAtivas : {len([f for f in self.faces if f.active])} Dest: {len(dest.faces)}")
        dest_centroids = [f.update_centroid() for f in dest.faces if f.active]
        dest_centroids_idxs = [i for i in range(len(dest_centroids))] 

            # verificar numero faces
        for i in range(0, max(len(dest.faces), len(self.faces))):
            # se obj atual tem menos faces que dest
            if i > len(self.faces) - 1:
                # adicionar nova face inativa e evento de ativação
                random_face = self.faces[random.randint(0, len(self.faces) - 1)]
                new_face = Face([Ponto(v.x, v.y, v.z) for v in random_face.vertices],True)
                self.faces.append(new_face)
                self.events.append(Event(timeline,i))
                timeline += 1
                print(f"Adicionado face {i} inativa para ser ativada em {timeline}")

            # atribui faces no destino, a partir da face mais proxima baseada no centroide
            if len(dest_centroids) > 0:
                _, dest_idx = self.faces[i].update_centroid().closest_point(dest_centroids)
                self.faces[i].set_dest(dest.faces[dest_centroids_idxs[dest_idx]])

                #remove pra evitar duplicatas
                del dest_centroids[dest_idx]
                del dest_centroids_idxs[dest_idx]
            else:
                random_face = dest.faces[random.randint(0, len(dest.faces) - 1)]
                new_face = Face([Ponto(v.x, v.y, v.z) for v in random_face.vertices])
                self.faces[i].set_dest(new_face)
                #evento de remoção de face para destino repetido
                self.events.append(Event(timeline,i))
                timeline += 1
                print(f"Adicionando evento de remoção em {timeline} para face {i} ativa")

        self.max_timeline = timeline


    def Aproxima(self,dest,passo):
        active_faces = len([f for f in self.faces if f.active])
        print(f"Faces Ativas: {active_faces} Dest: {len(dest.faces)}, Timeline: {self.morph_timeline} MaxTimeline: {self.max_timeline} Vertices: {len([v for f in self.faces for v in f.vertices])} Vertices Dest: {len([v
         for f in dest.faces for v in f.vertices])}")
        # if self.morph_timeline >= self.max_timeline:
        #     return
        # pra cada face ativa, move ela pro destino
        for i in range(len(self.faces)):
            if self.faces[i].active:
                self.faces[i].move_to_dest(passo)

        # pra cada evento que ta programado pra executar (criados la no transforma)
        for e in [e for e in self.events if e.should_execute(self.morph_timeline)]:

            # se o num de faces do destino é MAIOR que o num de faces ativas no obj atual
            if len(dest.faces) > active_faces:
                # acionar face
                self.faces[e.index].activate()

            #se o num de faces do destino é MENOR que o num de faces ativas no obj atual
            elif len(dest.faces) < active_faces:
                # remover faces
                print(f"Desativando face {e.index}")
                self.faces[e.index].deactivate()
            print(f"Vertices: {len([v for f in self.faces for v in f.vertices])} Vertices Dest: {len([v for f in dest.faces for v in f.vertices ])}")

            
        
        self.morph_timeline += 10


