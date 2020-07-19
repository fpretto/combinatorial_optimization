import sys
import cplex

TOLERANCE =10e-6 

#agregamos parametros. Esto podria agregarse por sysargv si despues se decide 
#extender la cantidad de turnos
cant_dias = 6
cant_turnos_por_dia = 5
cant_turnos = cant_dias * cant_turnos_por_dia 
cant_escalas_salario = 4
valores_escala= [-1000,-1200,-1400,-1500] 
big_M = 1000 



class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])
        

class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        self.var_idx = {} #agregamos a la clase la estructura que guardara los 
                          #indices de las variables
        

    def load(self,filename):
        # Abrimos el archivo.
        f = open(filename)

        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)
        
        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))
        
        
        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))
        
        # Cerramos el archivo.
        f.close()


def get_instance_data():
    file_location = sys.argv[1].strip()
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance


def generate_variables(my_problem, data):
    # Genera variables y función objetivo 
    # Generamos la estructura que mapea ("nombre variable","subindices") ---> indice de variable.
    
    # var_cnt va a ser el valor que va llevando la cuenta de cuantas variables 
    #agregadas hasta el momento.
    var_cnt = 0

    obj = []
    lb = []
    ub = []
    types = []
    names=[]

    # Agregamos las variables y(j,k)
    for k in range(cant_turnos):
        for j in range(data.cantidad_ordenes):

            # Definimos el valor para (i,j). 
            data.var_idx[('y',j,k)]=var_cnt
            names.append("y"+str((j,k)))
            obj.append(data.ordenes[j].beneficio)
            lb.append(0)
            ub.append(1)   
            types.append('B')

            # Incrementamos el proximo indice no usado
            var_cnt += 1

        
    # Agregamos las variables x(i,j,k)
    for k in range(cant_turnos):
        for j in range(data.cantidad_ordenes):
            for i in range(data.cantidad_trabajadores):

                # Definimos el valor para (i,j,k). 
                data.var_idx[('x',i,j,k)]=var_cnt
                names.append("x"+str((i,j,k)))
                obj.append(0)
                lb.append(0)
                ub.append(1)
                types.append('B')

                # Incrementamos el proximo indice no usado
                var_cnt += 1
            
        
    # Agregamos las variables D(i,d)
    for d in range(cant_dias):
        for i in range(data.cantidad_trabajadores):

            # Definimos el valor para (i,j). 
            data.var_idx[('D',i,d)]=var_cnt
            names.append("D"+str((i,d)))
            obj.append(0)
            lb.append(0)   
            ub.append(1)
            types.append('B')

            # Incrementamos el proximo indice no usado
            var_cnt += 1  
 
           
    # Agregamos la variable E(i,f)
    for j in range(cant_escalas_salario):
        for i in range(data.cantidad_trabajadores):

            # Definimos el valor para (i,j). 
            data.var_idx[('E',i,j)]=var_cnt
            names.append("E"+str((i,j)))
            obj.append(valores_escala[j]) # Agregamos los valores segun la escala de ordenes trabajadas
            lb.append(0)   
            ub.append(10) # Topeamos la variable en 10 ya que es el maximo de ordenes/turnos que un trabajador puede
                          # hacer en cada valor de la escala
            types.append('I')

            # Incrementamos el proximo indice no usado
            var_cnt += 1  

    # Agregamos la variable W(i,f)
    for j in range(cant_escalas_salario):
        for i in range(data.cantidad_trabajadores):
            
            # Definimos el valor para (i,j). 
            data.var_idx[('W',i,j)]=var_cnt
            names.append("W"+str((i,j)))
            obj.append(0)
            lb.append(0)   
            ub.append(1)
            types.append('B')

            # Incrementamos el proximo indice no usado
            var_cnt += 1  
    
    # Agregamos la variable X(i)
    for i in range(data.cantidad_trabajadores):
            
            # Definimos el valor para (i). 
            data.var_idx[('X',i)]=var_cnt
            names.append("X"+str((i)))
            obj.append(0)
            lb.append(0)   
            ub.append(24) # Topeamos la variable en 24 ya que es el maximo de ordenes/turnos que un trabajador puede hacer
            types.append('I')

            # Incrementamos el proximo indice no usado
            var_cnt += 1     


    # Agregamos la variable X(max)
    data.var_idx[('X','max')]=var_cnt
    names.append("X"+'max')
    obj.append(0)
    lb.append(0)   
    ub.append(24) # Topeamos la variable en 24 ya que es el maximo de ordenes/turnos que un trabajador puede hacer
    types.append('I')

    # Incrementamos el proximo indice no usado
    var_cnt += 1     

    # Agregamos la variable X(min)
    data.var_idx[('X','min')]=var_cnt
    names.append("X"+'min')
    obj.append(0)
    lb.append(0)   
    ub.append(24) # Topeamos la variable en 24 ya que es el maximo de ordenes/turnos que un trabajador puede hacer
    types.append('I')

    # Incrementamos el proximo indice no usado
    var_cnt += 1

    # Agregamos al modelo
    my_problem.variables.add(obj = obj, lb = lb, ub= ub, types = types, names = names) 


