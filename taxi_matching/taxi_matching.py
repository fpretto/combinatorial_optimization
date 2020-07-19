import os
os.chdir('C:/Users/fabri/Google Drive/MiM+Analytics/2 - Modelos de Decision/TP 2/src/')
from Instance import Instance
import cplex
import pandas as pd
import numpy as np
import time

EPS = 1e-6

################## Solucion FCFS greedy ######################
def solve_instance_greedy(inst):
    ''' Dada una instancia del problema, retorna la solucion FCFS con criterio greedy.
    La funcion idealmente devuelve una tupla de parametros: funcion objetivo y solucion.'''
    # Transponemos la matriz para poder iterar mas facilmente sobre los pasajeros
    matrix_pax = np.array(inst.dist_matrix).transpose()

    # Para cada pasajero buscamos el vehiculo disponible mas cercano
    vehiculos_disponibles = set(range(len(inst.dist_matrix))) # Generamos un listado con los vehiculos disponibles
    f_obj = [] # Inicializamos una lista para almacenar las distancias recorridas
    solucion = [] # Inicializamos una lista para almacenar las soluciones
    for j in range(len(matrix_pax)):
        pax_taxi_dist = {}
        for i in vehiculos_disponibles:
            pax_taxi_dist.update({i: matrix_pax[j][i]}) # Generamos un diccionario con las distancias de cada vehiculo al pasajero j
        i = min(pax_taxi_dist, key = lambda k: pax_taxi_dist[k]) # Nos quedamos con el vehiculo que este a la minima distancia de j
        f_obj.append(matrix_pax[j][i]) # Guardamos la distancia recorrida por el vehiculo asignado
        solucion.append((i,j)) # Guardamos el par (vehiculo, pasajero) como solucion de asignacion
        vehiculos_disponibles.remove(i) # Eliminamos el vehiculos utilizado del listado de los disponibles

    # Para el punto 6 y 7, calculamos el ratio entre la distancia recorrida para buscar al pasajero y la del viaje
    ratio = []
    for i in range(len(solucion)):
        ratio.append(inst.dist_matrix[solucion[i][0]][solucion[i][1]]/
                     np.where(inst.paxs_trip_dist[solucion[i][1]] == 0, 1,
                              inst.paxs_trip_dist[solucion[i][1]]))

    # Devolvemos la distancia total recorrida, la solucion de asignacion y el ratio de distancias promedio
    return sum(f_obj), solucion, sum(ratio)/len(inst.dist_matrix)

###############################################################

################## Solucion LP ################################
def generate_variables(inst, myprob):
    ''' Genera la matriz de restricciones sobre myprob. Reemplazar pass por el codigo correspondiente.'''

    objective = [] # Generamos una lista donde guardar la distancia entre cada vehiculo i y pasajero j
    idx = 0 # Inicializamos un contador para almacenar los ids
    for i in range(len(inst.dist_matrix)):
        for j in range(len(inst.dist_matrix)):
            inst.var_idx.update({(i,j): idx}) # Agregamos un id para cada par (vehiculo, pasajero)
            objective.append(inst.dist_matrix[i][j]) # Agregamos la distancia entre cada par (vehiculo, pasajero)
            idx += 1

    # Agregamos las variables a la funcion objetivo del problema lineal
    myprob.variables.add(obj=objective, lb=[0]*len(objective))


def generate_constraints(inst, myprob):
    ''' Genera la matriz de restricciones sobre myprob. Reemplazar pass por el codigo correspondiente.'''

    # Agregamos una a una las restricciones de que cada vehiculo le corresponde un pasajero
    vals = [1.0] * len(inst.dist_matrix)
    for i in range(len(inst.dist_matrix)):
        ind = []
        for j in range(len(inst.dist_matrix)):
            ind.append(inst.var_idx[(i, j)])

        row = [ind, vals]
        myprob.linear_constraints.add(lin_expr=[row], senses=['E'], rhs = [1])

    # Trasnponemos la matriz para poder iterar mas facilmente sobre los pasajeros
    matrix_pax = np.array(inst.dist_matrix).transpose()

    # Agregamos una a una las restricciones de que cada pasajero le corresponde un vehiculo
    vals = [1.0] * len(matrix_pax)
    for j in range(len(matrix_pax)):
        ind = []
        for i in range(len(matrix_pax)):
            ind.append(inst.var_idx[(i, j)])

        row = [ind, vals]
        myprob.linear_constraints.add(lin_expr=[row], senses=['E'], rhs = [1])

