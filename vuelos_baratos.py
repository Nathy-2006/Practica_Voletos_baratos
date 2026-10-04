# -*- coding: utf-8 -*-
"""
Nombre: Nathalia Teresa Barreiro Castro "B"
Practica #04 - Arboles y grafos (UEA)
Tema: Encuentro de vuelos baratos a partir de una base de datos ficticia.

Estructura de datos: grafo ponderado dirigido con lista de adyacencia.
Algoritmos: Dijkstra (cola de prioridad con heapq), BFS (minimo de escalas)
y Dijkstra con arreglo O(V^2) para comparar tiempos de ejecucion.
"""
import argparse
import heapq
import random
import time
from collections import defaultdict, deque


class Vuelo:
    """Arista dirigida del grafo."""
    def __init__(self, origen, destino, precio, minutos, aerolinea):
        self.origen = origen
        self.destino = destino
        self.precio = precio
        self.minutos = minutos
        self.aerolinea = aerolinea


class GrafoVuelos:
    def __init__(self):
        self.aeropuertos = {}            
        self.ady = defaultdict(list)     

    def cargar(self, ruta):
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                p = [x.strip() for x in linea.split(",")]
                if p[0] == "AEROPUERTO":
                    self.aeropuertos[p[1]] = (p[2], float(p[3]), float(p[4]))
                    self.ady.setdefault(p[1], [])
                elif p[0] == "VUELO":
                    self.agregar_vuelo(p[1], p[2], float(p[3]), int(p[4]), p[5])

    def agregar_vuelo(self, o, d, precio, minutos, aerolinea):
        self.ady[o].append(Vuelo(o, d, precio, minutos, aerolinea))
        self.ady.setdefault(d, [])

    def num_vuelos(self):
        return sum(len(v) for v in self.ady.values())

    # --- algoritmos ---
    def dijkstra(self, origen, destino, criterio="precio"):
        """Dijkstra con cola de prioridad (heap binario): O((V+E) log V)."""
        peso = (lambda v: v.precio) if criterio == "precio" else (lambda v: v.minutos)
        dist = {n: float("inf") for n in self.ady}
        prev = {}
        dist[origen] = 0
        cola = [(0, origen)]
        expandidos = 0
        while cola:
            d, u = heapq.heappop(cola)
            if d > dist[u]:
                continue
            expandidos += 1
            if u == destino:
                break
            for v in self.ady[u]:
                nd = d + peso(v)
                if nd < dist[v.destino]:
                    dist[v.destino] = nd
                    prev[v.destino] = v
                    heapq.heappush(cola, (nd, v.destino))
        if dist[destino] == float("inf"):
            return None, [], expandidos
        ruta, actual = [], destino
        while actual != origen:
            ruta.append(prev[actual])
            actual = prev[actual].origen
        ruta.reverse()
        return dist[destino], ruta, expandidos

    def dijkstra_arreglo(self, origen, destino):
        """Dijkstra clasico con busqueda lineal del minimo: O(V^2)."""
        nodos = list(self.ady)
        dist = {n: float("inf") for n in nodos}
        dist[origen] = 0
        visitado = set()
        for _ in nodos:
            u, mejor = None, float("inf")
            for n in nodos:                       
                if n not in visitado and dist[n] < mejor:
                    u, mejor = n, dist[n]
            if u is None or u == destino:
                break
            visitado.add(u)
            for v in self.ady[u]:
                if dist[u] + v.precio < dist[v.destino]:
                    dist[v.destino] = dist[u] + v.precio
        return dist[destino]

    def bfs_min_escalas(self, origen, destino):
        """BFS: ruta con menos vuelos (sin considerar precio). O(V+E)."""
        prev = {origen: None}
        cola = deque([origen])
        while cola:
            u = cola.popleft()
            if u == destino:
                break
            for v in self.ady[u]:
                if v.destino not in prev:
                    prev[v.destino] = v
                    cola.append(v.destino)
        if destino not in prev:
            return []
        ruta, actual = [], destino
        while prev[actual] is not None:
            ruta.append(prev[actual])
            actual = prev[actual].origen
        ruta.reverse()
        return ruta

    # --- reporteria ---
    def reporte_aeropuertos(self):
        print(f"\n{'COD':<5}{'CIUDAD':<20}{'SALIDAS':>8}{'LLEGADAS':>10}")
        print("-" * 43)
        llegadas = defaultdict(int)
        for vs in self.ady.values():
            for v in vs:
                llegadas[v.destino] += 1
        for c in sorted(self.aeropuertos):
            print(f"{c:<5}{self.aeropuertos[c][0]:<20}{len(self.ady[c]):>8}{llegadas[c]:>10}")

    def reporte_salidas(self, origen):
        print(f"\nVuelos directos desde {origen} ({self.aeropuertos[origen][0]}):")
        print(f"{'DESTINO':<9}{'PRECIO':>9}{'MIN':>6}  AEROLINEA")
        for v in sorted(self.ady[origen], key=lambda x: x.precio):
            print(f"{v.destino:<9}{v.precio:>9.2f}{v.minutos:>6}  {v.aerolinea}")

    def reporte_matriz(self, codigos):
        print("\nMatriz de adyacencia (precio USD, '-' = sin vuelo directo):")
        print(" " * 6 + "".join(f"{c:>7}" for c in codigos))
        for a in codigos:
            fila = {v.destino: v.precio for v in self.ady[a]}
            print(f"{a:<6}" + "".join(
                f"{fila[b]:>7.0f}" if b in fila else f"{'-':>7}" for b in codigos))

    def reporte_ruta(self, titulo, costo, ruta, unidad):
        print(f"\n{titulo}")
        if not ruta:
            print("  No existe ruta.")
            return
        for v in ruta:
            print(f"  {v.origen} -> {v.destino}  ${v.precio:>7.2f}  {v.minutos:>3} min  {v.aerolinea}")
        print(f"  TOTAL: {costo:.0f} {unidad} | Escalas: {len(ruta) - 1}")