def add_constraints_1(my_problem, data):
    
    vals= [1.0]* cant_turnos 
    
    # Agregamos cada una de las restricciones, moviendonos primero por las ordenes
    # y despues por los turnos
    for j in range(data.cantidad_ordenes):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos):
            ind.append(data.var_idx[('y',j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [1])    


def add_constraints_2(my_problem, data):
    
    vals= [1.0]* cant_dias 
    
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por los dias
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for d in range(cant_dias):
            ind.append(data.var_idx[('D',i,d)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [5]) 
        

def add_constraints_3a(my_problem, data):
    
    vals= [1.0]* data.cantidad_ordenes 
    
    # Agregamos cada una de las restricciones, moviendonos primero por los turnos,
    # despues por los trabajadores, despues por las ordenes
    for k in range(cant_turnos):
        for i in range(data.cantidad_trabajadores):
            # Generamos los indices
            ind = []
        # Agregamos en cada caso el indice de todas las variable x para un
        # guardados en var_idx. 
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])
        
        # Agregamos una restriccion por cada orden.
            row = [ind,vals]
            my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [1]) 
 
       
def add_constraints_3b(my_problem, data):
    
    vals= [1.0]* data.cantidad_ordenes * cant_turnos_por_dia
    
    # Cargamos las restriccion 3b1
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia):
            # Agregamos en cada caso el indice de todas las variable x  
            # guardados en var_idx.
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])  
    
    # Cargamos la restriccion 3b2
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del segundo dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia,  cant_turnos_por_dia * 2):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])  

    # Cargamos la restriccion 3b3
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del tercer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *2,  cant_turnos_por_dia *3):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])     

    # Cargamos la restriccion 3b4
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del tercer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *3,  cant_turnos_por_dia *4):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])  

    # Cargamos la restriccion 3b5
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del tercer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *4,  cant_turnos_por_dia *5):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])  

    # Cargamos la restriccion 3b6
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del tercer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *5,  cant_turnos_por_dia *6):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [4])                       


def add_constraints_3c(my_problem, data):
    
    vals= [1.0]* data.cantidad_ordenes * cant_turnos_por_dia
    vals.append(-big_M)

    # Cargamos la restriccion 3c1
    dia= 0
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  
    dia = dia+1
    
    # Cargamos la restriccion 3c2
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia,cant_turnos_por_dia *2):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  
    dia = dia+1
    
    # Cargamos la restriccion 3c3
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *2,cant_turnos_por_dia *3):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  
    dia = dia+1

    # Cargamos la restriccion 3c4
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *3,cant_turnos_por_dia *4):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  
    dia = dia+1
    
    # Cargamos la restriccion 3c5
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    #y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *4,cant_turnos_por_dia *5):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  
    dia = dia+1
    
    # Cargamos la restriccion 3c6
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    #y despues por las ordenes y turnos del primer dia
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for k in range(cant_turnos_por_dia *5,cant_turnos_por_dia *6):
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])

        # Agregamos la variable D
        ind.append(data.var_idx[('D',i,dia)])
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])  


