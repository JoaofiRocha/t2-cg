from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *
import random

class Event:
    def __init__(self, time: float, executed: bool = False):
        self.time = time
        self.executed = executed

class Face:
    def __init__(self, vertices: list):
        self.vertices = vertices
        self.centroid = None
        self.dest = None

    def print(self):
        print(f'Face:')
        for v in self.vertices:
            print(f'{v.x} {v.y} {v.z}')

    def update_centroid(self):
        x = sum([v.x for v in self.vertices]) / len(self.vertices)
        y = sum([v.y for v in self.vertices]) / len(self.vertices)
        z = sum([v.z for v in self.vertices]) / len(self.vertices)
        self.centroid = Ponto(x, y, z)
        return self.centroid
    
    def move_to_dest(self,passo):
        if self.dest == None:
            return
        for i in range(len(self.vertices)):
            closest,_ = self.vertices[i].closest_point([v for v in self.dest.vertices])
            self.vertices[i].x += (closest.x - self.vertices[i].x) * passo
            self.vertices[i].y += (closest.y - self.vertices[i].y) * passo
            self.vertices[i].z += (closest.z - self.vertices[i].z) * passo

        self.update_centroid()
        pass

class Objeto3D:
        
    def __init__(self):
        self.faces    = []
        self.position = Ponto(0,0,0)
        self.rotation = (0,0,0,0)
        self.vertices_dest = []
        self.events = []
        self.morph_timeline = 0
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
        for line in lines:
            values = line.split(' ')
            if values[0] == 'f':
                # item é uma face, os outros elementos da linha são dados sobre os vértices dela
                self.faces.append(Face([]))
                for fVertex in values[1:]:
                    fInfo = fVertex.split('/')
                    # dividimos cada elemento por '/'
                    verticeIdx = int(fInfo[0]) - 1
                    self.faces[-1].vertices.append(vertices[verticeIdx]) # primeiro elemento é índice do vértice da face
                    # ignoramos textura e normal
                
            # ignoramos outros tipos de items, no exercício não é necessário e vai só complicar mais
        for face in self.faces:
            face.update_centroid()
        pass

    def DesenhaVertices(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(self.rotation[3], self.rotation[0], self.rotation[1], self.rotation[2])
        glColor3f(.1, .1, .8)
        glPointSize(8)

        glBegin(GL_POINTS)
        for f in self.faces:
            glVertex(f.centroid.x, f.centroid.y, f.centroid.z)
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
            for v in f.vertices:
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()
        pass


    def Transforma(self, dest):
        print(f"Faces: {len(self.faces)} Dest: {len(dest.faces)}")
        dest_centroids = [f.update_centroid() for f in dest.faces]
        for i,c in enumerate(dest_centroids):
            print(f"Centroid {i}: {c.x} {c.y} {c.z}")  
        for i in range(0, len(self.faces)):
             #busca o centriode da face dest mais proximo
            
            _, dest_idx = self.faces[i].update_centroid().closest_point(dest_centroids)
            self.faces[i].dest = dest.faces[dest_idx]
            print(f"Face {i} mais proxima: {dest_idx}. Dest:{self.faces[i].dest.centroid.x} {self.faces[i].dest.centroid.y} {self.faces[i].dest.centroid.z} Orig: {self.faces[i].centroid.x} {self.faces[i].centroid.y} {self.faces[i].centroid.z}")



        # if len(dest.vertices)>len(self.vertices):
        #     self.vertices = self.vertices + [ random.choice(self.vertices) for _ in range(len(dest.vertices) - len(self.vertices))]

        # events_amount = max(len(dest.faces), len(self.faces))
        # interval = 100 / events_amount
        # for dest_idx in range(events_amount):
        #     event_time = dest_idx * interval
        #     event = Event(event_time)
        #     self.events.append(event)
        
        # vertices_cpy = dest.vertices.copy()
        # for origin_idx, v in enumerate(self.vertices):
        #     closest, dest_idx = v.closest_point(vertices_cpy)
        #     if dest_idx == None:
        #         dest_idx = random.randint(0, len(dest.vertices) - 1)
        #         closest = dest.vertices[dest_idx]
        #     else:
        #         del vertices_cpy[dest_idx]
                
        #     self.vertices_dest.append(closest)
        #     self.original_idxs.append(dest_idx)

        #     # no caso do tamanho de vertices do destino ser maior vai ter que inverter a chave
        #     k,v=0,0
        #     if len(self.vertices) > len(dest.vertices):
        #         k,v = dest_idx,origin_idx
        #     else:
        #         k,v = origin_idx,dest_idx


        #     if k not in self.rotas:
        #         self.rotas[k] = []
        #     self.rotas[k].append(v)
  
        # print(f"Vertices: {len(self.vertices)} CPY: {len(vertices_cpy)}")
        pass

    def mapFaces(self, face):
        return [self.original_idxs[i] for i in face]


    def AtualizaFaces(self,dest,index):

        pass


    def Aproxima(self,dest,passo):
        print(f"Faces: {len(self.faces)} Dest: {len(dest.faces)}")
        for i in range(len(self.faces)):
            self.faces[i].move_to_dest(passo)
        # print(f'Events {len([event for event in self.events if event.executed == False])}')
        # print(f"Timeline: {self.morph_timeline}")
        # print(f"Vertices: {len(self.vertices)} Dest: {len(dest.vertices)} VD: {len(self.vertices_dest)}")
        # print(f"Faces: {len(self.faces)} Dest: {len(dest.faces)}")
        # #verifica se tem evento
        # for index, event in enumerate(self.events):
        #     if self.morph_timeline >= event.time and event.executed == False:
        #         self.AtualizaFaces(dest,index)
        #         event.executed = True
        #         break
        # for i in range(0, len(self.vertices)):
        #     destPoint = self.vertices_dest[i]
        #     originPoint = self.vertices[i]

        #     if originPoint == destPoint:
        #         print(f"Vertice {i} já chegou no destino")
        #         continue
        #     if abs(destPoint.x - originPoint.x) < 0.01 and abs(destPoint.y - originPoint.y) < 0.01 and abs(destPoint.z - originPoint.z) < 0.01:
        #         self.vertices[i] = destPoint
        #     else:
        #         self.vertices[i].x += (destPoint.x - originPoint.x) * passo
        #         self.vertices[i].y += (destPoint.y - originPoint.y) * passo
        #         self.vertices[i].z += (destPoint.z - originPoint.z) * passo
        
        # self.morph_timeline += 1
        pass


