from nappingcat.util import import_module 
from nappingcat.exceptions import NappingCatUnhandled, NappingCatBadPatterns
import re

class CommandPatterns(object):
    def __init__(self, path=None, map=[]):
        self.path, self.map = path, map
        if self.path:
            self.module = import_module(self.path)

    def match(self, command):
        for regex, target in self.map:
            match = re.search(regex, command)
            if match:
                new_cmd = command.replace(command[match.start():match.end()], '')
                results = None
                if isinstance(target, CommandPatterns):
                    try:
                        results = target.match(new_cmd)
                    except NappingCatUnhandled:
                        pass
                elif isinstance(target, str):
                    results = getattr(self.module, target), match
                elif hasattr(target, '__call__'):
                    results = target, match
                else:
                    raise NappingCatBadPatterns("Target of %s is not a patterns instance, string, or callable." % command)
                if results is not None:
                    return results
        raise NappingCatUnhandled("This cat doesn't understand %s." % command)

    def __add__(self, other):
        ret = MultipleCommandPatterns()
        ret.add_pattern(self)
        ret.add_pattern(other)
        return ret

class MultipleCommandPatterns(CommandPatterns):
    def __init__(self, *args, **kwargs):
        super(MultipleCommandPatterns, self).__init__(*args, **kwargs)
        self.patterns = []

    def add_pattern(self, pattern):
        self.patterns.append(pattern)

    def match(self, command):
        try:
            return super(MultipleCommandPatterns, self).match(command)
        except NappingCatUnhandled, e:
            for pattern in self.patterns:
                try:
                    return pattern.match(command)
                except NappingCatUnhandled, e:
                    pass
        raise e

def include(path):
    router_module = import_module(path)
    cmdpatterns = getattr(router_module, 'cmdpatterns')
    return cmdpatterns

def patterns(path, *args):
    return CommandPatterns(path, args) 