def add_constraints_4a(my_problem, data):
    vals = [1.0, 1.0]

    # Cargamos la restriccion 4a1 - Dia 1
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4a2 - Dia 2
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia, cant_turnos_por_dia * 2 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4a3 - Dia 3
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 2, cant_turnos_por_dia * 3 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4a4 - Dia 4
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 3,cant_turnos_por_dia * 4 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4a5 - Dia 5
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 4, cant_turnos_por_dia * 5 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4a6 - Dia 6
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 5, cant_turnos_por_dia * 6 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[0], k)])
                ind.append(data.var_idx[('x', i, par[1], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

def add_constraints_4b(my_problem, data):
    vals = [1.0, 1.0]

    # Cargamos la restriccion 4b1 - Dia 1
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4b2 - Dia 2
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia, cant_turnos_por_dia * 2 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4b3 - Dia 3
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 2, cant_turnos_por_dia * 3 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4b4 - Dia 4
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 3,cant_turnos_por_dia * 4 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4b5 - Dia 5
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 4, cant_turnos_por_dia * 5 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])

    # Cargamos la restriccion 4b6 - Dia 6
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores
    # y despues por las ordenes y turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_conflictivas:
            for k in range(cant_turnos_por_dia * 5, cant_turnos_por_dia * 6 - 1):  # corta uno antes que los demas porque va a tener el (k+1)
                # Generamos los indices
                ind = []

                ind.append(data.var_idx[('x', i, par[1], k)])
                ind.append(data.var_idx[('x', i, par[0], k + 1)])

                # Agregamos una restriccion por cada par de ordenes conflictivas.
                row = [ind, vals]
                my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[1])


def add_constraints_5(my_problem, data):

    # Agregamos cada una de las restricciones, moviendonos primero por las ordenes
    # despues por los turnos y despues por los trabajadores
    for j in range(data.cantidad_ordenes):
        # Generamos los indices
        for k in range(cant_turnos):
            vals = [1.0] * data.cantidad_trabajadores
            ind = []
            for i in range(data.cantidad_trabajadores):
                ind.append(data.var_idx[('x',i,j,k)])
        
            ind.append(data.var_idx[('y',j,k)])
            # Agregamos los Tj
            vals.append (-data.ordenes[j].trabajadores_necesarios)

        # Agregamos una restriccion por cada orden
            row = [ind,vals]
            my_problem.linear_constraints.add(lin_expr = [row], senses = ['G'], rhs = [0])  


def add_constraints_6(my_problem, data):
    
    vals= [1.0, -1.0]

    # Cargamos la restriccion 6a1 - Dia 1
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia-1): # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y',par[0],k)])
            ind.append(data.var_idx[('y',par[1],k+1)])

        # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind,vals]
            my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])

    # Cargamos la restriccion 6a2 - Dia 2
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia, cant_turnos_por_dia * 2 - 1):  # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y', par[0], k)])
            ind.append(data.var_idx[('y', par[1], k + 1)])

            # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind, vals]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Cargamos la restriccion 6a3 - Dia 3
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia * 2, cant_turnos_por_dia * 3 - 1):  # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y', par[0], k)])
            ind.append(data.var_idx[('y', par[1], k + 1)])

            # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind, vals]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Cargamos la restriccion 6a4 - Dia 4
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia * 3, cant_turnos_por_dia * 4 - 1):  # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y', par[0], k)])
            ind.append(data.var_idx[('y', par[1], k + 1)])

            # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind, vals]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Cargamos la restriccion 6a5 - Dia 5
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia * 4, cant_turnos_por_dia * 5 - 1):  # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y', par[0], k)])
            ind.append(data.var_idx[('y', par[1], k + 1)])

            # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind, vals]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])

    # Cargamos la restriccion 6a6 - Dia 6
    # Agregamos cada una de las restricciones, moviendonos primero por los pares
    # de ordenes y despues por los turnos
    for par in data.ordenes_correlativas:
        for k in range(cant_turnos_por_dia * 5, cant_turnos_por_dia * 6 - 1):  # Corta uno antes que el resto porque tengo (k+1)
            # Generamos los indices
            ind = []
            ind.append(data.var_idx[('y', par[0], k)])
            ind.append(data.var_idx[('y', par[1], k + 1)])

            # Agregamos una restriccion por cada par de ordenes correlativas y turnos.
            row = [ind, vals]
            my_problem.linear_constraints.add(lin_expr=[row], senses=['L'], rhs=[0])


