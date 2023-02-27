"""Handle all OCI container image related work."""

import json
from pathlib import Path
import re
from subprocess import PIPE, run

# Regex pattern for full (e.g. docker.io/library/decoap:latest) and partial
# (decoap:latest) image identifiers
_image_pat = re.compile('^((?P<registry>[\w\.]+)/)?((?P<scope>[\w/]+)/)*(?P<name>\w+)(:(?P<tag>[\w-]+))?$')

_LOCAL_DIR = f'{str(Path.home())}/.local'
_SHARE_DIR = f'{_LOCAL_DIR}/share'
_CONTAINER_DIR = f'{_SHARE_DIR}/containers'

def get_image_list():
    return _load_json(f'{_CONTAINER_DIR}/storage/overlay-images/images.json')

def get_layer_list():
    return _load_json(f'{_CONTAINER_DIR}/storage/overlay-layers/layers.json')

def get_image(name):
    """Return the image matching name if it exists on the host."""
    image_list = get_image_list()

    for image in image_list:
        if 'names' in image:
            for image_name in image['names']:
                if name == image_name:
                    return image

    return None

def _run(command):
    """Execute a command in a subshell.

    Mock this function in tests to verify decoap behavior without actually
    executing anything in a shell."""
    return run(command, stdout=PIPE, check=True)

def _load_json(path):
    data = None
    with open(path, 'r') as fp:
        data = json.load(fp)

    return data

def get_layers_from(layer_id):
    '''Return the layers that make up this layer.'''
    layer_list = get_layer_list()
    layers = []

    search_layer = layer_id
    while search_layer:
        for layer in layer_list:
            if layer['id'] == search_layer:
                layers.append(layer['id'])
                search_layer = layer['parent'] if 'parent' in layer else None

    return layers

class Image():
    def __init__(self, name):
        mat = _image_pat.match(name)
        if not mat:
            raise Exception("Cannot parse image name.")

        registry = mat.group("registry")
        self.registry = registry if registry else "docker.io"

        scope = mat.group("scope")
        self.scope = scope if scope else "library"

        self.name = mat.group("name")

        tag = mat.group("tag")
        self.tag = tag if tag else "latest"

        self.fullname = f"{self.registry}/{self.scope}/{self.name}:{self.tag}"

        # Try to find the image layers if it's alredy on the host. If not on the
        # host, leave empty and let load_layers() fill it in later.
        self.load_layers()

    def __str__(self):
        ret = f"{self.registry}/" if self.registry else ""
        ret += f"{self.scope}/" if self.scope else ""
        ret += f"{self.name}"
        ret += f":{self.tag}" if self.tag else ""
        return ret

    def pull(self):
        _run(["podman", "pull", self.fullname])
        self.load_layers()

    def exists(self):
        """Return True if image exists on the host."""
        return get_image(self.fullname) is not None

    def load_layers(self):
        image_info = get_image(self.fullname)
        self.layers = [image_info["layer"]] if image_info else []

        if self.layers:
            self.layers += get_layers_from(self.layers[0])
