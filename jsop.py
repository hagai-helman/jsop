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
import io
import json
from warnings import warn

FORMAT_NAME = "JSOP"
FORMAT_VERSION_MAJOR = 1
FORMAT_VERSION_MINOR = 0

#
#   This module handles files of the format described in docs/data_format.md,
#   and provides the API described in README.md. One should read these two
#   documents before modifying this module.
#
#   The module is divided to four sections. Each section is based on the 
#   previous sections, but totally independent of the next sections:
#
#
#  I.   DBMWrapper
#       ***********
#
#       A class that wraps a DBM object, to store a mapping of:
#       (list of unicode strings) ==> (a JSON-serializable object).
#
#       The JSOP data structure assumes we have such a mapping.
#
#
#  II.  The Core
#       ********
#
#       The classes defined in this section provide an interface to objects in
#       a JSOP file - including objects that are distributed between several keys
#       of a DBMWrapper (i.e. JObjects).
#
#       This is the core section of this module.
#
#
#  III. The API
#       *******
#
#       This section defines the public interface for this module.
#
#
#  IV.  The CLI
#       *******
#
#       This section defines the module's command line interface.
#



####################         SECTION I: DBMWrapper         ####################




class DBMWrapper(object):
    """A wrapper for a DBM, with three features:

    * The keys are tuples of (unicode) strings (instead of bytearrays);
    * The values are any JSON-encodable object (instead of bytearrays);
    * A cache is used to avoid unnecessary I/O operations.

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


class ReadOnlyDBMWrapper(DBMWrapper):
    """A DBMWrapper that prevents writing to the DBM."""
    def __setitem__(self, key, value):
        raise io.UnsupportedOperation("not writable")

    def __delitem__(self, key):
        raise io.UnsupportedOperation("not writable")



####################         SECTION II: The Core         ####################


class JObject(object):
    """A base class for non-primitive JSON-style objects.
    
    Primitive objects are just stored in their addresses in the DBMWrapper.
    Unlike them, non-primitive objects (maps and lists) are stored in
    multiple addresses, including the root address, and other addresses in its
    'subtree' (i.e., addresses with the root address as a prefix).

    JDict and JList are classes that represent those non-primitive types.
    This abstract class defines the common methods they must support.
    """

    def _init(self, value):
        """Initialize the subtree under self's address.

        Assume there is no values in the subtree (other than its root) and
        hence garbage collection is not needed.
        """
        raise NotImplemented()

    def _destroy(self):
        """Remove all entries in the object's subtree."""
        raise NotImplemented()

    def export(self):
        """Return a copy of self, as a Python native object."""
        raise NotImplemented()

    def __eq__(self, other):
        if isinstance(other, JObject):
            return self.export() == other.export()
        else:
            return self.export() == other

def referror(ref):
    return JSOPError("Invalid Reference: " + "".join(["[{}]".format(repr(index)) for index in ref[1::3]]))