def add_constraints_7a(my_problem, data):
    
    vals= [1.0]* cant_turnos * data.cantidad_ordenes
    vals.append(-1.0)

    # Agregamos cada una de las restricciones, moviendonos primero por los turnos
    # y despues por las ordenes y despues por los trabajadores
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        for k in range(cant_turnos): 
            for j in range(data.cantidad_ordenes):
                ind.append(data.var_idx[('x',i,j,k)])
            
        ind.append(data.var_idx[('X',i)]) 
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [0])


def add_constraints_7b(my_problem, data):
    
    vals= [1.0, -1.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('X','max')])            
        ind.append(data.var_idx[('X',i)])    
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['G'], rhs = [0])


def add_constraints_7c(my_problem, data):
    
    vals= [1.0, -1.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('X','min')])            
        ind.append(data.var_idx[('X',i)])    
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0])

def add_constraints_7d(my_problem, data):
    
        vals= [1.0, -1.0]
    
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('X','max')])            
        ind.append(data.var_idx[('X','min')])    
        # Agregamos una restriccion la restriccion.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [10])



def add_constraints_8a1(my_problem, data):
    
    vals= [1.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,0)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [5])


def add_constraints_8a2(my_problem, data):
    
    vals= [1.0, -5.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,0)])
        ind.append(data.var_idx[('W',i,0)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['G'], rhs = [0])         

def add_constraints_8a3(my_problem, data):
    
    vals= [1.0, -5.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,1)])
        ind.append(data.var_idx[('W',i,1)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['G'], rhs = [0]) 

def add_constraints_8a4(my_problem, data):
    
    vals= [1.0, -5.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,1)])
        ind.append(data.var_idx[('W',i,0)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0]) 


def add_constraints_8a5(my_problem, data):
    
    vals= [1.0, -5.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,2)])
        ind.append(data.var_idx[('W',i,2)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['G'], rhs = [0]) 

def add_constraints_8a6(my_problem, data):
    
    vals= [1.0, -5.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,2)])
        ind.append(data.var_idx[('W',i,1)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0]) 

def add_constraints_8a7(my_problem, data):
    
    vals= [1.0, -9.0]

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        ind.append(data.var_idx[('E',i,3)])
        ind.append(data.var_idx[('W',i,2)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0]) 

def add_constraints_8b(my_problem, data):
    
    vals= [1.0] * cant_escalas_salario
    vals.append(-1)

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores 
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []

        for f in range(cant_escalas_salario):
            ind.append(data.var_idx[('E',i,f)])
        ind.append(data.var_idx[('X',i)])
                
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [0])    


def generate_constraints(data, my_problem):
    
    # Agregamos cada familia de restricciones obligatorias
    add_constraints_1(data, my_problem)
    add_constraints_2(data, my_problem)
    add_constraints_3a(data, my_problem)
    add_constraints_3b(data, my_problem)
    add_constraints_3c(data, my_problem)
    add_constraints_4a(data, my_problem)
    add_constraints_4b(data, my_problem)
    add_constraints_5(data, my_problem)
    add_constraints_6(data, my_problem)
    add_constraints_7a(data, my_problem)
    add_constraints_7b(data, my_problem)
    add_constraints_7c(data, my_problem)
    add_constraints_7d(data, my_problem)
    add_constraints_8a1(data, my_problem)
    add_constraints_8a2(data, my_problem)
    add_constraints_8a3(data, my_problem)
    add_constraints_8a4(data, my_problem)
    add_constraints_8a5(data, my_problem)
    add_constraints_8a6(data, my_problem)
    add_constraints_8a7(data, my_problem)
    add_constraints_8b(data, my_problem)


    
