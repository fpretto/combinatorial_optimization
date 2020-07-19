import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, 'C:/Repo/Github/combinatorial_optimization/pickers_simulation/')
from PickersData import PickersData
import random
import statistics
import pandas as pd


##################### Funciones dadas ######################
def get_pdf(data):
	# Dado un vector con muestras de una variable, retorna dos listas con los valores (a intervalos de 1) y su correspondiente frecuencia de ocurrencia
	bins = range(1, int(max(data)+1))
	count, _ = np.histogram(data, bins=bins)
	probs = count / sum(count)
	return bins,probs

def get_pdf(data):
	""" Dado un vector con muestras de una variable, retorna dos listas con los valores (a intervalos de 1) y su correspondiente frecuencia de ocurrencia"""
	bins = range(1, int(max(data) + 2))
	count, bin_edges = np.histogram(data, bins=bins)
	probs = count / sum(count)
	return bin_edges[:-1], probs

def get_cdf(probs):
	''' Dado un vector con probabilidades (pdf), retorna un vector de la misma dimension con la cdf. Probs puede ser la lista probs que retorna
	get_pdf.'''
	return np.cumsum(probs)

def get_picker(pickers_stat):
	''' Dada una lista con el tiempo en que cada picker termina su orden actual, devuelve el indice (i.e., picker) que termina primero'''
	return pickers_stat.index(min(pickers_stat)) 

def analyze_results(total_times,total_revs):
	''' Fucion que concentra el analisis de los resultados para un determinado escenario y con una cantidad de pickers dada.
	@param total_times: lista (de float) que en la posicion i tiene tiempo total de ejecutar la i-esima simulacion.
	@param total_revs: lista (de float) que en la posicion i tiene el revenue total reolectado para la i-esima simulacion.'''

	prob_completed = get_prob_completed(total_times,3600)
	times = statistics.mean(total_times)
	revs = statistics.mean(total_revs)
    
	print('Completados en 60 mins:', prob_completed)
	print('Tiempo promedio:', times)
	print('Rev. promedio:', revs)

	# Convertimos a minutos para agrupar.
	total_times_mins = [int(i/60.0) for i in total_times]
	b = range(max(total_times_mins) + 1) 

	# Cuando querramos graficar, descomentamos.
	#plt.hist(total_times_mins, bins = b, density=True)
	#plt.show()

	#plt.hist(total_times_mins, bins = b, density=True, cumulative=True)
	#plt.show()
	return prob_completed, times, revs

def get_prob_completed(times, value):
	success = [t for t in times if t <= value]
	return len(success)/len(times)

############################################################

def simulate_uniform(a,b):
	''' Simula una Unif(a,b). Debe convertir el resultado a un int'''
	return int(round(a + (b-a)*random.random()))

def simulate_empirical(vals, cumprobs):
	# Genera un numero aleatorio en base a una distribucion empirica usando el metodo de la transformada inversa.
	# @param vals: posibles valores de la distribucion
	# @param cumprobs: probabilidades acumuladas (cdf) para cada valor en vals.
	# @return valor v (perteneciente a vals) generado aleatoriamente
	i = 0 # Asignamos i = 1 para comenzar la iteración
	numero_random = random.random() # Generamos un número random entre 0 y 1
	while cumprobs[i] < numero_random: # Mientras el número random generado sea mayor que la probabilidad acumulada
		i = i + 1 # Sumamos 1 para continuar con la iteración
	valor = vals[i] # Asignamos el valor final en la variable 'valor'
	return valor
	# TESTEAR FUNCION
	
def generate_orders(n_orders, items_vals, items_cumprobs):
	# Simula la cantidad de items que tendra cada orden. La idea es usar la funcion simulate_empirical. Para eso, recibe:
	# @param n_orders: cuantas ordenes deben ser generadas.
	# @param items_vals: posibles valores para la cantidad de items de una orden.
	# @param items_cumprobs: probabilidades acumuladas para cada valor en items_vals.
	# @return lista de n_orders elementos, donde cada posicion tiene un int generado aleatoriamente siguiendo la distribucion (items_vals, items_probs)
	resultado = [] # Generamos una lista vacia donde vamos a ir cargando los valores
	for i in range (n_orders): # Desde 0 hasta el número establecido en n_orders
		valor = simulate_empirical(items_vals, items_cumprobs) # Simulamos un valor en base a la distribucion de items
		resultado.append(valor) # Lo agregamos en la lista generada anteriormente
	return resultado # Devolvemos la lista resultado



