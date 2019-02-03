# JSOP - JSON-Style Object Persistence

**JSOP** is a python module that provides a DBM-based time-efficient persistence for JSON-style data.

It can be used instead of JSON where the amount of data makes the I/O operartions too slow. Also, it is designed to enable easy migration of data in existing applications, with minimal code changes.

## Installation

```bash
pip install jsop
```

## Quickstart Guide

Create a new JSOP file:

```python
# 'data' is any JSON-encodable data.

import jsop

jsop.JSOP("/path/to/file").dump(data)
```


Read and write:

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

jsop.JSOP(path).dump({})

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

However, when you retrieve a map (dictionary) or an array (list), you get special objects, named *JDict* and *JList*, respectively.

With *JDict*, you can do most of the things you can do with a python *dict*:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"]
    # type(my_map) is JDict    
    
    a = my_map["a"]           # item access
    my_map["b"] = 3           # item assignment
    del my_map["c"]           # item removal
    flag = ("d" in my_map)    # using the "in" operator
    length = len(my_map)      # getting map's size
    keys = my_map.keys()      # getting list of keys
    for key in my_map:
        pass                  # iteration over keys
    my_map.clear()            # removing all keys from map
```

Also, you can convert the map to a regular python *dict*, by using the *collect()* method:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"].collect()
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
        pass                  # iteration
    my_array.append(8)        # adding an item
    my_array.remove(8)        # removing an item (note: may be slow for big lists)
    length = len(my_array)    # getting array's size
    my_array.clear()          # removing all items from array
```

Note that indexing is not supported. If you need a list with random access, consider using
a map.

Like as in JDict, JList also supports the *collect()* method, that returns a python *list*:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["array"].collect()
    # type(my_list) is list
```