def populate_by_row(inst, myprob):
    ''' Genera el modelo.'''
    # Seteamos problema de minimizacion.
    myprob.objective.set_sense(myprob.objective.sense.minimize)

    # Agregamos las variables del problema
    generate_variables(inst, myprob)

    # Agregamos las restricciones del problema
    generate_constraints(inst, myprob)

    # Exportamos el LP cargado en myprob con formato .lp.
    myprob.write('taxi_matching.lp')

def solve_instance_lp(inst):
    ''' Dada una instancia del problema, retorna la solucion general resolviendo un LP.
    La funcion idealmente devuelve una tupla de parametros: funcion objetivo y solucion.'''

    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    # Armamos el modelo.
    populate_by_row(inst, prob_lp)
    # Resolvemos el LP
    prob_lp.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'.
    x = prob_lp.solution.get_values() # Obtenemos los valores de las variables
    f_obj = prob_lp.solution.get_objective_value() # Obtenemos el valor de la funcion objetivo
    stat = prob_lp.solution.get_status() # Obtenemos el id de status de la solucion
    stat_str = prob_lp.solution.get_status_string(status_code=stat) # Obtenemos el valor del status de la solucion

    print('Funcion objetivo: ', f_obj)
    print('Status solucion: ', stat_str, '(' + str(stat) + ')')

    # Guardamos las variables > 0 (variables usadas)
    solucion = []
    for i in range(len(x)):
        if x[i] > EPS:
            for (vehiculo, pasajero), idx in inst.var_idx.items():
                if idx == i:
                    solucion.append((vehiculo, pasajero))

    # Para el punto 6 y 7, calculamos el ratio entre la distancia recorrida para buscar al pasajero y la del viaje
    ratio = []
    for i in range(len(solucion)):
        ratio.append(inst.dist_matrix[solucion[i][0]][solucion[i][1]]/
                     np.where(inst.paxs_trip_dist[solucion[i][1]] == 0, 1,
                              inst.paxs_trip_dist[solucion[i][1]]))
    # Devolvemos la distancia total recorrida, la solucion de asignacion y el ratio de distancias promedio
    return f_obj, solucion, sum(ratio)/len(inst.dist_matrix)

###############################################################

################## Solucion LP - Alternativa ##################

def generate_variables_alternativa(inst, myprob):
    ''' Genera la matriz de restricciones sobre myprob. Reemplazar pass por el codigo correspondiente.'''

    objective = [] # Generamos una lista donde guardar la distancia entre cada vehiculo i y pasajero j
    idx = 0 # Inicializamos un contador para almacenar los ids
    for i in range(len(inst.dist_matrix)):
        for j in range(len(inst.dist_matrix)):
            inst.var_idx.update({(i,j): idx}) # Agregamos un id para cada par (vehiculo, pasajero)
            # Agregamos el ratio entre distancia entre cada par (vehiculo, pasajero) y la distancia del viaje a realizar
            objective.append(inst.dist_matrix[i][j]/np.where(inst.paxs_trip_dist[j] == 0, 1, inst.paxs_trip_dist[j]))
            idx += 1

    # Agregamos las variables a la funcion objetivo del problema lineal
    myprob.variables.add(obj=objective, lb=[0]*len(objective))

def populate_by_row_alternativa(inst, myprob):
    ''' Genera el modelo.'''
    # Seteamos problema de minimizacion.
    myprob.objective.set_sense(myprob.objective.sense.minimize)

    # Agregamos las variables del problema
    generate_variables_alternativa(inst, myprob)

    # Agregamos las restricciones del problema
    generate_constraints(inst, myprob)

    # Exportamos el LP cargado en myprob con formato .lp.
    myprob.write('taxi_matching_alternativa.lp')

