
# Conjunto de oficinas
set O := { read "oficinas.txt" as "<1s>" };

# Conjunto de centrales operativas
set C := { read "centrales.txt" as "<1s>" };

# Demanda de las oficinas
param dem[O] := read "oficinas.txt" as "<1s> 2n";

# Distancia entre cada oficina y cada central operativa
param dist[O*C] := read "distancias.txt" as "n+";

# x[i,j] = 1 si la oficina i está asignada a la central operativa j
var x[O*C] binary;

# y[j] = 1 si la central operativa j es utilizada
var y[C] binary;

# Minimizamos el costo total total
minimize fobj: sum <i,j> in O*C: (0.017 * dist[i,j] * x[i,j]) + sum <j> in C: (5700 * y[j]);

# Cada oficina debe estar asignada a una central operativa
subto asignacion: forall <i> in O:
    sum <j> in C: x[i,j] == 1;