### BLOQUE DE VARIABLES Y RESTRICCIONES DESEABLES ###

def generate_variables_trab_conflictivos(my_problem, data):
    # Genera variables para las restricciones de trabajadores conflictivos
    
    #var_cnt va parte de la ultima agregada al diccionario
    var_cnt = len(data.var_idx)
    obj = []
    lb = []
    ub = []
    types = []
    names=[]
               
    # Agregamos la variable F(j,a,b)
    # Generamos los indices.
    for j in range(data.cantidad_ordenes):
        for par in data.conflictos_trabajadores:
            # Tenemos los dos for anidados porque necesitamos las combinaciones de (i,j)
            
            # Definimos el valor para (j,a,b). 
            data.var_idx[('F',j,par[0],par[1])]=var_cnt
            names.append("F"+str((j,par[0],par[1])))
            obj.append(0)
            lb.append(0)   
            ub.append(1)
            types.append('B')

            # Incrementamos el proximo indice no usado
            var_cnt += 1  
    
    # Agregamos la variable F(j)
    # Generamos los indices.
    for j in range(data.cantidad_ordenes):
        
        # Definimos el valor para (j). 
        data.var_idx[('F',j)]=var_cnt
        names.append("F"+str(j))
        obj.append(0)
        lb.append(0)   
        ub.append(1)
        types.append('B')

        # Incrementamos el proximo indice no usado
        var_cnt += 1
    
    # Agregamos la variable F
    # Generamos los indices.
    data.var_idx[('F',data.cantidad_ordenes+1)]=var_cnt
    names.append("F"+str(('total')))
    obj.append(-100)
    lb.append(0)   
    ub.append(1000)
    types.append('I')

    # Incrementamos el proximo indice no usado
    var_cnt += 1 

    # Agregamos al modelo
    my_problem.variables.add(obj = obj, lb = lb, ub= ub, types = types, names = names)   
    

        
def generate_variables_ord_repetitivas(my_problem, data):
    # Genera variables para las restricciones de ordenes repetitivas

    var_cnt = len(data.var_idx)
    
    obj = []
    lb = []
    ub = []
    types = []
    names=[]
            
    # Agregamos la variable R(i,a,b)
    # Generamos los indices.
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_repetitivas:
            # Definimos el valor para (i,a,b). 
            data.var_idx[('R',i,par[0],par[1])]=var_cnt
            names.append('R'+str((i,par[0],par[1])))
            obj.append(0)
            lb.append(0)
            ub.append(1)
            types.append('B')

            # Incrementamos el proximo indice no usado
            var_cnt += 1
    
    # Agregamos la variable R(i)
    # Generamos los indices.
    for i in range(data.cantidad_trabajadores):
        
        # Definimos el valor para (i). 
        data.var_idx[('R',i)]=var_cnt
        names.append("R"+str(i))
        obj.append(0)
        lb.append(0)   
        ub.append(1)
        types.append('B')

        # Incrementamos el proximo indice no usado
        var_cnt += 1
    
    # Agregamos la variable R
    # Generamos los indices.
    data.var_idx[('R',data.cantidad_trabajadores+1)]=var_cnt
    names.append("R"+str(('total')))
    obj.append(-100)
    lb.append(0)   
    ub.append(1000)
    types.append('I')

    # Incrementamos el proximo indice no usado
    var_cnt += 1 

    # Agregamos al modelo
    my_problem.variables.add(obj = obj, lb = lb, ub= ub, types = types, names = names)

    
def generate_variables_deseables(my_problem, data):
    generate_variables_ord_repetitivas(my_problem, data)
    generate_variables_trab_conflictivos(my_problem, data)
    
    

