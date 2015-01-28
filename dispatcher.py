#!/usr/bin/env python3

# This file is part of the MIDAS Workshop
# Jari Torniainen <jari.torniainen@ttl.fi>
# Copyright 2015 Finnish Institute of Occupational Health

import sys
from midas.dispatcher import Dispatcher
from midas.utilities import parse_config_to_dict


def start_dispatcher(cfg):
    d = Dispatcher(cfg)
    d.start()


if __name__ == "__main__":
    cfg = parse_config_to_dict(sys.argv[1], sys.argv[2])
    start_dispatcher(cfg)
