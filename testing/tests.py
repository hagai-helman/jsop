from jsop import JSOP
from testing import Testing
from tempfile import gettempdir
import subprocess
import json
import os
import random

FILENAME = "".join((random.choice("0123456789abcdef") for i in range(8)))
JSOP_PATH = os.path.join(gettempdir(), FILENAME + ".jsop")
JSON_PATH = os.path.join(gettempdir(), FILENAME + ".json")
STDOUT_PATH = os.path.join(gettempdir(), FILENAME + ".stdout")

def TEST_DATA():
    return {"int": 4, "map": {"a": 4, "list": [1,2,3]}, "list": [1,6,5], "7": 7, "null": None, "bool": True, "bool2": False}

testing = Testing()

@testing.test("init and export")
def test_init_and_export(ctx):
    ctx.stage("initialize empty db")
    JSOP(JSOP_PATH).init()
    ctx.stage("initialize and export empty db")
    assert JSOP(JSOP_PATH).export() == {}

    ctx.stage("initialize db with data")
    JSOP(JSOP_PATH).init(TEST_DATA())
    ctx.stage("initialize and export db with data")
    assert JSOP(JSOP_PATH).export() == TEST_DATA()
    

@testing.test("command line interface")
def test_cli(ctx):
    ctx.stage("initialize empty db")
    subprocess.run(["python3", "-m", "jsop", "init", JSOP_PATH])
    assert JSOP(JSOP_PATH).export() == {}

    ctx.stage("initialize db with data")
    json.dump(TEST_DATA(), open(JSON_PATH, "w"))
    subprocess.run(["python3", "-m", "jsop", "init", JSOP_PATH, JSON_PATH])
    assert JSOP(JSOP_PATH).export() == TEST_DATA()

    ctx.stage("export db to file")
    expected_value = TEST_DATA()
    del expected_value["int"]
    with JSOP(JSOP_PATH) as data:
        del data["int"]
    subprocess.run(["python3", "-m", "jsop", "export", JSOP_PATH, JSON_PATH])
    result = json.load(open(JSON_PATH))
    assert result == expected_value

    ctx.stage("export db to stdout")
    expected_value["int2"] = 5
    with JSOP(JSOP_PATH) as data:
        data["int2"] = 5
    subprocess.run(["python3", "-m", "jsop", "export", JSOP_PATH], stdout = open(JSON_PATH, "wb"))
    result = json.load(open(JSON_PATH))
    assert result == expected_value


@testing.test("dictionary test")
def test_dict(ctx):
    JSOP(JSOP_PATH).init(TEST_DATA())
    ctx.stage("item access (primitive types)")
    with JSOP(JSOP_PATH) as data:
        assert data["int"] == 4
        assert data["bool"] == True
        assert data["bool2"] == False
        assert data["null"] == None

    ctx.stage("item access (a dictionary)")
    with JSOP(JSOP_PATH) as data:
        assert data["map"].export() == {"a": 4, "list": [1,2,3]}

    ctx.stage("item access (a list)")
    with JSOP(JSOP_PATH) as data:
        assert data["list"].export() == [1,6,5]

    ctx.stage("item assignment (primitive types)")
    with JSOP(JSOP_PATH) as data:
        data["int"] = 7
        data["bool"] = False
        data["bool2"] = True
        data["string"] = "Hello, World!"
    with JSOP(JSOP_PATH) as data:
        assert data["int"] == 7
        assert data["bool"] == False
        assert data["bool2"] == True
        assert data["string"] == "Hello, World!"

    ctx.stage("item assignment (a dictionry)")
    with JSOP(JSOP_PATH) as data:
        data["map2"] = {"aaa": 1, "bbb": [2, 3]}
    with JSOP(JSOP_PATH) as data:
        assert data["map2"].export() == {"aaa": 1, "bbb": [2, 3]}

    ctx.stage("item assignment (a list)")
    with JSOP(JSOP_PATH) as data:
        data["list2"] = ["A", "B", {"C": 8}]
    with JSOP(JSOP_PATH) as data:
        assert data["list2"].export() == ["A", "B", {"C": 8}]

    ctx.stage("item removal")
    with JSOP(JSOP_PATH) as data:
        del data["map2"]["bbb"]
    with JSOP(JSOP_PATH) as data:
        assert data["map2"].export() == {"aaa": 1}

    ctx.stage("the 'in' operator")
    with JSOP(JSOP_PATH) as data:
        assert "aaa" in data["map2"]
        assert "bbb" not in data["map2"]
        assert "ccc" not in data["map2"]
    
    # int map list 7 null bool bool2 string map2 list2

    ctx.stage("getting dictionary's size")
    with JSOP(JSOP_PATH) as data:
        assert len(data) == 10
        assert len(data["map2"]) == 1

    ctx.stage("the keys() method")
    with JSOP(JSOP_PATH) as data:
        keys = data.keys()
        assert set(keys) == set(["int", "map", "list", "7", "null", "bool", "bool2", "string", "map2", "list2"])

    ctx.stage("iteration over keys")
    with JSOP(JSOP_PATH) as data:
        result = []
        for key in data:
            result.append(key)
        assert len(result) == 10
        assert set(result) == set(keys)

    ctx.stage("key which is not a string")
    with JSOP(JSOP_PATH) as data:
        assert data[7] == 7
        data[7] = 8
    with JSOP(JSOP_PATH) as data:
        assert data[7] == 8

    ctx.stage("clear")
    with JSOP(JSOP_PATH) as data:
        data.clear()
    with JSOP(JSOP_PATH) as data:
        assert data.export() == {}

