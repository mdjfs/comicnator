import random


def Seleccion(exclusion_fila, exclusion_columna, incert, numbers):
    rownumber = numbers[0]
    columnumber = numbers[1]
    i = 0
    seleccion = [0, 0]
    a = random.randint(2, columnumber - 2)
    b = random.randint(1, rownumber)
    seleccion[0] = a
    seleccion[1] = b
    while exclusion_columna[a] is True or exclusion_fila[b] is True:
        i = i + 1
        if incert is False:
            a = random.randint(2, columnumber - 2)
            b = random.randint(1, rownumber)
            seleccion[0] = a
            seleccion[1] = b
        else:
            b = random.randint(1, rownumber)
            a = columnumber - 1
            seleccion[0] = a
            seleccion[1] = b
        if i > 3000:
            incert = True
        if i > 200000:
            seleccion = None
            break
    return seleccion
