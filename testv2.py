#!/usr/bin/env python3

from pprint import pprint

import previz

API_ROOT = 'http://previz.app/api'
API_TOKEN = 'glCjaYtTMe5u3D6eOQi4CGJkoHLbOA7pRlhcbJQL5VQZB1ECXY5UskAg4y17'

TEAM_UUIDS = ['94071d22-3fd6-47bc-9e5b-b3b9f234c3f5', 'd899cd46-a94d-4b51-b9ce-eb6569df9c8b']
TEAM_UUID = TEAM_UUIDS[1]
PROJECT_UUID = 'ee35122e-65ba-4c56-8280-39653a32bf09'

p = previz.PrevizProject(API_ROOT, API_TOKEN, PROJECT_UUID)

#pprint(p.teams()) # currently broken because of ?include=projects
#pprint(p.teams([]))
#pprint(p.projects())
#pprint(p.teams(include=['owner']))
#pprint(p.team(TEAM_UUID, []))
#pprint(p.new_project('cf-pyapi-module', TEAM_UUID))

#pprint(p.project())

#pprint(p.new_scene('cf-pyapi-module', TEAM_UUID))
#pprint(p.delete_project())

#pprint(p.get_all())

p.assets()