def add_constraints_d1a(my_problem, data):
    
    vals= [1.0] * cant_turnos * 2
    vals.append(-1.0)
    
    # Agregamos cada una de las restricciones, moviendonos primero por las ordenes,
    # luego por los pares de trabajadores conflictivos y despues por los turnos
    for j in range(data.cantidad_ordenes):
        for par in data.conflictos_trabajadores:
            # Generamos los indices
            ind = []
            for k in range(cant_turnos):
                ind.append(data.var_idx[('x',par[0],j,k)])
                ind.append(data.var_idx[('x',par[1],j,k)])
            
            ind.append(data.var_idx[('F',j,par[0],par[1])])
            
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [1]) 

def add_constraints_d1b(my_problem, data):

    vals= [1.0] * data.cantidad_ordenes
    vals.append(-big_M)
    
    # Agregamos cada una de las restricciones, moviendonos primero por las ordenes y
    # luego por los pares de trabajadores conflictivos.
    for j in range(data.cantidad_ordenes):
        # Generamos los indices
        ind = []
        for par in data.conflictos_trabajadores:
            ind.append(data.var_idx[('F',j,par[0],par[1])])
            
        ind.append(data.var_idx[('F',j)])
            
        # Agregamos una restriccion por cada orden.
        row = [ind,vals]
        
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0]) 

def add_constraints_d1c(my_problem, data):

    vals= [1.0] * data.cantidad_ordenes
    vals.append(-1.0)

    # Generamos los indices
    ind = []

    # Agregamos cada una de las restricciones, moviendonos por las ordenes
    for j in range(data.cantidad_ordenes):
        ind.append(data.var_idx[('F',j)])
    
    ind.append(data.var_idx[('F',data.cantidad_ordenes+1)])
    # Agregamos una restriccion por cada orden.
    row = [ind,vals]
    my_problem.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [0])

def add_constraints_d2a(my_problem, data):
    
    vals= [1.0] * cant_turnos * 2
    vals.append(-1.0)
    
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores,
    # luego por los pares de ordenes repetitivas y despues por los turnos
    for i in range(data.cantidad_trabajadores):
        for par in data.ordenes_repetitivas:
            # Generamos los indices
            ind = []
            for k in range(cant_turnos):
                ind.append(data.var_idx[('x',i,par[0],k)])
                ind.append(data.var_idx[('x',i,par[1],k)])
            
            ind.append(data.var_idx[('R',i,par[0],par[1])])
            
            # Agregamos una restriccion por cada trabajador y par de ordenes.
            row = [ind,vals]
            my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [1])

def add_constraints_d2b(my_problem, data):

    vals= [1.0] * len(data.ordenes_repetitivas)
    vals.append(-big_M)
    
    # Agregamos cada una de las restricciones, moviendonos primero por los trabajadores y
    # luego por los pares de ordenes repetitivas.
    for i in range(data.cantidad_trabajadores):
        # Generamos los indices
        ind = []
        for par in data.ordenes_repetitivas:
            ind.append(data.var_idx[('R',i,par[0],par[1])])
            
        ind.append(data.var_idx[('R',i)])
            
        # Agregamos una restriccion por cada trabajador.
        row = [ind,vals]        
        my_problem.linear_constraints.add(lin_expr = [row], senses = ['L'], rhs = [0]) 
        
def add_constraints_d2c(my_problem, data):

    vals= [1.0] * data.cantidad_trabajadores
    vals.append(-1.0)

    # Generamos los indices
    ind = []

    # Agregamos cada una de las restricciones, moviendonos por los trabajadores.
    for i in range(data.cantidad_trabajadores):
        ind.append(data.var_idx[('R',i)])
    
    ind.append(data.var_idx[('R',data.cantidad_trabajadores+1)])
    # Agregamos una restriccion por cada trabajador.
    row = [ind,vals]
    my_problem.linear_constraints.add(lin_expr = [row], senses = ['E'], rhs = [0])


    
    
def generate_constraints_deseables(my_problem, data):
    
    add_constraints_d1a(my_problem, data)
    add_constraints_d1b(my_problem, data)
    add_constraints_d1c(my_problem, data)
    add_constraints_d2a(my_problem, data)
    add_constraints_d2b(my_problem, data)    
    add_constraints_d2c(my_problem, data) 
    

    

