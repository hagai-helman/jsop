from jsop import JSOP

JSOP("/tmp/jsop_test.jsop").dump({})

with JSOP("/tmp/jsop_test.jsop") as data:
    data["int"] = 3
    data["int2"] = 8
    data["null"] = None
    data["map"] = {"a": 4}
    data["list"] = [1,2,3]
    data[7] = 7

with JSOP("/tmp/jsop_test.jsop") as data:
    data["int"] += len(data["map"])
    del data["int2"]
    data["bool"] = "a" in data["map"]
    data["bool2"] = "b" in data["map"]
    data["map"]["list"] = data["list"]
    data["list"].append(4)
    data["list"].remove(2)
    data["list"].append(5)

with JSOP("/tmp/jsop_test.jsop") as data:
    assert data.export() == {"int": 4, "map": {"a": 4, "list": [1,2,3]}, "list": [1,3,4,5], "7": 7, "null": None, "bool": True, "bool2": False}
    assert data.keys() == ["int", "null", "map", "list", "7", "bool", "bool2"]
    for (a, b) in zip(data, data.keys()):
        assert a == b
    assert len(data["list"]) == 4
    for (a, b) in zip(data["list"], [1,3,4,5]):
        assert a == b
    for cell in data["list"].cells():
        if cell.value() == 3:
            cell.put(6)
        elif cell.value() == 4:
            cell.remove()

assert JSOP("/tmp/jsop_test.jsop").load() == {"int": 4, "map": {"a": 4, "list": [1,2,3]}, "list": [1,6,5], "7": 7, "null": None, "bool": True, "bool2": False}

with JSOP("/tmp/jsop_test.jsop") as data:
    data["list"].clear()
    data["map"].clear()


with JSOP("/tmp/jsop_test.jsop") as data:
    assert data["list"].export() == []
    assert data["map"].export() == {}

from subprocess import run
import json

run(["python3", "-m", "jsop", "init", "/tmp/jsop_test.jsop"])
assert JSOP("/tmp/jsop_test.jsop").export() == {}
json.dump({"int": 4, "map": {"a": 4, "list": [1,2,3]}, "list": [1,6,5], "7": 7, "null": None, "bool": True, "bool2": False}, open("/tmp/jsop_test.json", "w"))
run(["python3", "-m", "jsop", "init", "/tmp/jsop_test.jsop", "/tmp/jsop_test.json"])

with JSOP("/tmp/jsop_test.jsop") as data:
    data["int"] = 10
    data["list"].append(9)

assert JSOP("/tmp/jsop_test.jsop").export() == {"int": 10, "map": {"a": 4, "list": [1,2,3]}, "list": [1,6,5,9], "7": 7, "null": None, "bool": True, "bool2": False}

run(["python3", "-m", "jsop", "export", "/tmp/jsop_test.jsop", "/tmp/jsop_test.json"])

assert json.load(open("/tmp/jsop_test.json")) == {"int": 10, "map": {"a": 4, "list": [1,2,3]}, "list": [1,6,5,9], "7": 7, "null": None, "bool": True, "bool2": False}

with JSOP("/tmp/jsop_test.jsop") as data:
    del data["map"]

with open("/tmp/jsop_test.json", "wb") as fp:
    run(["python3", "-m", "jsop", "export", "/tmp/jsop_test.jsop"], stdout = fp)

assert json.load(open("/tmp/jsop_test.json")) == {"int": 10, "list": [1,6,5,9], "7": 7, "null": None, "bool": True, "bool2": False}
    
