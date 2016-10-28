class Visitor(object):
    def __init__(self):
        pass

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception("visit_{} is not support".format(type(node).__name__))
