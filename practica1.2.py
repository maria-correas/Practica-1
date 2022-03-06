#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 22:01:57 2022

@author: mat
"""


from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import Array
import random


N = 3 #numero de elementos que produce cada productor
NPROD = 5 #numero de productores que hay
NCONS = 1 #numero de consumidores 
K=2


def minimo(lista):
    minimo = lista[0]
    idx = 0
    aux = [lista[K*i] for i in range(NPROD)]

    for i in range(0,len(aux)):
        if aux[i]!=-1:
            minimo = aux[i]
            idx = i
            break
    for i in range(0,len(aux)):
        if(aux[i]<minimo and aux[i]!=-1):
            minimo = aux[i]
            idx = i
    return minimo,idx
    


def add_data(buffer, mutex, n_elementos, index, data):
    mutex.acquire() 
    try:
        buffer[K*index + n_elementos[index]] = data
        n_elementos[index]+=1
        print('añade', list(buffer))
    finally:
        mutex.release() 


def get_data(buffer, mutex, n_elementos, nums):
    mutex.acquire()
    try:
        data, index = minimo(buffer)
        nums.append(data)
        for i in range(n_elementos[index] - 1):
            buffer[index*K + i] = buffer[index*K + (i+1)]
        n_elementos[index] -= 1 
    finally:
        mutex.release() 
    return data, index


  
 
def productor(l_semaforos, mutex, buffer, idx, n_elementos):
    v=0
    for i in range(N):
        v+=random.randint(0,5) #creamos elemento 
        print('productor:', idx, 'iteracion:', i, 'valor:', v)
        l_semaforos[2*idx].acquire() # wait nonEmpty
        add_data(buffer, mutex, n_elementos, idx, v)#añadimos el elemento al buffer 
        l_semaforos[2*idx+1].release() # signal empty 
    v=-1
    l_semaforos[2*idx].acquire() # wait nonEmpty
    add_data(buffer, mutex, n_elementos, idx, v) #añadimos el elemento -1 al buffer para indicar que no se va a producir mas 
    l_semaforos[2*idx+1].release()  # signal empty 
    


    
def consumidor(l_semaforos, mutex, buffer, n_elementos):
    nums =[]
    for i in range(NPROD): #recorre la lista de semáforos de los productores
        l_semaforos[2*i+1].acquire() # wait nonEmpty
        
    while [-1]*(NPROD*K) != [buffer[i] for i in range(0,len(buffer))]: #mientras que el buffer sea distinto a la lista formada
                                        #por -1, los productores no habrán terminado de producir
        data, index= get_data(buffer, mutex, n_elementos, nums)
        #ajustamos los semaforos del elemento tomado del buffer
        l_semaforos[2*index].release() # signal empty   
        l_semaforos[2*index + 1].acquire() # wait nonEmpty
    
    print ('La lista final de numeros del consumidor es:', nums)
   


def main():
    buffer = Array('i',NPROD*K)    
    n_elementos = Array('i', NPROD)
    
    l_semaforos = [] #creamos una lista donde almacenar los semáforos 2 por productor
    for i in range(0,NPROD):    #uno para indicat empty y otro para indicar non empty
        empty = BoundedSemaphore(K)
        non_empty = Semaphore(0)
        l_semaforos.append(empty)
        l_semaforos.append(non_empty) 
    mutex = Lock() 
    lp = []
    for index in range(NPROD):
         lp.append(Process(target=productor, args=(l_semaforos, mutex, buffer, index, n_elementos)))
    lp.append(Process(target=consumidor, args=(l_semaforos, mutex, buffer, n_elementos)))    
    for p in lp:
         p.start()
    for p in lp:
         p.join()
    
   


if __name__ == "__main__":
 main()    
        

