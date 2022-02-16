import jsop
import sys


class JSOPTester(object):
    def __init__(self, filename):
        self._filename = filename
        self._tests = []

    def stage(self, stage_name):
        def add(action):
            self._tests.append((stage_name, action))
            return action
        return add

    def test(self):
        failures = []
        for (stage, action) in self._tests:
            a = {}
            jsop.JSOP(self._filename).init({})
            with jsop.JSOP(self._filename) as b:
                try:
                    if action(a) != action(b):
                        failures.append("{} (retval)".format(stage))
                except:
                    print(file = sys.stderr)
                    print(">>> Exception in stage {} <<<".format(stage), file = sys.stderr)
                    print(file = sys.stderr)
                    raise
            with jsop.JSOP(self._filename) as b:
                if a != b:
                    failures.append(stage)
        return failures


def define_stages(tester):

    @tester.stage("JDict.__setitem__")
    def build_dict(data):
        data["a"] = 0
        data["0"] = "a"
        data["None"] = None
        data["b"] = [0,1,2]
        data["c"] = data["b"].copy()
        data["b"][0] = data["b"].copy()

    @tester.stage("JDict.__getitem__")
    def action(data):
        build_dict(data)
        return [
            data["0"],
            data["a"],
            data["b"][0],
            data["None"]
        ]

    @tester.stage("JDict.__delitem__")
    def action(data):
        build_dict(data)
        del data["a"]

    @tester.stage("JDict.__contains__")
    def action(data):
        build_dict(data)
        return [
            "a" in data,
            "A" in data,
            "0" in data,
            "1" in data,
            "None" in data
        ]

    @tester.stage("JDict.__iter__")
    def action(data):
        build_dict(data)
        return sorted([key for key in data])

    @tester.stage("JDict.__len__")
    def action(data):
        build_dict(data)
        return len(data)

    @tester.stage("JDict.keys")
    def action(data):
        build_dict(data)
        return sorted(data.keys())

    @tester.stage("JDict.clear")
    def action(data):
        build_dict(data)
        data.clear()

    @tester.stage("JDict.update")
    def action(data):
        build_dict(data)
        data.update({"a": 0, "b": 1, "c": {"d": 3, "e": 4}})
        data.update(x = 3, y = 4, z = 5)
        data.update(data["c"])

    @tester.stage("JDict.get")
    def action(data):
        build_dict(data)
        return [
            data.get("a"),
            data.get("A"),
            data.get("0", 123),
            data.get("1", 123),
            data.get("None", 123)
        ]

    @tester.stage("JDict.pop")
    def action(data):
        build_dict(data)
        return [data.pop("0"), data.pop("1", 123)]

    @tester.stage("JDict.popitem")
    def action(data):
        build_dict(data)
        s = []
        while len(data) > 0:
            s.append(data.popitem())
        return sorted(s)

    @tester.stage("JDict.setdefault")
    def action(data):
        build_dict(data)
        return [
            data.setdefault("a"),
            data.setdefault("A"),
            data.setdefault("0", 123),
            data.setdefault("1", 123),
            data.setdefault("None", 123)
        ]

    @tester.stage("JDict.values")
    def action(data):
        data.update(a = 1, b = 2, c = 3)
        return sorted(data.values())

    @tester.stage("JDict.items")
    def action(data):
        build_dict(data)
        return sorted(data.items())

    @tester.stage("JDict.copy")
    def action(data):
        build_dict(data)
        data["self"] = data.copy()

    def build_list(data):
        data["list"] = [0,1,2,[3,4,5],{"6": 7, "8": 9}]

    @tester.stage("JList.__getitem__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [
            dlist[0],
            dlist[3][1],
            dlist[3][-1],
            dlist
        ]

    @tester.stage("JList.__setitem__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist[1] = [10,11,12]
        dlist[1][2] = 13

    @tester.stage("JList.__len__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [len(dlist), len(dlist[3])]

    @tester.stage("JList.__iter__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        s = []
        for item in dlist:
            s.append(item)
        return s

    @tester.stage("JList.__reversed__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        s = []
        for item in reversed(dlist):
            s.append(item)
        return s

    @tester.stage("JList.__add__, JList.__radd__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [
            dlist + dlist,
            dlist + [1,2,3],
            [1,2,3] + dlist
        ]

    @tester.stage("JList.__iadd__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist += [1,2,3]
        dlist += dlist

    @tester.stage("JList.__mul__, JList.__rmul__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [
            7 * dlist,
            dlist * 7
        ]

    @tester.stage("JList.__imul__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist *= 2
        dlist *= 2

    @tester.stage("JList.__delitem__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        del dlist[4]
        del dlist[3][1]
        del dlist[3][-1]
        del dlist[1]

    @tester.stage("JList.insert")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.insert(2, None)
        dlist.insert(-2, None)

    @tester.stage("JList.append")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.append(0)
        dlist.append(dlist.copy())
        dlist.append({})

    @tester.stage("JList.pop")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return dlist.pop()

    @tester.stage("JList.remove")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.remove(1)
        dlist.remove([3,4,5])

    @tester.stage("JList.__contains__")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [
            2 in dlist,
            3 in dlist,
            [3,4,5] in dlist,
            [3,4,6] in dlist
        ]

    @tester.stage("JList.sort")
    def action(data):
        data["list"] = [3,8,-1,0,3,4,3]
        dlist = data["list"]
        dlist.sort()

    @tester.stage("JList.revrese")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.reverse()

    @tester.stage("JList.index")
    def action(data):
        build_list(data)
        dlist = data["list"]
        return [
            dlist.index(2),
            dlist.index([3,4,5])
        ]

    @tester.stage("JList.count")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.extend([[3,4,5], [3,4,5]])
        return [
            dlist.count(2),
            dlist.count(3),
            dlist.count([3,4,5]),
            dlist.count([3,4,6])
        ]
 
    @tester.stage("JList.extend")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.extend([1,2,3,[1,2,3],{}])
        dlist.extend(dlist)

    @tester.stage("JList.clear")
    def action(data):
        build_list(data)
        dlist = data["list"]
        dlist.clear()



if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("usage: {} <JSOP-temp-file-path>".format(sys.argv[0]))

    tester = JSOPTester(sys.argv[1])
    define_stages(tester)
    failures = tester.test()

    if len(failures) == 0:
        print("PASSED all tests.")
    else:
        print("FAILED on the following tests:")
        for stage in failures:
            print("* {}".format(stage))
