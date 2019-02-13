# The JSOP Data Format - Version 1.0

This document describes the **JSOP 1.0** data format.

This format is designed to store "JSON-Style Objects". That means that any JSON-serializable object should be convertable to a JSOP database, and vice-versa. 

However, a JSOP database allows random access to data, without the need to load or rewrite the whole file for every read/write operation.


## The Basics

JSOP is not a file-format per-se. It is a structure for a **DBM** database.

DBM is a database that stores a mapping of byte-string keys to byte-string values, and provides a dictionary-like API. There are several implementations of DBM, and each one stores the database in a different way.

JSOP is built upon the DBM API, and it's independent of the chosen DBM implementation.

When a JSOP database in initialized or opened by the Python ```jsop``` library, Python's built-in ```dbm``` module is used to choose or determine the DBM implementation used.

JSOP actually uses DBM to map lists of unicode strings, to JSON-style objects.

The list of unicode strings is encoded to a byte-string in the following way:

* UTF-8 encode each string;
* Concatenate the strings, seperating them with a 0xFF byte (which never appears on UTF-8).

The JSON-style object is simply serialized using JSON, and the result is UTF-8 encoded.

For the rest of this document, we will assume we have a mapping that maps each **address** (a list of unicode strings), to a **value** (a JSON-style object). For an address ```addr``` we will denote the value as ```DBM[addr]```.


## The Format Versioning

The JSOP database declares a format version, to ensure compatability between a the data format, and the software handling it. 

The data format versionis stored in three addresses:

* ```["m", "format-name"]```
* ```["m", "format-version-major"]```
* ```["m", "format-version-minor"]```

The value of ```DBM[["m", "format-name"]]``` is always "JSOP". This should be changed only for forks of the JSOP project.

The value of ```DBM[["m", "format-version-major"]]``` is currently 1. This integer will be increased if a new version of the data format will break backward-compatibility.

The value of ```DBM[["m", "format-version-minor"]]``` is currently 0. This integer will be increased in future backward-compatible data format versions.

If a library supports a specific version, it should also be able to handle every earlier minor version of the same major version.


## How Objects Are Stored

Every object has an address, ```addr```. 

If the object is of a primitive data type (a number, a string, a boolean or null), then it is simply stored mapped to this address. Hence, the value of ```DBM[addr]``` will be the object itself. 

If the object is a map or a list, the value mapped to the address will be ```{}``` (an empty map) or ```[]``` (an empty list), respectively. The actual data will be stored mapped to other addresses, derived from the object's address.


### Maps

Let a map have the address ```addr```.

As we have mentioned, ```DBM[addr] == {}```.

Every key of the map is a unicode string, since keys in JSON maps are always strings. For every such key, denoted as ```key```, the address of the corresponding value will be ```DBM[addr + ["k", key, "v"]```.

In addition, the keys form a linked-list. ```DBM[addr + ["k", key, "p"]]``` will be the previous key (as a string), and ```DBM[addr + ["k", key, "n"]]``` will be the next key (again, as a string). If ```key``` is the first key, then ```DBM[addr + ["k", key, "p"]] == null```. If ```key``` is the last key, then ```DBM[addr + ["k", key, "n"]] == null```.

The value of ```DBM[addr + ["n"]]``` will be the first key, and ```DBM[addr + ["p"]]``` will be the last key. If the map is empty, they both will be ```null```.

Finally, the value of ```DBM[addr + ["m", "size"]]``` will always store the number of keys in the map.


### Lists

Lists are actually identical to maps, except for two differences:

* As mentioned before, ```DBM[addr] == []```, to indicate that this is a list;
* The keys are random strings.


### The Root Object

The JSOP database represents one JSON-style object, known as the *root object*. This is the object with the address ```[]``` (an empty list).

