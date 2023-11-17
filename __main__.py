#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 09:34:44 2023

@author: sebastianpedraza

Proyecto optmizacion
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from tabulate import tabulate

def solver():
    # Crear un nuevo modelo
    model = gp.Model("Optimizacion_Cafe")

    # Parámetros y datos
    n = 3  # Número de regiones
    m = 2  # Número de mezclas

    # Ingresos por mezcla
    P = [72, 75]  # Precio de venta por lb para Premium y Deluxe

    # Costos por región y mezcla
    C = [[52, 50, 48], [52, 50, 48]]  # Costos por lb para Premium y Deluxe

    # Demanda del mercado
    D = [35000, 25000]  # Demanda para Premium y Deluxe

    # Disponibilidad de café por región
    R = [20000, 25000, 15000]  # Disponibilidad por región (Tolima, Cauca, Eje Cafetero)

    # Porcentajes de cafeína por región
    percent_C = [2.5, 2, 1.5]  # Porcentaje de cafeína por región

    # Variables de decisión
    X = {}
    for i in range(n):
        for j in range(m):
            X[i, j] = model.addVar(vtype=GRB.CONTINUOUS, name=f"X_{i}_{j}")

    # Función objetivo
    model.setObjective(
        gp.quicksum(P[j] * X[i, j] for i in range(n) for j in range(m)) -
        gp.quicksum(C[j][i] * X[i, j] for i in range(n) for j in range(m)),
        sense=GRB.MAXIMIZE
    )

    # Restricciones de demanda del mercado
    for j in range(m):
        model.addConstr(gp.quicksum(X[i, j] for i in range(n)) <= D[j], f"Demanda_{j}")

    # Restricciones de disponibilidad por región
    for i in range(n):
        model.addConstr(gp.quicksum(X[i, j] for j in range(m)) <= R[i], f"Disponibilidad_{i}")


    # Restricciones de porcentaje de cafeína por mezcla
    for j in range(m):
        aux_vars = [model.addVar(vtype=GRB.CONTINUOUS, name=f"Aux_{i}_{j}") for i in range(n)]
        model.addConstr(gp.quicksum(aux_vars) == 1, f"Sum_Aux_{j}")
        for i in range(n):
            model.addConstr(X[i, j] * percent_C[i] >= aux_vars[i] * gp.quicksum(X[i, j] for i in range(n)), f"Porcentaje_Cafeina_{i}_{j}")

    model.params.NonConvex = 2
    model.optimize()

    regiones =  {0: 'Tolima', 1: 'Cauca', 2:'Eje cafetero'}
    mezcla   =  {0: 'Premium', 1: 'Deluxe'}

    solucion = {}
    if model.status == GRB.OPTIMAL:
        for i in range(n):
            for j in range(m):
                solucion[(regiones[i],mezcla[j])] = X[i,j].x

        solucion['Ganancias'] = model.objVal
    else: return None


    df = pd.DataFrame(list(solucion.items()), columns=['(Region, Mezcla)', 'Valor'])
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))








if __name__ == '__main__':
    solver()




