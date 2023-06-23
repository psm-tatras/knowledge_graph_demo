import spacy
from spacy.matcher import Matcher
import networkx as nx

nlp = spacy.load('en_core_web_lg')
obj_macher = Matcher(nlp.vocab)
stopwords = ["and", "that", "That", "The", "By", "In", "For", "As", "by", "off", "of", "in", "for", "the", "as", "or",
             "a", "A", "an", 'An']


def get_rule_based_keyphrases(doc):
    phrases = []
    rule_1 = [{"POS": "ADJ", "OP": "*"}, {"POS": "PROPN", "OP": "+"}]
    rule_2 = [{"POS": "PROPN", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "OP": "+"}]
    obj_macher.add("pobject_mod", [rule_1, rule_2], greedy="LONGEST")
    matches = obj_macher(doc)
    for m in matches:
        ms = m[1]
        me = m[2]
        # print(doc[ms:me])
        phrases.append(str(doc[ms:me].text))
    return phrases


def dep_tree_structure(doc):
    dep_tree = []
    for token in doc:
        # print(token.text,"\t",token.pos_,"\t",token.dep_,"\t",token.head)
        if token.pos_ != "PUNCT":
            dep_tree.append([token.head.text, token.pos_, token.dep_, token.text])
    return dep_tree


def make_main_graph(dep_structure):
    main_graph = nx.DiGraph()
    for item in dep_structure:
        source = item[0]
        target = item[-1]
        dep = item[-2]
        pos = item[1]
        main_graph.add_edge(target, source)
        nx.set_node_attributes(main_graph, {target: {"pos": pos, "dep": dep}})
    return main_graph


def find_path_between_verbs(verb_1, verb_2, graph):
    path = nx.shortest_path(graph, source=verb_1, target=verb_2)
    return path


def get_all_verbs(doc):
    all_verbs = []
    root_verb = ""
    dep_struct = dep_tree_structure(doc)
    for item in dep_struct:
        pos = item[1]
        word = item[-1]
        if pos == "VERB":
            all_verbs.append(word)
            if item[2] == "ROOT":
                root_verb = word
    return root_verb, all_verbs, dep_struct


def find_nodes_to_merge_n_drop(keyphrases, main_graph):
    relabel = {}
    drop_nodes = []
    for kp in keyphrases:
        merge = []
        all_words = kp.split()
        for wd in all_words:
            try:
                neighbours = main_graph.neighbors(wd)
                flag = True
                for n in neighbours:
                    if n not in all_words:
                        flag = False
                if flag:
                    merge.append(wd)
            except Exception as e:
                continue
        # print(merge)
        representative = list(set(all_words).difference(set(merge)))
        drop_nodes.extend(merge)
        # print(representative)
        for r in representative:
            relabel.update({r: kp})
    all_nodes = list(main_graph.nodes)
    for a_node in all_nodes:
        if a_node in stopwords:
            in_deg = main_graph.in_degree(a_node)
            out_deg = main_graph.out_degree(a_node)
            if in_deg == 0:
                drop_nodes.append(a_node)
    return relabel, drop_nodes
