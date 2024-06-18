from jsonmerge import merge
import json


def toFile(filename, data):
    with open(filename, "w", encoding="utf8") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))

def loadFromFile(filename):
    with open(filename, "r") as f:
        data = json.loads(f.read())
    return data

base = loadFromFile(input("(tmp.po.a.tmp) "))
head = loadFromFile(input("(tmp.po.b.tmp) "))

#result = merge(base, head)
result = merge(head, base)

toFile(input("(tmp.po.automerge.tmp) "), result)
