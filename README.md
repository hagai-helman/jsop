# JSOP - JSON-Style Object Persistence

**JSOP** is a persistence engine that allows an application to store a large amount of JSON-style data on disk, but to access it in an efficient way.

It is based on the ```dbm``` module, but offers a much easier-to-use API.

JSOP is also designed to enable easy migration of data in existing applications, that already store data in JSON files, with minimal changes to the code.

## Installation

```bash
pip3 install jsop
```

## Quickstart Guide

### Creating a new JSOP file

Programmatically :

```python
# 'data' is any JSON-serializable data.

import jsop

jsop.JSOP("/path/to/jsop").init(data)
```

Or from the command line:

```bash
python3 -m jsop init /path/to/jsop /path/to/data.json
```

(If an initial JSON file is not given, the file will be initialized with an empty map.)

### Read and Write

```python
with jsop.JSOP("/path/to/jsop") as data:
    name = data["name"]
    data["age"] = 30
    for friend in data["friends"]:
        print(friend["name"])
```

## Supported Operations

You can store any JSON-serializable data with JSOP using simple assignment. For example:

```python
path = "/path/to/jsop"

jsop.JSOP(path).init()      # initalize with an empty map.

with jsop.JSOP(path) as data:
    data["string"] = "Hello, World!"
    data["boolean"] = True
    data["map"] = {"a": 1, "b": 2, "c": 3}
    data["map"]["d"] = 4
    data["map"]["list"] = [5,6,7]
```

The file will be saved once the ```with``` block exits.

When you retrieve data of primitive types, you just get the corresponding python type:

```python
with jsop.JSOP(path) as data:
    my_string = data["string"]
    # type(my_string) is str

    my_int = data["map"]["c"]
    # type(my_int) is int
```

However, when you retrieve a map or a list, you get special objects, named ```JDict``` and ```JList```, respectively.

With ```JDict```, you can do most of the things you can do with a python ```dict```:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"]
    # type(my_map) is JDict
    
    a = my_map["a"]                  # item access
    my_map["b"] = 3                  # item assignment
    del my_map["c"]                  # item removal
    if "d" in my_map:
        pass                         # using the "in" operator
    length = len(my_map)             # getting map's size
    keys = my_map.keys()             # getting list of keys
    for key in my_map:
        pass                         # iteration over keys
    my_map.clear()                   # removing all keys from map
```

Also, you can convert the map to a regular python ```dict```, by using the ```export()``` method:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"].export()
    # type(my_map) is dict

    my_map["e"] = 5

    data["map"] = my_map
```

Note that like a JSON map, the keys in a JSOP map are always strings. If a different object is given as a key, it is converted to a string.

The ```JList``` object supports significantly less operations than a python ```list```:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["list"]
    # type(my_list) is JList

    for item in my_list:
        pass                         # iteration over items
    my_list.append(8)                # adding an item (at the end)
    my_list.prepend(8)               # adding an item (at the beginning)
    my_list.remove(8)                # removing an item (note: this method actually iterates over all items)
    if 8 in my_list:
        pass                         # using the "in" operator (note: this method also iterates over all items)
    length = len(my_list)            # getting list's size
    my_list.clear()                  # removing all items from list

    for cell in my_list.cells():     # iteration over cells
        my_value = cell.value()      # getting the value stored in a cell
        cell.put("hello")            # setting the value stored in a cell
        cell.remove()                # deleting a cell

```

Note that indexing is not supported. If you need a list with random access, consider using a map instead.

Like as in ```JDict```, ```JList``` also supports the ```export()``` method, which returns a python ```list```:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["list"].export()
    # type(my_list) is list
```

## Copy and Backup

In order to create copy a JSOP file, it is recommended to export its content to JSON. The reason is that JSON files take less space, and also because of partability: this practice avoids problems resulting from the use of different ```dbm``` implementations on different systems.

This can be done from the command line:

```bash
python3 -m jsop export /path/to/jsop /path/to/copy.json
```

If JSON file path is not given, the result will be printed to the standard output.