class JData(object):
    """A wrapper for DBMWrapper, that handles JObjects.

    In a JSOP database, maps and lists are not stored as plain JSON objects.
    Instead, an empty map or an empty list is stored at the address, "hinting" 
    the type of the object, while the object data itself is stored in other 
    addresses (derived from the original address).

    This wrapper handles two things:

    1. If the user tries to fetch a map or a list, it wraps it with a JDict or
       a JList object, respectively.
    2. If the user tried to delete or override a map or a list, it first destroys
       it, to ensure that all garbage in the database will be collected.
    """
    def __init__(self, db):
        self._db = db

    def __getitem__(self, address):
        try:
            value = self._db[address]
        except:
            raise referror(address)
        if isinstance(value, dict):
            return JDict(self, address)
        elif isinstance(value, list):
            return JList(self, address)
        else:
            return value

    def __setitem__(self, address, value):
        if isinstance(value, JObject):
            value = value.export()
        if address in self._db:
            del self[address]
        if isinstance(value, dict):
            self._db[address] = {}
            new_dict = JDict(self, address)
            new_dict._init(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            self._db[address] = []
            new_list = JList(self, address)
            new_list._init(value)
        else:
            self._db[address] = value

    def __delitem__(self, address):
        if address in self._db and isinstance(self[address], JObject):
            self[address]._destroy()
        try:
            del self._db[address]
        except:
            raise referror(address)

    def __contains__(self, address):
        return address in self._db


class JDict(JObject): 
    def __init__(self, db, address):
        self._db = db
        self._address = address

    def _init(self, value):
        """See JObject._init() for details."""
        self._db[self._address + ('p',)] = None
        self._db[self._address + ('n',)] = None
        self._db[self._address + ('s',)] = 0
        for key in value:
            self[key] = value[key]

    def __getitem__(self, key):
        key = str(key)
        return self._db[self._address + ('k', key, 'v')]

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
            self._db[self._address + ('s',)] += 1
        self._db[self._address + ('k', key, 'v')] = value

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(repr(key))
        key = str(key)
        prev_key = self._db[self._address + ('k', key, 'p')]
        next_key = self._db[self._address + ('k', key, 'n')]
        del self._db[self._address + ('k', key, 'v')]
        del self._db[self._address + ('k', key, 'p')]
        del self._db[self._address + ('k', key, 'n')]
        if prev_key is not None:
            self._db[self._address + ('k', prev_key, 'n')] = next_key
        else:
            self._db[self._address + ('n',)] = next_key
        if next_key is not None:
            self._db[self._address + ('k', next_key, 'p')] = prev_key
        else:
            self._db[self._address + ('p',)] = prev_key
        self._db[self._address + ('s',)] -= 1

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
        return self._db[self._address + ('s',)]

    def keys(self):
        return list(self)

    def clear(self):
        for key in self:
            del self[key]

    def update(self, other = None, **kw):
        if other is not None:
            if hasattr(other, "keys"):
                for k in other.keys():
                    self[k] = other[k]
            else:
                for (k, v) in other:
                    self[k] = v
        if len(kw) > 0:
            self.update(kw)

    def get(self, key, default=None):
        key = str(key)
        if key in self:
            return self[key]
        else:
            return default

    def pop(self, k, *args):
        k = str(k)
        if len(args) > 1:
            raise TypeError("pop() expected at most 2 arguments, got {}".format(len(args) + 1))
        if k in self:
            v = self[k]
            if isinstance(v, JObject):
                v = v.export()
            del self[k]
            return v
        else:
            if len(args) == 1:
                return args[0]
            else:
                raise KeyError(k)

    def popitem(self):
        if len(self) == 0:
            raise KeyError("popitem(): dictionary is empty")
        key = next(iter(self))
        return (key, self.pop(key))

    def setdefault(self, key, default = None):
        key = str(key)
        if key not in self:
            self[key] = default
        return self[key]

    def values(self):
        for key in self:
            yield self[key]

    def items(self):
        for key in self:
            yield (key, self[key])

    def copy(self):
        return self.export()

    def export(self):
        """See JObject.export() for details."""
        result = {}
        for key in self:
            if isinstance(self[key], JObject):
                result[key] = self[key].export()
            else:
                result[key] = self[key]
        return result

    def _destroy(self):
        """See JObject._destroy() for details."""
        self.clear()
        del self._db[self._address + ('n',)]
        del self._db[self._address + ('p',)]
        del self._db[self._address + ('s',)]
        


class JList(JObject):
    def __init__(self, db, address):
        self._dict = JDict(db, address)

    def _init(self, value):
        """See JObject._init() for details."""
        self._dict._init({})
        for item in value:
            self.append(item)

    def __getitem__(self, index):
        if index not in range(-len(self), len(self)):
            raise IndexError("list index out of range")
        elif index < 0:
            return self[len(self) + index]
        return self._dict[index]

    def __setitem__(self, index, value):
        if index not in range(-len(self), len(self)):
            raise IndexError("list assignment index out of range")
        elif index < 0:
            self[len(self) + index] = value
        self._dict[index] = value

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __reversed__(self):
        for i in range(len(self) - 1, -1, -1):
            yield self[i]

    def __add__(self, other):
        return list(self) + other

    def __radd__(self, other):
        return other + list(self)

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, other):
        return list(self) * other

    def __rmul__(self, other):
        return other * list(self)

    def __imul__(self, other):
        self.extend(self * (other - 1))
        return self

    def __delitem__(self, index):
        if index >= len(self) or index < -len(self):
            raise IndexError("list assignment out of range")
        elif index < 0:
            del self[len(self) + index]
        else:
            for i in range(index, len(self) - 1):
                self[i] = self[i + 1]
            self.pop()

    def insert(self, index, value):
        if index >= len(self):
            self.append(value)
        elif index < -len(self):
            self.insert(0, value)
        elif index < 0:
            self.insert(len(self) + index, value)
        else:
            self.append(None)
            for i in range(len(self) - 1, index, -1):
                self[i] = self[i - 1]
            self[index] = value

    def append(self, item):
        self._dict[len(self)] = item

    def pop(self):
        if len(self) == 0:
            raise IndexError("pop from empty list")
        return self._dict.pop(len(self) - 1)

    def remove(self, item):
        for i in range(len(self)):
            if self[i] == item:
                del self[i]
                return
        raise ValueError("item not in list")

    def __contains__(self, item):
        for i in range(len(self)):
            if self[i] == item:
                return True
        return False

    def sort(self, *args, **kw):
        exported = self.export()
        exported.sort()
        self.clear()
        self.extend(exported)

    def reverse(self):
        exported = self.export()
        exported.reverse()
        self.clear()
        self.extend(exported)

    def index(self, value, start = 0, stop = 9223372036854775807):
        for i in range(start, min(len(self), stop)):
            if self[i] == value:
                return i
        raise ValueError("{} is not in list".format(value))

    def count(self, value):
        counter = 0
        for item in self:
            if item == value:
                counter += 1
        return counter

    def copy(self):
        return self.export()

    def extend(self, other):
        for item in other:
            self.append(item)


    def clear(self):
        self._dict.clear()

    def export(self):
        """See JObject.export() for details."""
        result = []
        for item in self:
            if isinstance(item, JObject):
                result.append(item.export())
            else:
                result.append(item)
        return result

    def _destroy(self):
        """See JObject._destroy() for details."""
        self._dict._destroy()