@testing.test("list test")
def test_list(ctx):
    JSOP(JSOP_PATH).init([])
    
    ctx.stage("appending items")
    with JSOP(JSOP_PATH) as data:
        data.append(1)
        data.append("hello")
        data.append([1,2,3])
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, "hello", [1,2,3]]

    ctx.stage("prepending items")
    with JSOP(JSOP_PATH) as data:
        data.prepend(5)
        data.prepend("this")
        data.prepend({"foo": "bar"})
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [{"foo": "bar"}, "this", 5, 1, "hello", [1,2,3]]

    JSOP(JSOP_PATH).init([1, "hello", [1,2,3]])

    ctx.stage("iteration over items")
    with JSOP(JSOP_PATH) as data:
        result = []
        for item in data:
            result.append(item)
        assert len(result) == 3
        assert result[:2] == [1, "hello"]
        assert type(result[2]) == type(data)
        assert result[2].export() == [1,2,3]

    ctx.stage("using the 'in' operator")
    with JSOP(JSOP_PATH) as data:
        assert 1 in data
        assert "hello" in data
        assert 2 not in data
        assert [1,2,3] in data
        assert [4,5,6] not in data

    ctx.stage("remove")
    with JSOP(JSOP_PATH) as data:
        data.remove("hello")
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, [1,2,3]]
    with JSOP(JSOP_PATH) as data:
        data.append(2)
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, [1,2,3], 2]
    with JSOP(JSOP_PATH) as data:
        data.remove(2)
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, [1,2,3]]
    with JSOP(JSOP_PATH) as data:
        data.remove(1)
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [[1,2,3]]

    ctx.stage("getting list's size")
    JSOP(JSOP_PATH).init([1, "hello", [1,2,3]])
    with JSOP(JSOP_PATH) as data:
        assert len(data) == 3

    ctx.stage("getting cell's value")
    with JSOP(JSOP_PATH) as data:
        result = []
        for cell in data.cells():
            result.append(cell.value())
        assert len(result) == 3
        assert result[:2] == [1, "hello"]
        assert type(result[2]) == type(data)
        assert result[2].export() == [1,2,3]

    ctx.stage("setting cell's value")
    with JSOP(JSOP_PATH) as data:
        for (i, cell) in enumerate(data.cells()):
            if i == 1:
                cell.put("world")
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, "world", [1,2,3]]

    ctx.stage("removing a cell")
    with JSOP(JSOP_PATH) as data:
        for (i, cell) in enumerate(data.cells()):
            if i == 1:
                cell.remove()
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [1, [1,2,3]]

    with JSOP(JSOP_PATH) as data:
        for (i, cell) in enumerate(data.cells()):
            if i == 0:
                cell.remove()
    with JSOP(JSOP_PATH) as data:
        assert data.export() == [[1,2,3]]

    with JSOP(JSOP_PATH) as data:
        for (i, cell) in enumerate(data.cells()):
            if i == 0:
                cell.remove()
    with JSOP(JSOP_PATH) as data:
        assert data.export() == []

    ctx.stage("clear")
    JSOP(JSOP_PATH).init([1, "hello", [1,2,3]])
    with JSOP(JSOP_PATH) as data:
        data.clear()
    with JSOP(JSOP_PATH) as data:
        assert data.export() == []


if __name__ == "__main__":
    testing.run_all()

