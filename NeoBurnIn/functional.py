#!/usr/bin/env python3
#
# Last Change: Thu Jun 18, 2020 at 02:38 AM +0800

import re


##############
# "Functors" #
##############

def name(data, reg_pattern):
    return bool(re.search(reg_pattern, data.name))


def valueGt(data, thresh):
    try:
        return data.value > thresh
    except Exception:
        return False


def valueLt(data, thresh):
    try:
        return data.value < thresh
    except Exception:
        return False


##########################
# "Functor" construction #
##########################

def combinator_and(functors):
    def combined(data):
        result = [f(data) for f in functors]
        return False if False in result else True
    return combined


# NOTE: The peculiar form of the lambda function arguments is needed to bind
# variables early, namely **during** the list comprehension, not **after**!
def construct_functors(match):
    return [lambda x, f=f, arg=arg: globals()[f](x, arg)
            for f, arg in match.items()]


def parse_directive(rules):
    parsed = {}

    for rule in rules:
        functors = construct_functors(rule['match'])
        action = rule['action']

        combined = combinator_and(functors)
        executor = lambda sink, sink_name=action['sink'], \
            state=action['state'], ch=action['ch']: \
            getattr(sink[sink_name], state)(ch)

        parsed[combined] = executor

    return parsed
