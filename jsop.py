"""A dbm-based persistence for JSON-style data.

It allows you to store a large amount of JSON-style data on disk, but to access it quickly and efficiently.


To initialize a new JSOP database:

    from jsop import JSOP

    # 'data' can be any JSON-serializable object
    JSOP("/path/to/jsop").init(data)


To access an existing JSOP database:

    from jsop import JSOP

    with JSOP("/path/to/jsop") as data:
        name = data["name"]
        data["age"] = 30
        for friend in data["friends"]:
            print(friend["name"])


For the full documentation, see https://github.com/hagai-helman/jsop.
"""

import dbm
import json
import random

class DBMWrapper(object):
    """A wrapper for a DBM, with three features:

    * The keys are tuples of (unicode) strings (instead of bytearrays);
    * The values are any JSON-encodable object (instead of bytearrays);
    * A cache is used to avoid I/O operations.

    The usage is similar to a dbm object.
    """
    def __init__(self, *args):
        self._args = args

    def __enter__(self):
        self._cache = {}
        self._dbm = dbm.open(*self._args).__enter__()
        return self

    def __exit__(self, *args):
        self._dbm.__exit__(*args)
    
    def __getitem__(self, key):
        bkey = b'\xff'.join((s.encode("utf8") for s in key))
        if bkey not in self._cache:
            self._cache[key] = json.loads(self._dbm[bkey].decode("utf8"))
        return self._cache[key]

    def __setitem__(self, key, value):
        bkey = b'\xff'.join((s.encode("utf8") for s in key))
        bvalue = json.dumps(value).encode("utf8")
        self._dbm[bkey] = bvalue
        self._cache[key] = value

    def __delitem__(self, key):
        bkey = b'\xff'.join((s.encode("utf8") for s in key))
        del self._dbm[bkey]
        del self._cache[key]

    def __contains__(self, key):
        bkey = b'\xff'.join((s.encode("utf8") for s in key))
        return bkey in self._dbm

    def keys(self):
        return [tuple([s.decode("utf8") for s in bkey.split(b'\xff')]) for bkey in self._dbm.keys()]

################################################################################

class JObject(object):
    def __eq__(self, other):
        if isinstance(other, JObject):
            return self.export() == other.export()
        else:
            return self.export() == other

def get(db, address):
    value = db[address]
    if isinstance(value, dict):
        return JDict(db, address)
    elif isinstance(value, list):
        return JList(db, address)
    else:
        return value

def store(db, address, value):
    if address in db and isinstance(get(db, address), JObject):
        get(db, address).clear()
    if isinstance(value, JObject):
        value = value.export()
    if isinstance(value, dict):
        db[address] = {}
        db[address + ('p',)] = None
        db[address + ('n',)] = None
        new_dict = JDict(db, address)
        for key in value:
            new_dict[key] = value[key]
    elif isinstance(value, list) or isinstance(value, tuple):
        db[address] = []
        db[address + ('p',)] = None
        db[address + ('n',)] = None
        new_list = JList(db, address)
        for item in value:
            new_list.append(item)
    else:
        db[address] = value

def remove(db, address):
    if address in db and isinstance(get(db, address), JObject):
        get(db, address).clear()
    del db[address]

class JDict(JObject): 
    def __init__(self, db, address):
        self._db = db
        self._address = address

    def __getitem__(self, key):
        key = str(key)
        return get(self._db, self._address + ('k', key, 'v'))

    # Note that given a new key, __setitem__ must **append** the new key to the linked
    # list of keys. The JList.append() method relies on this behavior.
    def __setitem__(self, key, value):
        key = str(key)
        if key not in self:
            last_key = self._db[self._address + ('p',)]
            self._db[self._address + ('k', key, 'p')] = last_key
            self._db[self._address + ('k', key, 'n')] = None
            if last_key is not None:
                self._db[self._address + ('k', last_key, 'n')] = key
            else:
                self._db[self._address + ('n',)] = key
            self._db[self._address + ('p',)] = key
        store(self._db, self._address + ('k', key, 'v'), value)

    # This method is almost the same as __setitem__, but given a new key, it prepends it
    # to the linked list of keys, rather than append it.
    # It is used by the JList.prepend() method.
    def _prepend(self, key, value):
        key = str(key)
        if key not in self:
            first_key = self._db[self._address + ('n',)]
            self._db[self._address + ('k', key, 'n')] = first_key
            self._db[self._address + ('k', key, 'p')] = None
            if first_key is not None:
                self._db[self._address + ('k', first_key, 'p')] = key
            else:
                self._db[self._address + ('p',)] = key
            self._db[self._address + ('n',)] = key
        store(self._db, self._address + ('k', key, 'v'), value)

    def __delitem__(self, key):
        key = str(key)
        prev_key = self._db[self._address + ('k', key, 'p')]
        next_key = self._db[self._address + ('k', key, 'n')]
        remove(self._db, self._address + ('k', key, 'v'))
        remove(self._db, self._address + ('k', key, 'p'))
        remove(self._db, self._address + ('k', key, 'n'))
        if prev_key is not None:
            self._db[self._address + ('k', prev_key, 'n')] = next_key
        else:
            self._db[self._address + ('n',)] = next_key
        if next_key is not None:
            self._db[self._address + ('k', next_key, 'p')] = prev_key
        else:
            self._db[self._address + ('p',)] = prev_key


    def __contains__(self, key):
        key = str(key)
        return self._address + ('k', key, 'v') in self._db

    def __iter__(self):
        key = self._db[self._address + ('n',)]
        while key is not None:
            next_key = self._db[self._address + ('k', key, 'n')]
            yield key
            key = next_key

    def __len__(self):
        return len(list(iter(self)))

    def keys(self):
        return list(self)

    def clear(self):
        for key in self:
            del self[key]

    def export(self):
        result = {}
        for key in self:
            if isinstance(self[key], JObject):
                result[key] = self[key].export()
            else:
                result[key] = self[key]
        return result

