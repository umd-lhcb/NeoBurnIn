#!/usr/bin/env python
#
# Last Change: Mon Jan 20, 2020 at 02:39 AM -0500

import re


##############
# "Functors" #
##############

def smart_termination(f):
    def wrapper(*args, final=False):
        print(args, f)
        if args[0] is None:
            return False if final else None

        elif final:
            return f(*args)

        else:
            return args[0] if f(*args) else None

    return wrapper


@smart_termination
def name(data, reg_pattern):
    return bool(re.search(reg_pattern, data.name))


@smart_termination
def valueGt(data, thresh):
    return data.value > thresh


@smart_termination
def valueLt(data, thresh):
    return data.value < thresh


##########################
# "Functor" construction #
##########################

known_functors = {
    'name': name,
    'valueGt': valueGt,
    'valueLt': valueLt
}


def combinator_and(functors):
    def combined(data):
        for f in functors:
            data = f(data)
        return data
    return combined


def construct_functors(match):
    functors = list()
    size = len(match)

    for idx, f in enumerate(match):
        if idx+1 == size:
            functor = lambda x: known_functors[f](x, match[f], final=True)
        else:
            functor = lambda x: known_functors[f](x, match[f])
        functors.append(functor)

    return functors


def parse_directive(rules):
    parsed = {}

    for rule in rules:
        functors = construct_functors(rule['match'])
        action = rule['action']

        combined = combinator_and(functors)
        executor = lambda sink: sink[action['sink']].getattr(action['state'])(
            action['ch']
        )
        parsed[combined] = executor

    return parsed
