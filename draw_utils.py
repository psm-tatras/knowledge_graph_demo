from pyvis.network import Network


def draw_html_graph(graph_name,graph):
    nt = Network(directed=True)
    nt.from_nx(graph)
    nt.show("%s.html"%graph_name, notebook=False)