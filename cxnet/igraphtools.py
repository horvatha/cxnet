#!/usr/bin/env python
# coding: utf-8

try:
    from pygraphviz import AGraph
except ImportError:
    print("""igraphtools: I can not found pygraphviz module.""")
import igraph

def igraph_from_dot(file):
    """numbered_graph(file) -> graph

  Input:
    file: the name of the dot-file 

  Output:
    graph: igraph.Graph object. Verticies has the attribute
         "name".
    """
    print("Step 1/3: Reading from dot.")
    a=AGraph(file)
    vertices = a.nodes()
    edges = a.edges()
    numbered_edges = []
    print("Step 2/3: To numbered graph. Be patient...")
    for x, y in edges:
        xx = vertices.index(x)
        yy = vertices.index(y)
        numbered_edges.append((xx,yy))
    print("Step 3/3: To igraph.")
    g=igraph.Graph(len(vertices), numbered_edges)
    g.vs["name"]=vertices
    return g

def igraph_from_vertices_edges(vertices, edges):
    numbered_edges = []
    print("To numbered graph. Be patient...")
    for x, y in edges:
        xx = vertices.index(x)
        yy = vertices.index(y)
        numbered_edges.append((xx,yy))
    print("To igraph.")
    g=igraph.Graph(len(vertices), numbered_edges)
    g.vs["name"]=vertices
    return g

