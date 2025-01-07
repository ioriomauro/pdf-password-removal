# -*- coding: utf-8 -*-
from argparse import ArgumentError
from itertools import chain


def parse_range_list(rl):
    def parse_range(r):
        if len(r) == 0:
            return []
        parts = r.split("-")
        if len(parts) > 2:
            raise ArgumentError(f'Invalid range: {r}')
        return range(int(parts[0]), int(parts[-1])+1)
    return sorted(set(chain.from_iterable(map(parse_range, rl.split(",")))))
