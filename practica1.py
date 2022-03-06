#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 10:38:28 2022

@author: mat
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import Array
import random


N = 10 #numero de elementos que produce cada productor
NPROD = 3 #numero de productores que hay
NCONS = 1 #numero de consumidores 

def productor(l_semaforos, buffer, idx):
    v=0
    for i in range(N):
        v+=random.randint(0,5) #creamos elemento 
        l_semaforos[2*idx].acquire() # wait nonEmpty
        buffer[idx] =v #añadimos el elemento al buffer 
        l_semaforos[2*idx+1].release() # signal empty 
    v=-1
    l_semaforos[2*idx].acquire() # wait nonEmpty
    buffer[idx] =v  #añadimos el elemento -1 al buffer para indicar que no se va a producir mas 
    l_semaforos[2*idx+1].release()  # signal empty 
    

def no_menos_1(n):
    if n!=-1:
        return True
    else:
        return False
   
def minimo(buffer):
    l2 = filter(no_menos_1, buffer) #filtramos la lista para eliminar los -1
    minimo = min (l2) #tomamos el minimo de la lista filtrada
    
    for i in range (len(buffer)): #recorremos la lista para encontrar el indice donde se encuentra el minimo
        if buffer[i] == minimo:
            return minimo,i


def consumidor(l_semaforos, buffer):
    nums =[]
    for i in range(NPROD): #recorre la lista de semáforos de los productores
        l_semaforos[2*i+1].acquire() # wait nonEmpty
        
    while [-1]*NPROD != list(buffer): #mientras que el buffer sea distinto a la lista formada
                                        #por -1, los productores no habrán terminado de producir
        
        v, index = minimo(buffer)  #tomamos el elemento mínimo del buffer
        print('añade el número:', v, 'de Productor', index)  
        nums.append(v)     #añadimos el mínimo a la lista nums del consumidor 
        print (f"numeros del consumidor: {nums}")   
        #ajustamos los semaforos del elemento tomado del buffer
        l_semaforos[2*index].release() # signal empty   
        l_semaforos[2*index + 1].acquire() # wait nonEmpty
    
    print ('La lista final de numeros del consumidor es:', nums)
   



def main():
    buffer = Array('i',NPROD)   #creamos un array de tamaño igual al numero de productores 
    
    l_semaforos = [] #creamos una lista donde almacenar los semáforos 2 por productor
    for i in range(0,NPROD):    #uno para indicat empty y otro para indicar non empty
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(1)
        l_semaforos.append(empty)
        l_semaforos.append(non_empty)
    l_productores = [ Process(target = productor,   #creamos una lista de procesos de los productores 
                       name=f'prod_{i}', 
                       args=(l_semaforos,buffer,i))
                    for i in range (NPROD)]
    cons = Process(target = consumidor, args = (l_semaforos,buffer))  #creamos el proceso consumidor
    
    
    for p in l_productores: 
         p.start()
    cons.start() 
    for p in l_productores:
        p.join()
    cons.join()


if __name__ == "__main__":
 main()    
        




        
        
        
        
        
        
    
    
    
    
    
    