def simulate_order_time(n_items, picker, pickers_dist):
	#Simulamos el tiempo que le lleva a un picker procesar una determinada orden. Recordar que una orden esta definida por el numero de items
	#que tiene, y que cada picker tiene su propia distribucion de tiempos de inter-picks.
	#@param n_items: cantidad de items del picker.
	#@param picker: id (0 a 9) del picker que atiende la orden.
	#@param pickers_dist: diccionario con la info de todos los pickers.
	#@return float con el tiempo total de procesar la orden, que consiste en la suma de los tiempos inter-picks entre ordenes.
	#Ayuda: en pickers_dist, para acceder a los tiempos y probs. acumuladas del picker se puede hacer:
	#	pickers_dist[picker]['times']
	#	pickers_dist[picker]['cumprobs']
	sumatoria = float() # Definimos al tiempo de la orden como un float
	for i in range(n_items): # Desde 0 hasta el número establecido en n_items
		valores = pickers_dist[picker]['times'] # Guardamos en la variable valores los tiempos de determinado picker
		probabilidad_acumulada = pickers_dist[picker]['cumprobs'] # Guardamos en la variable probabilidad_acumulada la probabilidad acumulada de los tiempos guardados anteriormente
		resultado = simulate_empirical(valores, probabilidad_acumulada) # Simulamos cuanto va a demorar determinado picker en agarrar ese item
		sumatoria = sumatoria + resultado # Vamos sumando los tiempos que demora en agarrar todos los items
	return sumatoria # Devolvemos el tiempo total que demoro determinado picker en ir a agarrar todos los objetos en la orden


def process_orders(orders, pickers_dist, n_pickers):
	''' Procesamos una serie de ordenes correspondiente a una simulacion. Recibe:
	@param orders: una lista con la cantidad de items de cada orden (como devuelve la funcion generate_orders).
	@param pickers_dist: diccionario definido con key = id de picker (0 a 9), y value un diccionario con los tiempos posibles y su correspondiente cdf.
	@param n_pickers: indica que se utilizan solo los primeros pickers.
	@return dos valores: el tiempo total en completar todas las ordenes, y el revenue generado.'''
	
	# En esta función, vamos a tener que mantener una lista de pickers y "tiempo de procesamiento", para cada vez que itero fijarme en el mínimo tiempo de picker para saber a cual selecciono...
	
	# Estado de los pickers. Inicialmente todos en el inicio del horizonte.
	pickers_stat = [0.0]*n_pickers	
	# Revenue recolectado durante la simulacion.
	collected_rev = 0.0

	# Procesamos las ordenes una por una, en el orden que fueron generadas.
	for order in orders:
		picker = get_picker(pickers_stat) # Buscamos primer picker en liberarse.

		tiempo = simulate_order_time(order, picker, pickers_dist) # Dado el picker, simulamos su tiempo.
		pickers_stat[picker] = pickers_stat[picker] + tiempo # Actualizamos el tiempo del picker.
		
		if pickers_stat[picker] <= 3600: # Verificamos si entro o no dentro de los 3600 segundos (1 hora) para recolectar el revenue.
			
			collected_rev = collected_rev + 100
		
	last_to_finish = max(pickers_stat) # Una vez que se termino el for, calculamos cuanto tiempo demora hacer todas las ordenes, calculando el maximo de la lista pickers_stat
	return last_to_finish, collected_rev # Devolvemos tiempo y revenue.	


def simulate_process(pickers_data, outcome, number_pickers, n_sims):
	''' Dado un posible outcome (bajo, moderado, alto) que tendra los limites esperados para la Unif(a,b) que modela la cantidad de ordenes,
	queremos realizar n_sims simulaciones y analizar el tiempo requerido para completarlas y el revenue generado.
	@param pickers_data: la estructura con los datos de la instancia, y las distribuciones para num. de items y pickers.
	@param outcome: una tupla de dos posiciones con los valores a,b de la variable Unif(a,b) que representa el escenario a analizar.
	@param number_pickers: el numero de pickers que se deben utilizar en la simulacion. No necesariamente es el maximo disponible.
	@param n_sim: cantidad de simulaciones a realizar.
	@return tupla con dos listas, una con los tiempos totales y otra con los revenues totales de cada simulacion.'''

	# Distribucion del numero de items.
	# Notar que las funciones para obtener las frecuencias y las acumuladas estan dadas al principio del archivo.
	# La clave de esto es tener un diccionario de diccionarios
	# Que tiene como clave el picker, el primero tiene como clave times (cuales son los distintos tiempos interpicks). El segundo diccionario, me devolvería cual es la función acumulada de ese tiempo interpick
	items_vals, items_probs = get_pdf(pickers_data.items_per_order) #tiene que llamar a get_pdf (...)
	items_cumprobs = get_cdf(items_probs) #tiene que llamar a get_cdf (...)
	

	# Distribucion de tiempos de viaje de cada picker.
	# Es un dict que tiene: 
	# 	-clave: id de picker (0 a 9)
	# 	-value: otro diccionario, con dos posibles claves:
	#		- 'times', donde el valor seran los posibles valores de la distribucion de tiempos inter-picks.
	#		- 'cumprobs', que tendra la freq. acumulada para cada uno de los valores en 'times'.
	pickers_dist = {}
	for picker in pickers_data.picker_times:
		# Reemplazar los None
		times, probs = get_pdf(pickers_data.picker_times[picker])
		cumprobs = get_cdf(probs)
		pickers_dist[picker] = {'times': times, 'cumprobs': cumprobs}


	# Guardamos los resultados de tiempo y revenue para cada simulacion dado un posible outcome y un numero de pickers.
	total_times = [] # Generamos lista vacia en donde vamos a ir agregando elementos
	total_revs = [] # Generamos lista vacia en donde vamos a ir agregando elementos

	# Simular.
	for i in range(n_sims):
	
		cant_ordenes = simulate_uniform(outcome[0],outcome[1]) # Simulamos primero el numero de ordenes. Recordar que para la Unif(a,b), a = outcome[0] y b = outcome[1].
		n_orders = generate_orders(cant_ordenes, items_vals, items_cumprobs) # Generamos las n_orders, cada una con su cantidad de items, usando la funcion generate_orders.
		# Procesamos las ordenes generadas con la funcion process_orders.
		# Los vamos agregando con la funcion append en las listas generadas anteriormente.
		total_times.append(process_orders(n_orders, pickers_dist, number_pickers)[0]) # Recordar que process_orders devuelve dos valores: (i) el tiempo total de la simulacion actual, (ii) el revenue recolectado 
		total_revs.append(process_orders(n_orders, pickers_dist, number_pickers)[1]) # Recordar que process_orders devuelve dos valores: (i) el tiempo total de la simulacion actual, (ii) el revenue recolectado
	return total_times,total_revs

