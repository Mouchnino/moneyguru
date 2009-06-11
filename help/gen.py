#!/usr/bin/env python

import os

from hsdocgen import generate_help

generate_help.main('.', 'moneyguru_help', force_render=True)