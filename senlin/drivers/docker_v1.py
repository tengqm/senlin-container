# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from docker import Client
from docker import errors
from oslo_config import cfg
from oslo_log import log

from senlin.common.i18n import _LW
from senlin.drivers import base

LOG = log.getLogger(__name__)


class DockerClient(object):
    '''Container driver.'''

    def __init__(self, params):
        self.host_ip = params.get('host_ip', None)
        self.container_name = params.get('container_name', None)
        self.container_id = params.get('container_id', None)
        url = 'tcp://' + self.host_ip + ':2375'
        self.dockerclient = Client(base_url=url)

    def create_container(self, image, container_name):
        try:
            container = self.dockerclient.create_container(image=image,
                                                           name=container_name)
        except errors.NotFound:
            for line in self.dockerclient.pull(image, stream=True):
                json.dumps(json.loads(line), indent=4)
            container = self.dockerclient.create_container(image=image,
                                                           name=container_name)
        return container

    def delete_container(self, container):
        try:
            res = self.dockerclient.remove_container(container)
        except errors.NotFound:
            return True
        return True
