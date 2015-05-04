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

import time

from oslo_config import cfg
from oslo_log import log

from openstack.compute.v2 import server_ip
from openstack.compute.v2 import server_metadata

from senlin.common import exception
from senlin.drivers import base
from senlin.drivers.openstack import sdk

LOG = log.getLogger(__name__)


class NovaClient(base.DriverBase):
    '''Nova V2 driver.'''

    def __init__(self, params):
        self.conn = sdk.create_connection(params)
        self.session = self.conn.session
        self.auth = self.session.authenticator

    def flavor_create(self, **params):
        try:
            return self.conn.compute.create_flavor(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def flavor_get(self, **params):
        try:
            return self.conn.compute.get_flavor(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def flavor_get_by_name(self, name):
        try:
            return self.conn.compute.find_flavor(name_or_id=name)
        except sdk.exc.HttpException as ex:
            raise ex

    def flavor_list(self, details=False, **params):
        try:
            return self.conn.compute.list_flavors(details=details, **params)
        except sdk.exc.HttpException as ex:
            raise ex

    def flavor_update(self, flavor):
        # flavor here can be the ID of flavor or flavor class
        try:
            return self.conn.compute.update_flavor(value=flavor)
        except sdk.exc.HttpException as ex:
            raise ex

    def flavor_delete(self, **params):
        try:
            self.conn.compute.delete_flavor(**params)
        except sdk.exc.HttpException as ex:
            sdk.ignore_not_found(ex)

    def image_create(self, **params):
        raise NotImplemented

    def image_get(self, **params):
        try:
            return self.conn.compute.get_image(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def image_get_by_name(self, name):
        try:
            return self.conn.compute.find_image(name_or_id=name)
        except sdk.exc.HttpException as ex:
            raise ex

    def image_list(self, details=False):
        try:
            return self.conn.compute.list_images(details=details)
        except sdk.exc.HttpException as ex:
            raise ex

    def image_delete(self, image):
        # image here can be a ID of image or a image class
        try:
            return self.conn.compute.delete_image(value=image)
        except sdk.exc.HttpException as ex:
            raise ex

    def keypair_create(self, **params):
        try:
            return self.conn.compute.create_keypair(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def keypair_get(self, **params):
        try:
            return self.conn.compute.get_keypair(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def keypair_list(self, **params):
        try:
            return self.conn.compute.list_keypairs(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def keypair_update(self, **params):
        try:
            return self.conn.compute.update_keypair(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def keypair_delete(self, keypair):
        # keypair here can be the ID of keypair or a keypair class
        try:
            self.conn.compute.delete_keypair(value=keypair)
        except sdk.exc.HttpException as ex:
            sdk.ignore_not_found(ex)

    def server_create(self, **params):
        timeout = cfg.CONF.default_action_timeout
        if 'timeout' in params:
            timeout = params.pop('timeout')

        server_obj = None
        try:
            server_obj = self.conn.compute.create_server(**params)
        except sdk.exc.HttpException as ex:
            raise ex

        try:
            # wait for new version of openstacksdk to fix this,
            # then use self.conn.compute.wait_for_status() instead
            server_obj.wait_for_status(self.session, wait=timeout)
        except sdk.exc.ResourceFailure as ex:
            raise exception.ProfileOperationFailed(ex.message)
        except sdk.exc.ResourceTimeout as ex:
            raise exception.ProfileOperationTimeout(ex.message)

        return server_obj

    def server_get(self, **params):
        try:
            return self.conn.compute.get_server(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_list(self, details=False):
        try:
            return self.conn.compute.list_servers(details=details)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_update(self, **params):
        try:
            return self.conn.compute.update_server(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_delete(self, **params):
        def _is_not_found(ex):
            parsed = sdk.parse_exception(ex)
            return isinstance(parsed, sdk.HTTPNotFound)

        timeout = cfg.CONF.default_action_timeout
        if 'timeout' in params:
            timeout = params.pop('timeout')

        try:
            self.conn.compute.delete_server(**params)
        except sdk.exc.HttpException as ex:
            if _is_not_found(ex):
                return

        total_sleep = 0
        while total_sleep < timeout:
            try:
                self.server_get(**params)
            except Exception as ex:
                if not _is_not_found(ex):
                    raise ex

            time.sleep(5)
            total_sleep += 5

        raise exception.ProfileOperationTimeout(ex.message)

    def server_interface_create(self, **params):
        try:
            return self.conn.compute.create_server_interface(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_interface_get(self, **params):
        try:
            return self.conn.compute.get_server_interface(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_interface_list(self):
        try:
            return self.conn.compute.list_server_interfaces()
        except sdk.exc.HttpException as ex:
            raise ex

    def server_interface_update(self, **params):
        try:
            return self.conn.compute.update_server_interface(**params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_interface_delete(self, interface):
        try:
            self.conn.compute.delete_server_interface(value=interface)
        except sdk.exc.HttpException as ex:
            sdk.ignore_not_found(ex)

    def server_ip_list(self, **params):
        try:
            return server_ip.ServerIP.list(self.session, **params)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_metadata_create(self, **params):
        obj = server_metadata.ServerMetadata.new(**params)
        try:
            return obj.create(self.session)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_metadata_get(self, **params):
        obj = server_metadata.ServerMetadata.new(**params)
        try:
            return obj.get(self.session)
        except sdk.exc.HttpException as ex:
            raise ex

    def server_metadata_update(self, **params):
        obj = server_metadata.ServerMetadata.new(**params)
        try:
            return obj.update(self.session)
        except sdk.exc.HttpException as ex:
            raise ex