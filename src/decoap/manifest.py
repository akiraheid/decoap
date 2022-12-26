"""Manifest operations can be done with this module."""

import json

class Manifest():
    """The manifest for the application."""

    def __init__(self):
        pass

def load(path):
    data = None
    with open(path, 'r') as fp:
        data = json.load(fp)

    return data