def benchmark(tamanos=(100, 400, 1600, 3200), repeticiones=3):
    """Compara Dijkstra con heap vs arreglo en grafos aleatorios dispersos (E = 5V)."""
    print("\nBENCHMARK (grafos aleatorios, 5 vuelos por aeropuerto)")
    print(f"{'V':>6}{'E':>8}{'Heap (ms)':>12}{'Arreglo (ms)':>14}{'Speed-up':>10}")
    random.seed(42)
    filas = []
    for n in tamanos:
        g = GrafoVuelos()
        for i in range(n):
            g.ady.setdefault(f"N{i}", [])
        for i in range(n):
            for _ in range(5):
                j = random.randrange(n)
                if j != i:
                    g.agregar_vuelo(f"N{i}", f"N{j}", random.randint(30, 500), 60, "X")
        t_heap = t_arr = 0.0
        for _ in range(repeticiones):
            t0 = time.perf_counter(); g.dijkstra("N0", f"N{n-1}"); t_heap += time.perf_counter() - t0
            t0 = time.perf_counter(); g.dijkstra_arreglo("N0", f"N{n-1}"); t_arr += time.perf_counter() - t0
        t_heap = t_heap / repeticiones * 1000
        t_arr = t_arr / repeticiones * 1000
        filas.append((n, g.num_vuelos(), t_heap, t_arr))
        print(f"{n:>6}{g.num_vuelos():>8}{t_heap:>12.3f}{t_arr:>14.3f}{t_arr / t_heap:>9.1f}x")
    return filas


