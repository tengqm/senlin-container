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

import base64
import copy

from senlin.common.i18n import _
from senlin.common import schema
from senlin.common import utils
from senlin.profiles import base
from senlin.drivers import docker_v1


class ContainerProfile(base.Profile):

    KEYS = (
        CONTEXT, CLUSTER, IMAGE, NAME, COMMAND,
    ) = (
        'context', 'cluster', 'image', 'name', 'command',
    )

    properties_schema = {
        CONTEXT: schema.Map(
            _('Customized security context for operationg servers.')
        ),
        IMAGE: schema.String(
            _('The image used to create a container')
        ),
        NAME: schema.String(
            _('The name of the container.')
        ),
        COMMAND: schema.String(
            _('The command ran when container is started.')
        ),
    }

    def __init__(self, type_name, name, **kwargs):
        super(ContainerProfile, self).__init__(type_name, name, **kwargs)

        self._dockerclient = None

    def docker(self, obj):
        if self._dockerclient is not None:
            return self._dockerclient
        params = obj.metadata
        self._dockerclient = docker_v1.DockerClient(params)
        return self._dockerclient

    def do_create(self, obj):
        image = self.properties[self.IMAGE]
        docker_driver = self.docker(obj)
        container_name = docker_driver.container_name
        container = self.docker(obj).create_container(image,
                                                      container_name)
        return container['Id']

    def do_delete(self, obj):
        docker_driver = self.docker(obj)
        container_id = docker_driver.container_id
        if container_id:
            res = self.docker(obj).delete_container(container_id)
            return res
        return True
