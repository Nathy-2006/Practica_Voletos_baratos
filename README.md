# Práctica #04 – Árboles y grafos (UEA): Buscador de vuelos baratos

Sistema en Python que modela una red de vuelos ficticia como **grafo ponderado dirigido**
(lista de adyacencia) y encuentra la ruta más barata o más rápida con **Dijkstra**.

## Archivos
- `vuelos_baratos.py` – programa principal (grafo, Dijkstra, BFS, reportería, benchmark, gráfico).
- `vuelos.txt` – base de datos ficticia (14 aeropuertos, 60 vuelos).

## Requisitos
Python 3.10+. Para el gráfico: `pip install matplotlib networkx`.

## Uso
```bash
python vuelos_baratos.py            # menú interactivo
python vuelos_baratos.py --demo     # demostración completa + benchmark
python vuelos_baratos.py --grafico grafo_vuelos.png   # imagen del grafo
```
