#!/usr/bin/env python3

from pprint import pprint

import previz

API_ROOT = 'http://previz.app/api'
API_TOKEN = 'zdvBU8BtPL5cubhlshz0qsYYaT7B0hMuebpQoMijNcXrN2qDc29WLTCxO5pL'

TEAM_UUIDS = ['94071d22-3fd6-47bc-9e5b-b3b9f234c3f5', '938b52d0-0f4b-4179-afb9-901108456487']
TEAM_UUID = TEAM_UUIDS[1] # charles-team
PROJECT_UUID = '9e380e70-853d-41f1-a720-15d6ee4dd29a'
SCENE_UUID = '35fafefb-aea7-4da8-b1b7-c23bac1198eb'
SCENE_JSON_URL = 'http://previz.app/api/scenes/35fafefb-aea7-4da8-b1b7-c23bac1198eb/json'

#p = previz.PrevizProject(API_ROOT, API_TOKEN)
p = previz.PrevizProject(API_ROOT, API_TOKEN, PROJECT_UUID)

#pprint(p.teams()) # currently broken because of ?include=projects
#pprint(p.teams([]))
#pprint(p.projects())
#pprint(p.teams(include=['owner']))
#pprint(p.team(TEAM_UUID, []))
#pprint(p.new_project('cf-pyapi-module', TEAM_UUID))

#pprint(p.project())
#pprint(p.delete_project())

#pprint(p.scene(SCENE_UUID, include=[]))
#pprint(p.new_scene('cf-pyapi-module'))

def cb(*args, **kwargs):
    print('cb', args, kwargs)
#pprint(p.update_scene(SCENE_JSON_URL, 'scene.json', open('scene.json'), cb))
#p.update_scene(SCENE_JSON_URL, open('scene.json'), cb)

#pprint(p.get_all())

#p.assets()

#pprint(p.plugins())
#pprint(p.updated_plugin('blender', '0.0.7'))
