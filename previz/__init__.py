import collections
import copy
from contextlib import contextmanager
import json
import os
import uuid

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import semantic_version

__author__ = 'Previz'
__contact__ = 'info@previz.co'
__version__ = '1.0.1'

def not_implented_in_v2(func):
    def wrapper(*args, **kwargs):
        raise NotImplementedError('{} is not yet implemented in the Previz API v2'.format(func.__qualname__))
    return wrapper

def extract_apiv2_data(func):
    def wrapper(*args, **kwargs):
        return walk_data(func(*args, **kwargs))
    return wrapper

def single_element(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)[0]
    return wrapper

def find_by_key(iterable, key, value):
    for i in iterable:
        if i[key] == value:
            return i

def iter_resp(resp):
    items = resp['data']
    if type(items) is dict:
        yield resp
    else:
        for i in items:
            yield i

def add_link_to_data(link_name, new_key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            resp = func(*args, **kwargs)
            for item in iter_resp(resp):
                link = find_by_key(item['links'], 'rel', link_name)
                item['data'][new_key] = link['url']
            return resp
        return wrapper
    return decorator

def add_plugins_download_url(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        for plugin in resp['data']:
            data = plugin['data']
            link = find_by_key(plugin['links'], 'rel', 'plugin.download')
            data['downloadUrl'] = link['url']
        return resp
    return wrapper

def accumulate_pagination_next(func):
    def wrapper(*args, **kwargs):
        data = []
        self = args[0]
        rep = func(*args, **kwargs)
        data.extend(rep['data'])
        url = pagination_next_url(rep)
        while url:
            rep = self.request('GET', url)
            rep.raise_for_status()
            rep = rep.json()
            data.extend(rep['data'])
            url = pagination_next_url(rep)

        ret = rep
        ret['data'] = data

        return ret
    return wrapper

def iter2dict(key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            return dict((x[key], x) for x in ret)
        return wrapper
    return decorator


def pagination_next_url(rep):
    if 'pagination' not in rep:
        return None
    for link in rep['pagination']['links']:
        if link['rel'] == 'pagination.next':
            return link['url']

def get_updated_version(api_data, handle, version):
    d = api_data[handle]
    if semantic_version.Version(d['current_version']) > semantic_version.Version(version):
        d = copy.deepcopy(d)
        d['version'] = d['current_version']
        del d['current_version']
        return d


class ReaderMonitor(object):
    def __init__(self, obj, cb = None):
        self.obj = obj
        self.read_so_far = 0
        self.cb = cb

        try:
            self.size = os.fstat(self.obj.fileno()).st_size
        except OSError:
            self.size = None

    def __getattr__(self, attr):
        return getattr(self.obj, attr)

    def read(self, size):
        ret = self.obj.read(size)
        read_size = len(ret)
        self.read_so_far += read_size
        if self.cb is not None:
            self.cb(self.obj, read_size, self.read_so_far, self.size)
        return ret


class PrevizProject(object):
    endpoints_masks = {
        'teams':       '{root}/teams',
        'team':        '{root}/teams/{team_id}',
        'switch_team': '{root}/teams/{team_id}/switch',
        'projects':    '{root}/projects',
        'project':     '{root}/projects/{project_id:s}',
        'scenes' :     '{root}/scenes',
        'scene':       '{root}/scenes/{scene_id:s}',
        'assets':      '{root}/projects/{project_id:s}/assets',
        'asset':       '{root}/projects/{project_id:s}/assets/{asset_id:s}',
        'state':       '{root}/projects/{project_id:s}/state',
        'plugins':     '{root}/plugins'
    }

    def __init__(self, root, token, project_id = None):
        self.root = root
        self.token = token
        self.project_id = project_id

    @iter2dict('handle')
    @extract_apiv2_data
    @add_plugins_download_url
    @accumulate_pagination_next
    def plugins(self):
        r = self.request('GET',
                         self.url('plugins'))
        r.raise_for_status()
        return r.json()

    def updated_plugin(self, handle, version):
        return get_updated_version(self.plugins(), handle, version)

    @extract_apiv2_data
    @accumulate_pagination_next
    def teams(self, include = ['owner,projects']):
        r = self.request('GET',
                         self.url('teams'),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    @single_element
    @extract_apiv2_data
    def team(self, team_id, include=['projects']):
        r = self.request('GET',
                         self.url('team', team_id=team_id),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    @extract_apiv2_data
    @accumulate_pagination_next
    def projects(self, include=['scenes', 'team']): # XXX 'assets' not implemented yet
        r = self.request('GET',
                         self.url('projects'),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    @extract_apiv2_data
    def new_project(self, project_name, team_uuid):
        data = {'title': project_name,
                'team_id': team_uuid}
        r = self.request('POST',
                         self.url('projects'),
                         data=data)
        r.raise_for_status()
        return r.json()

    @single_element
    @extract_apiv2_data
    def project(self, include=['assets', 'scenes', 'team']):
        r = self.request('GET',
                         self.url('project'),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    def delete_project(self):
        r = self.request('DELETE',
                         self.url('project'))
        r.raise_for_status()

    @single_element
    @extract_apiv2_data
    @add_link_to_data('scene.json', 'jsonUrl')
    def scene(self, scene_id, include=['bookmarks', 'project', 'tracks']):
        r = self.request('GET',
                         self.url('scene', scene_id=scene_id),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    @extract_apiv2_data
    @add_link_to_data('scene.json', 'jsonUrl')
    def new_scene(self, title):
        data = {
            'title': title,
            'project_id': self.project_id
        }
        r = self.request('POST',
                         self.url('scenes'),
                         data=data)
        r.raise_for_status()
        return r.json()

    def update_scene(self, json_url, fp, progress_callback = None):
        headers = {'Content-Type': 'application/json'}
        r = self.request('PUT',
                         json_url,
                         data=ReaderMonitor(fp, progress_callback),
                         headers=headers)
        r.raise_for_status()

    @not_implented_in_v2
    @accumulate_pagination_next
    def assets(self):
        r = self.request('GET',
                         self.url('assets'))
        r.raise_for_status()
        return r.json()

    @not_implented_in_v2
    def delete_asset(self, asset_id):
        r = self.request('DELETE',
                         self.url('asset', asset_id=asset_id))
        r.raise_for_status()

    @not_implented_in_v2
    def upload_asset(self, filename, fp, progress_callback = None):
        method, data = self.method('POST')
        data, headers = self.build_multipart_encoder(filename, fp, data, progress_callback)
        r = self.request(method,
                         self.url('assets'),
                         data=data,
                         headers=headers)
        r.raise_for_status()
        return r.json()

    def get_all(self):
        return self.teams(['projects.scenes'])

    def url(self, mask_name, **url_elems_override):
        url_elems = self.url_elems.copy()
        url_elems.update(url_elems_override)
        return self.endpoints_masks[mask_name].format(**url_elems)

    def build_multipart_encoder(self, filename, fp, fields, progress_callback):
        fields['file'] = (filename, fp, None)
        data = MultipartEncoder(
            fields = fields
        )
        data = MultipartEncoderMonitor(data, progress_callback)
        headers = {'Content-Type': data.content_type}
        return data, headers

    @property
    def url_elems(self):
        return {
            'root': self.root,
            'project_id': self.project_id,
        }

    @property
    def common_headers(self):
        return {
            'Accept': 'application/vnd.previz.v2+json',
            'Authorization': 'Bearer {0}'.format(self.token)
        }

    def method(self, method):
        data = {}
        if method in ['PATCH', 'PUT']:
            data['_method'] = method.lower()
            method = 'POST'
        return method, data

    def request(self, *args, **kwargs):
        headers = {}
        headers.update(self.common_headers)
        headers.update(kwargs.get('headers', {}))
        kwargs['headers'] = headers

        return requests.request(*args,
                                verify=False, # TODO: how to make it work on Mac / Windows ?
                                **kwargs)


class UuidBuilder(object):
    def __init__(self, dns = 'app.previz.co'):
        self.namespace = uuid.uuid5(uuid.NAMESPACE_DNS, dns)

    def __call__(self, name = None):
        return str(self.uuid(name)).upper()

    def uuid(self, name):
        if name is None:
            return uuid.uuid4()
        return uuid.uuid5(self.namespace, name)


buildUuid = UuidBuilder()


def flat_list(iterable):
    def flatten(values):
        try:
            for value in values:
                for iterated in flatten(value):
                    yield iterated
        except TypeError:
            yield values

    return list(flatten(iterable))

def ensure_list(obj):
    return obj if isinstance(obj, list) else [obj]

def is_data_node(obj):
    return isinstance(obj, dict) and 'data' in obj

def walk_data(obj):
    def iter(obj):
        if is_data_node(obj):
            return iter(obj['data'])

        if isinstance(obj, list):
            return [iter(o) for o in obj]

        if isinstance(obj, dict):
            ret = {}
            for k, v in obj.items():
                ret[k] = iter(v)
            return ret

        return obj

    return iter(obj)

def to_param(name, v):
    if not isinstance(v, list):
        return {name: v}

    ret = {}
    v = ','.join([str(i) for i in v])
    if len(v) > 0:
        ret[name] = v
    return ret

def to_params(params):
    ret = {}
    for k, v in params.items():
        ret.update(to_param(k, v))
    return ret

#############################################################################

UVSet = collections.namedtuple('UVSet',
                               ['name',
                                'coordinates'])

Mesh = collections.namedtuple('Mesh',
                             ['name',
                              'geometry_name',
                              'world_matrix',
                              'faces',
                              'vertices',
                              'uvsets'])


Scene = collections.namedtuple('Scene',
                               ['generator',
                                'source_file',
                                'background_color',
                                'objects'])


def build_metadata(scene):
    return {
        'version': 4.4,
        'type': 'Object',
        'generator': scene.generator,
        'sourceFile': scene.source_file
    }


def build_scene_root(scene, children):
    ret = {
        'type': 'Scene',
        'matrix': [
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0
        ],
        'uuid': buildUuid(),
        'children': children
    }

    if scene.background_color is not None:
        ret['background'] = scene.background_color

    return ret


def build_geometry(scene, mesh):
    return {
        'data': {
            'metadata': {
                'version': 3,
                'generator': scene.generator,
            },
            'name': mesh.geometry_name,
            'faces': flat_list(mesh.faces),
            'uvs': [flat_list(uvset.coordinates) for uvset in mesh.uvsets],
            'vertices': flat_list(mesh.vertices)
        },
        'uuid': buildUuid(),
        'type': 'Geometry'
    }


def build_user_data(mesh):
    return {'previz': {
            'uvsetNames': [uvset.name for uvset in mesh.uvsets]
        }
    }


def build_object(mesh, geometry_uuid):
    return {
        'name': mesh.name,
        'uuid': buildUuid(),
        'matrix': flat_list(mesh.world_matrix),
        'visible': True,
        'type': 'Mesh',
        'geometry': geometry_uuid,
        'userData': build_user_data(mesh)
    }


def build_objects(scene):
    objects = []
    geometries = []

    for mesh in scene.objects:
        geometry = build_geometry(scene, mesh)
        object = build_object(mesh, geometry['uuid'])

        objects.append(object)
        geometries.append(geometry)

    return build_scene_root(scene, objects), geometries


def build_three_js_scene(scene):
    ret = {}

    scene_root, geometries = build_objects(scene)

    return {
        'animations': [],
        'geometries': geometries,
        'images': [],
        'materials': [],
        'metadata': build_metadata(scene),
        'object': scene_root,
        'textures': []
    }


def export(scene, fp):
    scene = build_three_js_scene(scene)
    json.dump(scene, fp, indent=1, sort_keys=True)
