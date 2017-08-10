#!/usr/bin/env python3

from pprint import pprint

import previz

#API_ROOT = 'http://previz.app/api'
#API_TOKEN = 'Ux7lRGCnlGFn91F0yIiTEFhwiVWdb7YD1pFzeb4Ee6UpLL6sDIdjDQOEnpNK'

API_ROOT = 'https://app.previz.co/api'
API_TOKEN = 'He6N2cbxd6DHYWa8OXOqosUpw2uprQxvamVuenpQFPVKffT7AWjeetHFkvts'

TEAM_UUIDS = ['94071d22-3fd6-47bc-9e5b-b3b9f234c3f5', '938b52d0-0f4b-4179-afb9-901108456487']
TEAM_UUID = TEAM_UUIDS[1] # charles-team
PROJECT_UUID = 'c4cde74c-ecf6-4cca-9f6d-1b4475c21c5b'
SCENE_UUID = '8045e460-7f5e-48f3-a02e-28e98eccabca'
SCENE_JSON_URL = 'https://app.previz.co/api/scenes/8045e460-7f5e-48f3-a02e-28e98eccabca/json'

#p = previz.PrevizProject(API_ROOT, API_TOKEN)
p = previz.PrevizProject(API_ROOT, API_TOKEN, PROJECT_UUID)

#pprint(p.teams(include=[])

#pprint(p.teams()) # currently broken because of ?include=projects
#pprint(p.teams([]))
#pprint(p.projects(include=[]))
#pprint(p.teams(include=['owner']))
#pprint(p.team(TEAM_UUID, []))
#pprint(p.new_project('cf-pyapi-module', TEAM_UUID))

#pprint(p.project())
#pprint(p.delete_project())

#pprint(p.scene(SCENE_UUID, include=[]))
#pprint(p.new_scene('cf-pyapi-module'))

def cb(*args, **kwargs):
    print('cb', args, kwargs)
p.update_scene(SCENE_JSON_URL, open('scene.json', 'r'), cb)

#pprint(len(p.get_all()))
#pprint(len(p.get_all()))
#pprint(len(p.get_all()))

#pprint(len(p.teams()))
#pprint(len(p.teams()))
#pprint(len(p.teams()))
#pprint(len(p.teams()))


#p.assets()

#pprint(p.plugins())
#pprint(p.updated_plugin('blender', '0.0.7'))
