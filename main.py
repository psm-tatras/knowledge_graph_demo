import networkx as nx

from parse_utils import *
from draw_utils import *


def make_knowledge_graph(file_name):
    f = open(file_name)
    text = f.readlines()
    knowledge_graph = nx.DiGraph()
    for line in text:
        line_doc = nlp(line)
        for sent in line_doc.sents:
            doc = nlp(sent.text)
            keyphrases = get_rule_based_keyphrases(doc)
            root_verb, all_verbs, dep_struct = get_all_verbs(doc)
            main_graph = make_main_graph(dep_struct)
            # draw_html_graph("data/main_graph", main_graph)
            relabel, drop_nodes = find_nodes_to_merge_n_drop(keyphrases, main_graph)
            temp_graph = main_graph.copy()
            temp_graph.remove_nodes_from(drop_nodes)
            merged_graph = nx.relabel_nodes(temp_graph, relabel)
            knowledge_graph = nx.compose(merged_graph,knowledge_graph)
            print(sent)
            print("-------------------------------------------------------")
    return knowledge_graph


kg = make_knowledge_graph("data/sentence.txt")
draw_html_graph("final_graph", kg)
