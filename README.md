# JSOP - JSON-Style Object Persistence

**JSOP** is a python module that provides a DBM-based time-efficient persistence for JSON-style data.

It can be used instead of JSON where the amount of data makes the I/O operartions too slow. Also, it is designed to enable easy migration of data in existing applications, with minimal code changes.

## Installation

```bash
pip3 install jsop
```

## Quickstart Guide

### Creating a new JSOP file

Programmatically :

```python
# 'data' is any JSON-encodable data.

import jsop

jsop.JSOP("/path/to/file").init(data)
```

Or from the command line:

```bash
python3 -m jsop init /path/to/file /path/to/data.json
```

(If an initial JSON file is not given, the file will be initialized with an empty dictionary.)

### Read and Write

```python
with jsop.JSOP("/path/to/file") as data:
    name = data["name"]
    data["age"] = 30
    for friend in data["friends"]:
        print(friend["name"])
```

## Supported Operations

You can store any JSON-encodable data with JSOP using simple assignment. For example:

```python
path = "/path/to/file"

jsop.JSOP(path).init()      # initalize with an empty dictionary.

with jsop.JSOP(path) as data:
    data["string"] = "Hello, World!"
    data["boolean"] = True
    data["map"] = {"a": 1, "b": 2, "c": 3}
    data["map"]["d"] = 4
    data["map"]["array"] = [5,6,7]
```

When you retrieve data of primitive types, you just get the corresponding python type:

```python
with jsop.JSOP(path) as data:
    my_string = data["string"]
    # type(my_string) is str

    my_int = data["map"]["c"]
    # type(my_int) is int
```

However, when you retrieve dictionary or a list, you get special objects, named *JDict* and *JList*, respectively.

With *JDict*, you can do most of the things you can do with a python *dict*:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"]
    # type(my_map) is JDict
    
    a = my_map["a"]                  # item access
    my_map["b"] = 3                  # item assignment
    del my_map["c"]                  # item removal
    flag = ("d" in my_map)           # using the "in" operator
    length = len(my_map)             # getting map's size
    keys = my_map.keys()             # getting list of keys
    for key in my_map:
        pass                         # iteration over keys
    my_map.clear()                   # removing all keys from map
```

Also, you can convert the map to a regular python *dict*, by using the *export()* method:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"].export()
    # type(my_map) is dict

    my_map["e"] = 5

    data["map"] = my_map
```

Note that like a JSON map, the keys in a JSOP map are always strings. If a different object is given as a key, it is converted to a string.

The *JList* object supports significantly less operations than a python *list*:

```python
with jsop.JSOP(path) as data:
    my_array = data["map"]["array"]
    # type(my_array) is JList

    for item in my_array:
        pass                         # iteration over items
    my_array.append(8)               # adding an item
    my_array.remove(8)               # removing an item (note: this method actually iterates over all items)
    length = len(my_array)           # getting array's size
    my_array.clear()                 # removing all items from array

    for cell in my_array.cells():    # iteration over cells
        my_value = cell.value()      # getting the value stored in a cell
        cell.put("hello")            # setting the value stored in a cell
        cell.remove()                # deleting a cell

```

Note that indexing is not supported. If you need a list with random access, consider using
a map.

Like as in JDict, JList also supports the *export()* method, that returns a python *list*:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["array"].export()
    # type(my_list) is list
```

## Copy and Backup

In order to create copy a JSOP file, it is recommended to export its content to JSON, since JSON files take less space.

This can be done from the command line:

```bash
python3 -m jsop export /path/to/file /path/to/backup.json
```

If JSON file path is not given, the result will be printed to the standard output.
