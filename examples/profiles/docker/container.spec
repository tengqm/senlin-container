{
  'properties': {
    'name': 'start_one_container',
    'image': 'hello-world',
    'command': '/bin/sleep 30',
    'context':{
      'region_name': 'RegionOne'
    },
  },
  'type': 'docker.container',
  'version': '1.0'
}
