import numpy as np
import pandas as pd

# Fijar semilla para reproducibilidad
np.random.seed(42)

# Configuración del dominio universitario sintético
carreras = [
    "Ingeniería Informática",
    "Ingeniería Industrial",
    "Licenciatura en Sistemas",
]
anios = [1, 2, 3, 4, 5]

# Crear un catálogo de materias (nodos del grafo)
materias = []
materia_id = 1

for carrera in carreras:
    for anio in anios:
        # Generar 3 materias por año y carrera
        for j in range(1, 4):
            materias.append(
                {
                    "materia_id": f"MAT_{materia_id:03d}",
                    "carrera": carrera,
                    "anio": anio,
                    "nombre": f"{carrera.split()[0]} - Año {anio} - Mat {j}",
                }
            )
            materia_id += 1

df_materias = pd.DataFrame(materias)

# Generar todos los pares de materias no repetidos (combinaciones simples)
pares = []
n_materias = len(df_materias)

for i in range(n_materias):
    for j in range(i + 1, n_materias):
        m1 = df_materias.iloc[i]
        m2 = df_materias.iloc[j]

        misma_carrera = bool(m1["carrera"] == m2["carrera"])
        mismo_anio = bool(m1["anio"] == m2["anio"])

        # Lógica sintética basada en probabilidad/relevancia académica
        if misma_carrera and mismo_anio:
            # Alto solapamiento de estudiantes
            base_estudiantes = np.random.randint(40, 120)
            prob_conflicto_base = 0.85
        elif misma_carrera and abs(m1["anio"] - m2["anio"]) == 1:
            # Solapamiento moderado (estudiantes recursantes o adelantados)
            base_estudiantes = np.random.randint(10, 45)
            prob_conflicto_base = 0.50
        elif misma_carrera:
            # Poca interacción (diferencia de 2 o más años en la misma carrera)
            base_estudiantes = np.random.randint(0, 15)
            prob_conflicto_base = 0.20
        else:
            # Distinta carrera (carreras cruzadas, materias electivas/básicas)
            if mismo_anio and (m1["anio"] in [1, 2]):
                # Materias básicas comunes (Ej: Matemática, Física)
                base_estudiantes = np.random.randint(15, 60)
                prob_conflicto_base = 0.60
            else:
                base_estudiantes = np.random.randint(0, 8)
                prob_conflicto_base = 0.05

        # Añadir ruido aleatorio razonable
        cant_estudiantes_compartidos_historico = int(
            base_estudiantes * np.random.uniform(0.8, 1.2)
        )

        # Determinar variable de regresión: cant_estudiantes_afectados
        factor_conflicto = np.random.uniform(0.3, 0.95)
        cant_estudiantes_afectados = int(
            cant_estudiantes_compartidos_historico * factor_conflicto
        )

        # Determinar variable de clasificación: hubo_conflicto (según un umbral o probabilidad)
        hubo_conflicto = bool(
            cant_estudiantes_afectados > 10
            or (np.random.rand() < prob_conflicto_base)
        )

        pares.append(
            {
                "materia_id_1": m1["materia_id"],
                "materia_id_2": m2["materia_id"],
                "cant_estudiantes_compartidos_historico": cant_estudiantes_compartidos_historico,
                "mismo_anio": mismo_anio,
                "misma_carrera": misma_carrera,
                "cant_estudiantes_afectados": cant_estudiantes_afectados,
                "hubo_conflicto": hubo_conflicto,
            }
        )

df_dataset = pd.DataFrame(pares)

# Guardar a archivo CSV
df_dataset.to_csv("dataset_mesas_examen.csv", index=False)
print(f"Dataset generado exitosamente con {len(df_dataset)} filas/pares.")