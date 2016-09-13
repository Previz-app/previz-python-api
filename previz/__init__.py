import requests


class PrevizProject(object):
    endpoints_masks = {
        'projects': '{root}/projects',
        'project':  '{root}/projects/{project_id:d}',
        'scene':    '{root}/projects/{project_id:d}/scene',
        'assets':   '{root}/projects/{project_id:d}/assets',
        'asset':    '{root}/projects/{project_id:d}/assets/{asset_id:d}',
        'state':    '{root}/projects/{project_id:d}/state',
    }

    def __init__(self, root, token, project_id = None):
        self.root = root
        self.token = token
        self.project_id = project_id

    def request(self, *args, **kwargs):
        return requests.request(*args,
                                headers=self.headers,
                                verify=False, # TODO: how to make it work on Mac / Windows ?
                                **kwargs)

    def update_scene(self, fp):
        r = self.request('POST',
                         self.url('scene'),
                         files={'file': fp})
        return r.json()

    def projects(self):
        r = self.request('GET',
                         self.url('projects'))
        return r.json()

    def new_project(self, project_name):
        data = {'title': project_name}
        return self.request('POST',
                            self.url('projects'),
                            data=data).json()

    def delete_project(self):
        self.request('DELETE',
                     self.url('project'))

    def assets(self):
        return self.request('GET',
                            self.url('assets')).json()

    def delete_asset(self, asset_id):
        self.request('DELETE',
                     self.url('asset', asset_id=asset_id))

    def upload_asset(self, fp):
        return self.request('POST',
                            self.url('assets'),
                            files={'file': fp}).json()

    def set_state(self, state):
        data = {'state': state}
        self.request('PUT',
                     self.url('state'),
                     data=data)

    def url(self, mask_name, **url_elems):
        url_elems.update(self.url_elems)
        return self.endpoints_masks[mask_name].format(**url_elems)

    @property
    def url_elems(self):
        return {
            'root': self.root,
            'project_id': self.project_id,
        }
    
    @property
    def headers(self):
        return {'Authorization': 'Bearer {}'.format(self.token)}
