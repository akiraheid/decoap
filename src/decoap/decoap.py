import argparse
import json
from os.path import basename, exists
from os import chmod, makedirs
from pathlib import Path
from random import randint
import re
from shutil import copy as file_copy
import stat
from sys import exit
from textwrap import dedent

from pprint import pprint as pp

import decoap.manifest as manifest

_LOCAL_DIR = f'{str(Path.home())}/.local'
_SHARE_DIR = f'{_LOCAL_DIR}/share'
_CONTAINER_DIR = f'{_SHARE_DIR}/containers'

def load_json(path):
    data = None
    with open(path, 'r') as fp:
        data = json.load(fp)

    return data

def get_image_list():
    return load_json(f'{_CONTAINER_DIR}/storage/overlay-images/images.json')

def get_layer_list():
    return load_json(f'{_CONTAINER_DIR}/storage/overlay-layers/layers.json')

def get_image(name):
    image_list = get_image_list()

    for image in image_list:
        if 'names' in image:
            for image_name in image['names']:
                if name in image_name:
                    return image

def get_args():
    image_help = 'The image name or ID.'
    gen_help = ''

    parser = argparse.ArgumentParser()
    parser.add_argument('IMAGE', type=str, help=image_help)
    parser.add_argument('-g', '--generate-config', type=bool, help=gen_help)

    return parser.parse_args()

def get_layers_from(layer_id):
    '''Return the layers that make up this layer. Layers are returned in
    descending order.'''
    layer_list = get_layer_list()
    layers = []

    search_layer = layer_id
    while search_layer:
        for layer in layer_list:
            if layer['id'] == search_layer:
                layers.append(layer['id'])
                search_layer = layer['parent'] if 'parent' in layer else None

    return layers

def find_in_latest_decoap_layer(layers, path):
    layer_dir = f'{_CONTAINER_DIR}/storage/overlay'
    for layer in layers:
        layer_path = f'{layer_dir}/{layer}'
        if not exists(layer_path):
            print(f'Layer path [{layer_path}] does not exist')
            continue

        found_path = f'{layer_path}/diff/decoap/{path}'
        if exists(found_path):
            return found_path

    return None

def get_container_name(manifest):
    return basename(manifest['containerName'])

def get_icon_path(layers):
    return find_in_latest_decoap_layer(layers, 'icons/icon.png')

def find_manifest(layers):
    return find_in_latest_decoap_layer(layers, 'manifest.json')

def parse_manifest(manifest_path):
    data = manifest.load(manifest_path)

    if not 'appName' in data:
        raise Exception('Missing "appName" in manifest.')

    if not 'containerName' in data:
        raise Exception('Missing "containerName" in manifest.')

    return data

def get_manifest(layers):
    manifest_path = find_manifest(layers)
    if not manifest_path:
        print('No manifest.json found')
        exit(1)

    print(f'Found manifest at {manifest_path}')

    return parse_manifest(manifest_path)

def get_random_port_range(size):
    '''Return a port range of specified size between [49152, 65536].'''
    MIN = 49152
    MAX = 65536
    if size == None or size < 0:
        size = 0

    if size > (MAX - MIN):
        raise Exception(f'Size {size} greater than range between {MIN}-{MAX}.')

    start = randint(MIN, MAX-size)

    end = start + size
    return (start, end)

def parse_ports(port_str):
    host_regex = '(?P<host_port>(\d+(-\d+)?|x))(\+(?P<host_range>\d+))?'
    target_regex = '(?P<target_port>(\d+(-\d+)?|x))(\+(?P<target_range>\d+))?'
    pat = re.compile(f'{host_regex}:{target_regex}')
    match = pat.match(port_str)
    if not match:
        raise Exception(f'Expected port format {host_regex}:{target_regex}')

    host_port = match.group('host_port')
    host_range = match.group('host_range')
    target_port = match.group('target_port')
    target_range = match.group('target_range')

    host = ''
    if host_port == 'x':
        port_range = int(host_range) if host_range else 0
        start_end = get_random_port_range(port_range)
        host = f'{start_end[0]}'
        if host_range:
            host = f'{start_end[0]}-{start_end[1]}'
    else:
        host = f'{host_port}'

    target = ''
    if target_port == 'x':
        port_range = int(target_range) if target_range else 0
        start_end = get_random_port_range(port_range)
        target = f'{start_end[0]}'
        if target_range:
            target = f'{start_end[0]}-{start_end[1]}'
    else:
        target = f'{target_port}'

    return f'-p {host}:{target}'

