import collections as co
import itertools as it

def unique(list_):
    return len(set(list_)) == len(list_)

def get_combos(branches):
    by_parent = co.defaultdict(list)

    print(by_parent)
    # for branch in branches:
        # by_parent[branch.p].append(branch)

    combos = it.product(*by_parent.values())

    return it.ifilter(lambda x: unique([b.c for b in x]), combos)

get_combos({"p":[],"c":["a","b","c","d"]})    