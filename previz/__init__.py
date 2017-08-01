import collections
from contextlib import contextmanager
import json
import uuid

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import semantic_version

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

def accumulate_pagination_next(func):
    data = []
    def wrapper(*args, **kwargs):
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

def pagination_next_url(rep):
    if 'pagination' not in rep:
        return None
    for link in rep['pagination']['links']:
        if link['rel'] == 'pagination.next':
            return link['url']

def get_updated_version(api_data, handle, version):
    d = api_data[handle]
    current_version = d['current_version']
    if semantic_version.Version(version) >= semantic_version.Version(current_version):
        return
    return d['versions'][current_version]

class PrevizProject(object):
    endpoints_masks = {
        'teams':       '{root}/teams',
        'team':        '{root}/teams/{team_id}',
        'switch_team': '{root}/teams/{team_id}/switch',
        'projects':    '{root}/projects',
        'project':     '{root}/projects/{project_id:s}',
        'scenes' :     '{root}/projects/{project_id:s}/scenes',
        'scene':       '{root}/scenes/{scene_id:s}',
        'assets':      '{root}/projects/{project_id:s}/assets',
        'asset':       '{root}/projects/{project_id:s}/assets/{asset_id:s}',
        'state':       '{root}/projects/{project_id:s}/state'
    }

    def __init__(self, root, token, project_id = None):
        self.root = root
        self.token = token
        self.project_id = project_id

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
    def scene(self, scene_id, include=['bookmarks', 'project', 'tracks']):
        r = self.request('GET',
                         self.url('scene', scene_id=scene_id),
                         params=to_params({'include': include}))
        r.raise_for_status()
        return r.json()

    @not_implented_in_v2
    def new_scene(self, scene_name):
        data = {'name': scene_name}
        r = self.request('POST',
                         self.url('scenes'),
                         data=data)
        r.raise_for_status()
        return r.json()

    @not_implented_in_v2
    def update_scene(self, scene_id, filename, fp, progress_callback = None):
        method, data = self.method('PATCH')
        data, headers = self.build_multipart_encoder(filename, fp, data, progress_callback)
        r = self.request(method,
                         self.url('scene', scene_id=scene_id),
                         data=data,
                         headers=headers)
        r.raise_for_status()
        return r.json()

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