def calculate_EMV(df, probs):
    # Calulo de EMV dado un DF con los escenarios y una lista con las probabilidades asociadas
    EMV = []
    for i in range(len(df)):
        EMV_i = []
        for j in range(len(df.columns)):
            EMV_ij = df.iloc[i, j]*probs[j]
            EMV_i.append(EMV_ij)
        EMV.append(sum(EMV_i))
        
    return EMV
    

def main():

	# Fijar la semilla para debug.
    random.seed(0)

	# Data base
    max_number_pickers = 10 # No tocar este valor. 
    number_of_simulations = 1000
	# Definicion de los posibles escenarios como una lista de tuplas, donde cada tupla representa los valores Unif(a,b)
	# Impacto bajo: Unif(20,25), posicion 0 de la lista scenarios.
	# Impacto moderado: Unif(30,40), posicion 1 de la lista scenarios.
	# Impacto alto: Unif(45,60), posicion 2 de la lista scenarios.
    scenarios = [(20,25),(30,40),(45,60)]
    probs_scenarios = [0.2, 0.4, 0.4]
	
	# Se leen los datos de archivo y se procesan. No deberian modificar esto. Es algo simple de hacer (pero molesto!)
    data = PickersData(max_number_pickers)
    
	####### Van dos posibles formas de resolverlos, segun cuan comomdos se sientan con el codigo.
	### Posibilidad 1: resolver el ejercicio de manera automática pasando por todas las combinaciones de outcome,n_pickers.
	# Simular
	# Movemos los escenarios.
    results_prob = pd.DataFrame()
    results_revs = pd.DataFrame()
    for outcome in scenarios:
		# Para cada escenario, el posible numero de pickers.
        scenario_probs = []
        scenario_revs = []
        for n_pickers in range(5,max_number_pickers + 1): 
            print(outcome, n_pickers)
			# Para cada posible escenario y numero de pickers realizamos las number_of_simulations simulaciones.
            times,revs = simulate_process(data, outcome, n_pickers, number_of_simulations)
			# Procesamos los resultados
            prob_completed, times, revs = analyze_results(times,revs)
            scenario_probs.append(prob_completed)
            scenario_revs.append(revs)
        
        results_prob = pd.concat([results_prob, pd.Series(scenario_probs)], axis = 1)
        results_revs = pd.concat([results_revs, pd.Series(scenario_revs)], axis = 1)
        
    EMV_revs = calculate_EMV(results_revs, probs_scenarios)
    EMV_servicio = calculate_EMV(results_prob, probs_scenarios)
    
    print('Valor Monetario Esperado por Nro de Pickers:')
    print(EMV_revs)
    print('')
    print('Nivel de Servicio Esperado por Nro de Pickers:')
    print(EMV_servicio)
    

	### Posibilidad 2: realizar una ejecucion por cada combinacion cambiando las opciones de outcome y n_pickers.
	### Descomentar las siguientes lineas, e ir modificando el valor de las variables outcome y n_pickers.
	# outcome = outcomes[0] 
	# n_pickers = 6
	## Para cada posible escenario y numero de pickers realizamos las number_of_simulations simulaciones.
	#times,revs = simulate_process(data, outcome, n_pickers, number_of_simulations)
	## Procesamos los resultados
	#analyze_results(times,revs)
	

if __name__ == '__main__':
	main()
