#!/usr/bin/env python3

# This file is part of the MIDAS Workshop
# Jari Torniainen <jari.torniainen@ttl.fi>
# Copyright 2015 Finnish Institute of Occupational Health

#  The "bare essentials" template for node creation

import sys
from midas.node import BaseNode
import midas.utilities as mu


class ECGNode(BaseNode):

    def __init__(self, *args):
        super().__init__(*args)

        # self.metric_functions.append()
        # self.process_list.append()

if __name__ == '__main__':
    node = mu.midas_parse_config(ECGNode, sys.argv)

    if node is not None:
        node.start()
        node.show_ui()