def generate_launcher_bin(manifest):
    args = [f'--name {manifest["appName"]}']

    if 'detach' in manifest and manifest['detach']:
        args.append('-d')

    if 'devices' in manifest:
        for device in manifest['devices']:
            args.append(f'--device {device}')

    if 'env' in manifest:
        for env in manifest['env']:
            args.append(f'-e {env}')

    if 'ports' in manifest:
        for port in manifest['ports']:
            port_range = parse_ports(port)
            args.append(f'{port_range}')

    if 'rm' in manifest and manifest['rm']:
        args.append('--rm')
        pass

    createDirs = []
    if 'volumes' in manifest:
        for volume in manifest['volumes']:
            parts = volume.split(':')
            hostVol = parts[0]
            containerVol = parts[1]

            if not exists(hostVol):
                print(f'Application wants to mount a path that doesn\'t exist.')
                createPath = ''
                while createPath.lower() not in ['y', 'n']:
                    createPath = input(f'Create missing path {hostVol} [y/N]:')

                    # Default answer is 'n'
                    if createPath == '':
                        createPath = 'n'

                if createPath.lower() == 'y':
                    createDirs.append(hostVol)

            args.append(f'-v {volume}')

    content = dedent(f'''\
            #!/bin/bash

            mkdir -p {' '.join(createDirs)}

            podman run {' '.join(args)} {manifest["containerName"]}
            ''')

    bin_dir = f'{_LOCAL_DIR}/bin'
    if not exists(bin_dir):
        makedirs(bin_dir)

    path = f'{bin_dir}/{get_container_name(manifest)}'
    with open(path, 'w') as fp:
        fp.write(content)

    perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
    chmod(path, perms)

    print(f'Created executable launcher {path}')

def generate_desktop_launcher(manifest, layers):
    icon_path = get_icon_path(layers)
    container_name = get_container_name(manifest)

    others = []
    if icon_path:
        dest_dir = f'{_SHARE_DIR}/icons'
        dest = f'{dest_dir}/{container_name}.png'

        if not exists(dest_dir):
            makedirs(dest_dir, mode=0o755, exist_ok=True)

        file_copy(icon_path, dest)
        others.append(f'Icon={container_name}')
    else:
        dest = f'{_SHARE_DIR}/icons/default.png'
        others.append(f'Icon=default')

    if 'mimeTypes' in manifest:
        mime = 'MimeType=' + ';'.join(manifest['mimeTypes'])
        others.append(mime)

    app_name = manifest['appName']
    launcher_content = dedent(f'''\
            [Desktop Entry]
            Type=Application
            Version=1.0
            Name={app_name}
            Exec={container_name}''')

    others = '\n'.join(others)
    launcher_content += '\n' + others

    launcher_path = f'{_SHARE_DIR}/applications/{container_name}.desktop'

    with open(launcher_path, 'w') as fp:
        fp.write(launcher_content)

    print(f'Created desktop launcher {launcher_path}')

def _main():
    args = get_args()
    image = get_image(args.IMAGE)
    image_name = image["names"][0]

    layers = get_layers_from(image['layer'])
    print(f'Found matching image [{image_name}] composed of layers:')
    print('\n'.join(layers))

    manifest = get_manifest(layers)

    generate_launcher_bin(manifest)
    generate_desktop_launcher(manifest, layers)

    # Sanitize manifest content of ';'

if __name__ == '__main__':
    _main()