def random_key():
    return "".join((random.choice("0123456789abcdef") for i in range(16)))


class JCell(JObject):
    def __init__(self, jdict, key):
        self._dict = jdict
        self._key = key

    def value(self):
        return self._dict[self._key]

    def put(self, value):
        self._dict[self._key] = value

    def remove(self):
        del self._dict[self._key]

    def export(self):
        return self.value().export()


class JList(JObject):
    def __init__(self, db, address):
        self._dict = JDict(db, address)

    def __iter__(self):
        for key in self._dict:
            yield self._dict[key]

    def __len__(self):
        return len(list(iter(self)))

    def append(self, item):
        self._dict[random_key()] = item

    def prepend(self, item):
        key = random_key()
        self._dict._prepend(key, item)

    def remove(self, item):
        for key in self._dict:
            if self._dict[key] == item:
                del self._dict[key]

    def __contains__(self, item):
        for key in self._dict:
            if self._dict[key] == item:
                return True
        return False

    def cells(self):
        for key in self._dict:
            yield JCell(self._dict, key)

    def clear(self):
        self._dict.clear()

    def export(self):
        result = []
        for item in self:
            if isinstance(item, JObject):
                result.append(item.export())
            else:
                result.append(item)
        return result

################################################################################

class JSOPError(Exception):
    pass

class JSOP(object):
    """A dbm-based persistence for JSON-style data.

    It allows you to store a large amount of JSON-style data on disk, but to access it quickly and efficiently.


    To initialize a new JSOP database:

        from jsop import JSOP

        # 'data' can be any JSON-serializable object
        JSOP("/path/to/jsop").init(data)


    To access an existing JSOP database:

        from jsop import JSOP

        with JSOP("/path/to/jsop") as data:
            name = data["name"]
            data["age"] = 30
            for friend in data["friends"]:
                print(friend["name"])


    For the full documentation, see https://github.com/hagai-helman/jsop.
    """

    def __init__(self, filename):
        self._filename = filename

    def init(self, obj = {}):
        """Store a JSON-encodable object in a new JSOP file."""
        with DBMWrapper(self._filename, "n") as dbmw:
            store(dbmw, ("m", "format-version"), "JSOP-1")
            store(dbmw, (), obj)

    def dump(self, obj = {}):
        """Synonym of init()."""
        self.init(obj)

    def export(self):
        """Get the data stored in the JSOP file as a Python native object."""
        with self as data:
            return data.export()

    def load(self):
        """Synonym of export()."""
        return self.export()

    def __enter__(self):
        with DBMWrapper(self._filename, "r") as dbmw:
            try:
                format_version = get(dbmw, ("m", "format-version"))
            except:
                raise JSOPError("Cannot determine fromat version")
        if format_version != "JSOP-1":
            raise JSOPError("Unsupported format version: {}".format(format_version))
        self._dbmw = DBMWrapper(self._filename, "w").__enter__()
        return get(self._dbmw, ())

    def __exit__(self, *args):
        self._dbmw.__exit__(*args)


__all__ = ["JSOP", "JSOPError"]

################################################################################

import sys

def print_usage():
    print("""
    usage: python3 -m jsop <command> <JSOP-database-path> [<JSON-file-path>]

    Supported commands: init, export.

    When command is "init", a new JSOP database will be created.
    If a JSON file is specified, its content is used to initialize the file.
    Else, the file will be initialized with an empty map ({}).

    When command is "export", the content of the JSOP file will be
    exported in JSON format.
    If a JSON file path is specified, the result will be saved to this file.
    Else, the result will be (beautifully) printed to the standard output.
    """)

if __name__ == "__main__":
    if 3 <= len(sys.argv) <= 4 and sys.argv[1] in ["init", "export"]:
        command = sys.argv[1]
        path = sys.argv[2]
        if len(sys.argv) == 4:
            json_path = sys.argv[3]
        else:
            json_path = None

        if command == "init":
            if json_path is None:
                obj = {}
            else:
                obj = json.load(open(json_path))
            JSOP(path).init(obj)

        elif command == "export":
            if json_path is None:
                print(json.dumps(JSOP(path).export(), indent=1))
            else:
                json.dump(JSOP(path).export(), open(json_path, "w"))
    else:
        print_usage()
        exit(1)