####################         SECTION III: The API         ####################



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

    def __init__(self, filename, readonly=False):
        self._filename = filename
        self._readonly = readonly

    def init(self, obj = {}):
        """Store a JSON-encodable object in a new JSOP file."""
        if self._readonly:
            raise io.UnsupportedOperation("not writable")
        with DBMWrapper(self._filename, "n") as dbmw:
            jdata = JData(dbmw)
            jdata[("m", "format-name")] = FORMAT_NAME
            jdata[("m", "format-version-major")] = FORMAT_VERSION_MAJOR
            jdata[("m", "format-version-minor")] = FORMAT_VERSION_MINOR
            jdata[()] = obj

    def dump(self, obj = {}):
        """DEPRECATED. Synonym of init()."""
        warn(DeprecationWarning("JSOP.dump() is DEPRECATED. Use JSOP.init() instead."))
        self.init(obj)

    def export(self):
        """Get the data stored in the JSOP file as a Python native object."""
        with self as data:
            return data.export()

    def load(self):
        """DEPRECATED. Synonym of export()."""
        warn(DeprecationWarning("JSOP.load() is DEPRECATED. Use JSOP.export() instead."))
        return self.export()

    def __enter__(self):
        with DBMWrapper(self._filename, "r") as dbmw:
            jdata = JData(dbmw)
            try:
                format_name = jdata[("m", "format-name")]
                format_version_major = jdata[("m", "format-version-major")]
                format_version_minor = jdata[("m", "format-version-minor")]
            except:
                raise JSOPError("Cannot determine fromat version")
        supported_format = True
        supported_format &= (format_name == FORMAT_NAME)
        supported_format &= (format_version_major == FORMAT_VERSION_MAJOR)
        supported_format &= (format_version_minor <= FORMAT_VERSION_MINOR)
        if not supported_format:
            raise JSOPError("Unsupported format version: {} {}.{}".format(format_name, format_version_major, format_version_minor))
        if self._readonly:
            self._dbmw = ReadOnlyDBMWrapper(self._filename, "r").__enter__()
        else:
            self._dbmw = DBMWrapper(self._filename, "w").__enter__()
        return JData(self._dbmw)[()]

    def __exit__(self, *args):
        self._dbmw.__exit__(*args)


__all__ = ["JSOP", "JSOPError"]



####################          SECTION IV: The CLI          ####################


import sys
import typing

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
    json_path : typing.Optional[str]
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
                print(json.dumps(JSOP(path).export(), indent=1, sort_keys=True))
            else:
                json.dump(JSOP(path).export(), open(json_path, "w"), indent=0, sort_keys=True)
    else:
        print_usage()
        exit(1)


