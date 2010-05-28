from nappingcat.util import import_module 
from nappingcat.exceptions import NappingCatUnhandled, NappingCatBadPatterns
import re

class CommandPatterns(object):
    def __init__(self, path, map):
        self.path, self.map = path, map
        if self.path:
            self.module = import_module(self.path)

    def find_func(self, func):
        for regex, target in self.map:
            if isinstance(target, CommandPatterns):
                result = target.find_func(func)
                if result:
                    return (regex + result[0], result[1])
            elif target is func:
                return (regex, target) 
        return (None, func)

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

def include(path):
    router_module = import_module(path)
    cmdpatterns = getattr(router_module, 'cmdpatterns')
    return cmdpatterns

def patterns(path, *args):
    return CommandPatterns(path, args) 
