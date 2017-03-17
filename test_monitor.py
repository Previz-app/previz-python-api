#!/usr/bin/env python3

import pprint
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor

API_KEY='1UWVfUpGOxxYRUXvLPzQVd6LkHPea4M7RlU4JuMZZUGMuUTk7WBDe9Qz1fmG'
FILE_PATH='test-1920x1920.png'
headers={'Authorization': 'Bearer {0}'.format(API_KEY)}

#r = requests.get('http://previz.app/api/projects/2/assets', headers=headers)

#r = requests.post('http://previz.app/api/projects/2/assets',
#                  files={'file': open(FILE_PATH, 'rb')},
#                  headers=headers)


#multiple_files = [
#    ('images', ('test-2048x2048.png', open('test-2048x2048.png', 'rb'), 'image/png')),
#    ('images', ('test-1920x1920.png', open('test-1920x1920.png', 'rb'), 'image/png')),
#]
#r = requests.post('http://previz.app/api/projects/2/assets',
#                  files=multiple_files,
#                  headers=headers)

def cb(encoder):
    print(encoder.bytes_read, encoder.encoder.len)

m = MultipartEncoder(
#        fields = {'file': (FILE_PATH, open(FILE_PATH, 'rb'), 'image/png')}
        fields = {'file': (FILE_PATH, open(FILE_PATH, 'rb'), None)}
    )
m = MultipartEncoderMonitor(m, None)
print(type(m))
print(dir(m))
headers['Content-Type'] = m.content_type
print('########', m.content_type)
r = requests.post('http://previz.app/api/projects/2/assets',
                  data=m,
                  headers=headers)


r.raise_for_status()
print(r.status_code)
pprint.pprint(r.json())