def grafico(g, ruta, archivo):
    """Dibuja el grafo con matplotlib/networkx y resalta la ruta mas barata."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import networkx as nx
    G = nx.DiGraph()
    for c in g.aeropuertos:
        G.add_node(c)
    for vs in g.ady.values():
        for v in vs:
            G.add_edge(v.origen, v.destino, precio=v.precio)
    pos = nx.spring_layout(G.to_undirected(), seed=7, k=1.6, iterations=200)  
    aristas_ruta = [(v.origen, v.destino) for v in ruta]
    nodos_ruta = {n for e in aristas_ruta for n in e}
    fig, ax = plt.subplots(figsize=(11, 7))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#c5c9d1", arrows=True,
                           arrowsize=8, width=0.8, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_ruta, edge_color="#d62828",
                           width=3, arrows=True, arrowsize=18, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=650,
                           node_color=["#f77f00" if n in nodos_ruta else "#457b9d" for n in G])
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_color="white", font_weight="bold")
    ax.set_title("Red de vuelos ficticia - ruta mas barata resaltada en rojo")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(archivo, dpi=130)
    plt.close(fig)


def menu(g):
    while True:
        print("\n=== BUSCADOR DE VUELOS BARATOS ===")
        print("1) Aeropuertos   2) Vuelos desde un aeropuerto   3) Buscar ruta mas barata")
        print("4) Ruta mas rapida   5) Matriz de adyacencia   6) Benchmark   0) Salir")
        op = input("Opcion: ").strip()
        if op == "0":
            break
        elif op == "1":
            g.reporte_aeropuertos()
        elif op == "2":
            g.reporte_salidas(input("Origen (ej. UIO): ").strip().upper())
        elif op in ("3", "4"):
            o = input("Origen: ").strip().upper()
            d = input("Destino: ").strip().upper()
            if o not in g.aeropuertos or d not in g.aeropuertos:
                print("Codigo no valido.")
                continue
            crit = "precio" if op == "3" else "duracion"
            costo, ruta, _ = g.dijkstra(o, d, crit)
            g.reporte_ruta(f"Ruta optima por {crit}", costo, ruta, "USD" if crit == "precio" else "min")
        elif op == "5":
            g.reporte_matriz(sorted(g.aeropuertos))
        elif op == "6":
            benchmark()


def demo(g):
    print("=" * 60)
    print("DEMO - Practica #04: Buscador de vuelos baratos (Dijkstra)")
    print("=" * 60)
    print(f"Base de datos cargada: {len(g.aeropuertos)} aeropuertos, {g.num_vuelos()} vuelos")
    g.reporte_aeropuertos()
    g.reporte_salidas("MCH")
    g.reporte_matriz(["MCH", "GYE", "UIO", "BOG", "PTY", "MIA"])

    consultas = [("MCH", "MAD"), ("GYE", "MIA"), ("UIO", "MAD")]
    for o, d in consultas:
        t0 = time.perf_counter()
        costo, ruta, exp = g.dijkstra(o, d, "precio")
        ms = (time.perf_counter() - t0) * 1000
        g.reporte_ruta(f"[{o} -> {d}] Ruta mas BARATA (Dijkstra, {ms:.3f} ms, {exp} nodos expandidos)",
                       costo, ruta, "USD")
        cr, rr, _ = g.dijkstra(o, d, "duracion")
        g.reporte_ruta(f"[{o} -> {d}] Ruta mas RAPIDA (Dijkstra por duracion)", cr, rr, "min")
        rb = g.bfs_min_escalas(o, d)
        g.reporte_ruta(f"[{o} -> {d}] Menos escalas (BFS)", sum(v.precio for v in rb), rb, "USD")
        directo = [v for v in g.ady[o] if v.destino == d]
        if directo:
            print(f"  (Vuelo directo existente: ${directo[0].precio:.2f}; ahorro con escalas: "
                  f"${directo[0].precio - costo:.2f})")


    ok = all(abs(g.dijkstra(o, d)[0] - g.dijkstra_arreglo(o, d)) < 1e-9
             for o in g.aeropuertos for d in g.aeropuertos if o != d)
    print(f"\nVerificacion Dijkstra(heap) == Dijkstra(arreglo) en todos los pares: {ok}")
    return benchmark()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--archivo", default="vuelos.txt")
    ap.add_argument("--demo", action="store_true", help="ejecuta la demostracion sin menu")
    ap.add_argument("--grafico", metavar="PNG", help="genera imagen del grafo (MCH->MAD)")
    a = ap.parse_args()
    g = GrafoVuelos()
    g.cargar(a.archivo)
    if a.grafico:
        _, ruta, _ = g.dijkstra("MCH", "MAD")
        grafico(g, ruta, a.grafico)
        print("Grafico guardado en", a.grafico)
    if a.demo:
        demo(g)
    elif not a.grafico:
        menu(g)