def populate_by_row(my_problem, data, modelo):
  
    # Agregamos las variables y función objetivo

    if modelo == 'CRD':
        generate_variables(my_problem, data)
        generate_variables_deseables(my_problem, data)
    else:
        generate_variables(my_problem, data)

    
    # Seteamos direccion del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)

    # Definimos las restricciones del modelo.

    if modelo == 'CRD':
        generate_constraints(my_problem, data)
        generate_constraints_deseables(my_problem, data)
    else:
        generate_constraints(my_problem, data)



    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('field_service.lp')

def solve_lp(my_problem, algoritmo):

    # Definimos los parametros del solver
    my_problem.parameters.mip.tolerances.mipgap.set(0.005)
    #my_problem.parameters.mip.tolerances.mipgap.set(1e-10)

    if algoritmo == 'BB_BBS':
        # Parametros para definir un branch-and-bound puro sin cortes ni heuristicas
        my_problem.parameters.mip.limits.cutpasses.set(-1)
        my_problem.parameters.mip.strategy.heuristicfreq.set(-1)

        # Parametro para definir que algoritmo de lp usar
        my_problem.parameters.lpmethod.set(my_problem.parameters.lpmethod.values.primal)

        # Parametro para definir la eleccion de nodo
        my_problem.parameters.mip.strategy.nodeselect.set(1)

    elif algoritmo == 'BB_DFS':
        # Parametros para definir un branch-and-bound puro sin cortes ni heuristicas
        my_problem.parameters.mip.limits.cutpasses.set(-1)
        my_problem.parameters.mip.strategy.heuristicfreq.set(-1)

        # Parametro para definir que algoritmo de lp usar
        my_problem.parameters.lpmethod.set(my_problem.parameters.lpmethod.values.primal)

        # Parametro para definir la eleccion de nodo
        my_problem.parameters.mip.strategy.nodeselect.set(0)

    elif algoritmo == 'BC_CC':
        # Parametros para definir cortes y heuristicas
        my_problem.parameters.mip.strategy.heuristicfreq.set(-1)

        # my_problem.parameters.timelimit.set(60)
        # ~ my_problem.parameters.mip.limits.cutpasses.set(-1)

        # ~ my_problem.parameters.mip.cuts.cliques.set(-1)
        # ~ my_problem.parameters.mip.cuts.flowcovers.set(-1)
        my_problem.parameters.mip.cuts.covers.set(-1)
        # ~ my_problem.parameters.mip.cuts.disjunctive.set(-1)
        # ~ my_problem.parameters.mip.cuts.pathcut.set(-1)
        # ~ my_problem.parameters.mip.cuts.gubcovers.set(-1)
        # ~ my_problem.parameters.mip.cuts.mcfcut.set(-1)
        # ~ my_problem.parameters.mip.cuts.implied.set(-1)
        # ~ my_problem.parameters.mip.cuts.mircut.set(-1)
        # ~ my_problem.parameters.mip.cuts.zerohalfcut.set(-1)
    
    # Resolvemos el ILP.    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    x_names = my_problem.variables.get_names()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ', objective_value)
    print('Status solucion: ', status_string,'(' + str(status) + ')')

    # Imprimimos las variables usadas.
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.

        if x_variables[i] > TOLERANCE:
            print(str(x_names[i]) + ':' , x_variables[i])



def main():
    
    ## Obtenemos los datos de la instancia.
    data = get_instance_data()
    
    ## Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    ## Armamos el modelo. Elegimos uno de los 2 modelos
    # Modelo = SRD -> Sin restricciones deseables
    # Modelo = CRD -> Con restricciones deseables
    populate_by_row(prob_lp, data, modelo = sys.argv[2].strip())

    ## Resolvemos el modelo.
    # Algoritmo = BB_BBS -> Branch and Bound con seleccion del proximo nodo mediante Best-Bound Search
    # Algoritmo = BB_DFS -> Branch and Bound con seleccion del proximo nodo mediante Depth-First Search
    # Algoritmo = BC_CC -> Branch and Cut con cortes por cobertura
    solve_lp(prob_lp, algoritmo = sys.argv[3].strip())


if __name__ == '__main__':
    main()