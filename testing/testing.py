class NoStage(object):
    pass

class TestingContext(object):
    def __init__(self):
        self._stage = None

    def stage(self, stage = NoStage()):
        if isinstance(stage, NoStage):
            return self._stage
        else:
            self._stage = stage

class Testing(object):
    def __init__(self):
        self.tests = []

    def test(self, desc):
        def dec(func):
            self.tests.append((desc, func)) 
            return func
        return dec

    def run_all(self):
        for (desc, func) in self.tests:
            context = TestingContext()
            try:
                func(context)
            except Exception as e:
                print()
                print("TEST FAILED: ", desc)
                if context.stage():
                    print("STAGE: ", context.stage())
                print()
                raise e