def solve_instance_lp_alternativa(inst):
    ''' Dada una instancia del problema, retorna la solucion general resolviendo un LP.
    La funcion idealmente devuelve una tupla de parametros: funcion objetivo y solucion.'''

    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    # Armamos el modelo.
    populate_by_row_alternativa(inst, prob_lp)
    # Resolvemos el LP
    prob_lp.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'.
    x = prob_lp.solution.get_values() # Obtenemos los valores de las variables
    ratio = prob_lp.solution.get_objective_value() # Obtenemos el valor de la funcion objetivo (en este caso la suma de ratios)
    stat = prob_lp.solution.get_status() # Obtenemos el id de status de la solucion
    stat_str = prob_lp.solution.get_status_string(status_code=stat) # Obtenemos el valor del status de la solucion

    # Imprimimos las variables > 0 (variables usadas)
    solucion = []
    for i in range(len(x)):
        if x[i] > EPS:
            for (vehiculo, pasajero), idx in inst.var_idx.items():
                if idx == i:
                    solucion.append((vehiculo, pasajero))
    f_obj = []
    for i in range(len(solucion)):
        f_obj.append(inst.dist_matrix[solucion[i][0]][solucion[i][1]])

    print('Funcion objetivo: ', sum(f_obj))
    print('Status solucion: ', stat_str, '(' + str(stat) + ')')

    # Devolvemos la distancia total recorrida, la solucion de asignacion y el ratio de distancias promedio
    return sum(f_obj), solucion, ratio/len(inst.dist_matrix)

###############################################################

#### Implementar funciones auxiliares necesarias para analizar resultados y proponer mejoras.

def main():
    inst_types = ['small','medium','large','xl']
    n_inst = ['0','1','2','3','4','5','6','7','8','9']

    # Esquema para ejecutar las soluciones directamente sobre las 40 instancias.
    results = pd.DataFrame()
    for t in inst_types:
        for n in n_inst:
            t = 'small'
            n = '0'
            inst_file = 'input/' + t + '_' + n + '.csv'
            inst = Instance(inst_file)

            # Solucion greedy.
            start_time = time.time()
            f_greedy, x_greedy, ratio_greedy = solve_instance_greedy(inst)
            greedy_time = time.time() - start_time

            # Solucion lp
            start_time = time.time()
            f_lp, x_lp, ratio_lp = solve_instance_lp(inst)
            lp_time = time.time() - start_time

            # Solucion lp alternativa
            start_time = time.time()
            f_lp_alt, x_lp_alt, ratio_alt = solve_instance_lp_alternativa(inst)
            lp_alt_time = time.time() - start_time

            # Guardamos la solucion de cada algoritmo para la instancia
            inst_sol = pd.concat([pd.Series(t), pd.Series(n),
                                  pd.Series(f_greedy), pd.Series(ratio_greedy), pd.Series(greedy_time),
                                  pd.Series(f_lp)    , pd.Series(ratio_lp)    , pd.Series(lp_time),
                                  pd.Series(f_lp_alt), pd.Series(ratio_alt)   , pd.Series(lp_alt_time)], axis=1)

            results = pd.concat([results, inst_sol], axis = 0, ignore_index = True)

    # Consolidamos los resultados totales y generamos metricas
    results.columns = ['TipoInstancia', 'NroInstancia',
                       'SolucionGreedy', 'RatioGreedy', 'TiempoGreedy',
                       'SolucionMatching', 'RatioMatching', 'TiempoMatching',
                       'SolucionAlternativa', 'RatioAlternativa', 'TiempoAlternativa']

    results['GAP_dist_lp_gr']   = round((results['SolucionMatching']    / results['SolucionGreedy'] - 1),2)
    results['GAP_ratio_lp_gr']  = round((results['RatioMatching']       / results['RatioGreedy'] - 1), 2)
    results['GAP_time_lp_gr']   = round((results['TiempoMatching']      / results['TiempoGreedy'] - 1), 2)
    results['GAP_dist_alt_gr']  = round((results['SolucionAlternativa'] / results['SolucionGreedy'] - 1),2)
    results['GAP_ratio_alt_gr'] = round((results['RatioAlternativa']    / results['RatioGreedy'] - 1), 2)
    results['GAP_time_alt_gr']  = round((results['TiempoAlternativa']   / results['TiempoGreedy'] - 1), 2)
    results['GAP_dist_alt_lp']  = round((results['SolucionAlternativa'] / results['SolucionMatching'] - 1),2)
    results['GAP_ratio_alt_lp'] = round((results['RatioAlternativa']    / results['RatioMatching'] - 1), 2)
    results['GAP_time_alt_lp']  = round((results['TiempoAlternativa']   / results['TiempoMatching'] - 1), 2)

    # Exportamos los resultados
    path = 'C:/Repo/Github/combinatorial_optimization/taxi_matching/'
    results.to_csv(path + 'results.csv')
    results.groupby('TipoInstancia').mean().to_csv(path + 'results_grouped.csv')

if __name__ == '__main__':
    main()

