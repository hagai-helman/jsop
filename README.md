# JSOP - JSON-Style Object Persistence

**JSOP** is a Python persistence engine designed to efficiently store and access JSON-style data on disk. It simplifies data management using a user-friendly API, making it an ideal choice for applications that need to handle substantial amounts of structured data with ease.

## Key Features

- **Efficient Data Storage:** JSOP is built on the `dbm` module, providing efficient storage capabilities.

- **User-Friendly API:** We've made data management straightforward, so you can get your project up and running with minimal effort.

- **Seamless Migration:** If your existing applications already store data in JSON files, JSOP allows you to migrate with minimal code changes, ensuring a smooth transition.

## Installation

Install JSOP using pip:

```bash
pip3 install jsop
```

## Quick Start

### Creating a New JSOP File

#### Programmatically

```python
import jsop

# Initialize JSOP with your JSON-serializable data.
data = {...}  # Your JSON data here
jsop.JSOP("/path/to/jsop").init(data)
```

#### From the Command Line

```bash
python3 -m jsop init /path/to/jsop /path/to/data.json
```

(If no initial JSON file is provided, the file will be initialized with an empty map.)

### Read and Write

```python
with jsop.JSOP("/path/to/jsop") as data:
    name = data["name"]
    data["age"] = 30
    for friend in data["friends"]:
        print(friend["name"])
```

## Supported Operations

### Assignments

Store JSON-serializable data using simple assignments:

```python
path = "/path/to/jsop"

jsop.JSOP(path).init()      # Initialize with an empty map.

with jsop.JSOP(path) as data:
    data["string"] = "Hello, World!"
    data["boolean"] = True
    data["map"] = {"a": 1, "b": 2, "c": 3}
    data["map"]["d"] = 4
    data["map"]["list"] = [5, 6, 7]
```

The file will be saved when the `with` block exits.

### Accessing Data

Retrieve data of primitive types and get the corresponding Python type:

```python
with jsop.JSOP(path) as data:
    my_string = data["string"]  # type(my_string) is str
    my_int = data["map"]["c"]  # type(my_int) is int
```

When you retrieve a map or a list, you get special objects, named `JDict` and `JList`, respectively.

### Map Operations

With `JDict`, you can perform various operations similar to a Python `dict`:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"]  # type(my_map) is JDict
    
    a = my_map["a"]                  # item access
    my_map["b"] = 3                  # item assignment
    del my_map["c"]                  # item removal
    if "d" in my_map:
        pass                         # using the "in" operator
    length = len(my_map)             # getting map's size
    keys = my_map.keys()             # getting a list of keys
    for key in my_map:
        pass                         # iteration over keys
    if my_map == my_map:
        pass                         # comparison with a JDict
    if my_map == {"a": 1, "b": 3}:
        pass                         # comparison with a Python dict
    my_map.clear()                   # removing all keys from a map
```

You can also convert the map to a regular Python `dict` using the `export()` method:

```python
with jsop.JSOP(path) as data:
    my_map = data["map"].export()  # type(my_map) is dict

    my_map["e"] = 5

    data["map"] = my_map
```

### List Operations

Similarly, the `JList` object supports most operations supported by a Python `list`:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["list"]  # type(my_list) is JList

    for item in my_list:
        pass                         # iteration over items
    my_list.append(8)                # adding an item
    eight = my_list.pop()            # removing (and returning) the last item
    six = my_list[1]                 # item access by index
    my_list[1] = 9                   # item assignment
    my_list.remove(9)                # removing an arbitrary item
    if 8 in my_list:
        pass                         # using the "in" operator
    length = len(my_list)            # getting the list's size
    if my_list == my_list:
        pass                         # comparison with a JList
    if my_list == [5, 6, 7]:
        pass                         # comparison with a Python list
    my_list.clear()                  # removing all items from the list
```

Like in `JDict`, `JList` also supports the `export()` method, which returns a Python `list`:

```python
with jsop.JSOP(path) as data:
    my_list = data["map"]["list"].export()  # type(my_list) is list
```

### Handling References

Be cautious when keeping references to `JDict` and `JList` objects. Unlike Python's regular `dict` and `list` objects, these are references to specific "paths" in the JSOP root object:

```python
with jsop.JSOP(path) as data:
    data["list_of_lists"] = [[1, 2, 3], [4, 5, 6]]

    item = data["list_of_lists"][0]
    # `item` is a reference to the first item of the list under the key "list_of_lists" in `data`.

    del data["list_of_lists"]
    # The "list_of_lists" no longer exists, and `item` becomes an invalid reference.

    print(item[2])
    # This will raise an exception.
```

## Locking

If multiple concurrent processes may access the database simultaneously, you need a locking mechanism to ensure data consistency. Some DBM implementations provide internal locking, while others require an external mechanism like [`filelock`](https://py-filelock.readthedocs.io/).

When you need read-only access, consider using `JSOP(path, readonly=True)` to prevent writing and pass the flag to the DBM implementation.

## Copy and Backup

To create a copy of a JSOP file, it's recommended to export its content to JSON. This reduces storage space and ensures portability across different systems (and specifically, different DBM implementations):

```bash
python3 -m jsop export /path/to/jsop /path/to/copy.json
```

If no JSON file path is given, the result will be printed to the standard output. Dictionaries are sorted by key to ensure efficiency in diff-based backup systems.

## Choosing DBM Implementation

You can choose the DBM implementation to use by overriding the `jsop.dbm` variable. For example:

```python
import jsop
import dbm.gnu

jsop.dbm = dbm.gnu
```

