# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Container endpoint for Senlin v1 ReST API.
"""

from senlin.api.common import util
from senlin.api.common import wsgi
from senlin.common import consts


class ContainerController(wsgi.Controller):
    """WSGI controller for container resource in Senlin V1 API."""

    REQUEST_SCOPE = 'containers'

    @util.policy_enforce
    def index(self, req):
        param_whitelist = {
                'Limit': 'single',
                'host': 'single',
        }
        params = util.get_allowed_params(req.params, param_whitelist)
        containers = self.rpc_client.container_list(req.context, **params)
        return {'containers': containers}

    @util.policy_enforce
    def create(self, req, body):
        data = body.get('container')
        params = {
            'host': data['host'],
            'image': data['Image'],
            'command': data['Command'],
            'name': data['Name'],
        }
        container = self.rpc_client.container_create(req.context, **params)
        return {'container': container}

    @util.policy_enforce
    def delete(self, req, path):
        res = self.rpc_client.container_delete(req.context, path)
        return res
