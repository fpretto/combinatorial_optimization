def generate_instance(nombre_instancia, cant_trabajadores, cant_ordenes, beneficio_min, beneficio_max,
                      trab_necesarios_min, trab_necesarios_max, cant_conflictos_trabajadores,
                      cant_ordenes_correlativas, cant_ordenes_conflictivas, cant_ordenes_repetitivas):
    import random

    f = open(nombre_instancia + ".txt","w+")

    f.write(str(cant_trabajadores) + '\n')
    f.write(str(cant_ordenes) + '\n')

    for i in range(cant_ordenes):
        f.write(str(i) + ' ')
        f.write(str(random.randint(beneficio_min, beneficio_max)) + ' ')
        f.write(str(random.randint(trab_necesarios_min, trab_necesarios_max)) + '\n')

    # Trabajadores Conflictivos
    f.write(str(cant_conflictos_trabajadores) + '\n')

    for i in range(cant_conflictos_trabajadores):
        lista = list(range(cant_trabajadores))
        trab1 = random.choice(lista)
        f.write(str(trab1) + ' ')

        lista.remove(trab1)
        trab2 = random.choice(lista)
        f.write(str(trab2) + '\n')

    # Ordenes Correlativas
    f.write(str(cant_ordenes_correlativas) + '\n')

    for i in range(cant_ordenes_correlativas):
        lista = list(range(cant_ordenes))
        ord1 = random.choice(lista)
        f.write(str(ord1) + ' ')

        lista.remove(ord1)
        ord2 = random.choice(lista)
        f.write(str(ord2) + '\n')

    # Ordenes Conflictivas
    f.write(str(cant_ordenes_conflictivas) + '\n')

    for i in range(cant_ordenes_conflictivas):
        lista = list(range(cant_ordenes))
        ord1 = random.choice(lista)
        f.write(str(ord1) + ' ')

        lista.remove(ord1)
        ord2 = random.choice(lista)
        f.write(str(ord2) + '\n')


    # Ordenes Repetitivas
    f.write(str(cant_ordenes_repetitivas) + '\n')

    for i in range(cant_ordenes_repetitivas):
        lista = list(range(cant_ordenes))
        ord1 = random.choice(lista)
        f.write(str(ord1) + ' ')

        lista.remove(ord1)
        ord2 = random.choice(lista)
        f.write(str(ord2) + '\n')

    f.close()

### Generar instancia
location = 'C:/Repo/Github/combinatorial_optimization/field_service/data/'

generar_instancia(nombre_instancia              = location + 'input_field_service_3',
                  cant_trabajadores             = 100,
                  cant_ordenes                  = 300,
                  beneficio_min                 = 500,
                  beneficio_max                 = 50000,
                  trab_necesarios_min           = 1,
                  trab_necesarios_max           = 15,
                  cant_conflictos_trabajadores  = 10,
                  cant_ordenes_correlativas     = 10,
                  cant_ordenes_conflictivas     = 10,
                  cant_ordenes_repetitivas      = 10)