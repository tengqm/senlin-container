#
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

'''
Senlin exception subclasses.
'''

import functools
import sys

from oslo_log import log as logging
import six

from senlin.common.i18n import _
from senlin.common.i18n import _LE

_FATAL_EXCEPTION_FORMAT_ERRORS = False
LOG = logging.getLogger(__name__)


def wrap_exception(notifier=None, publisher_id=None, event_type=None,
                   level=None):
    '''Decorator that wraps a method to catch any exceptions.

    It logs the exception as well as optionally sending
    it to the notification system.
    '''
    def inner(f):
        def wrapped(*args, **kw):
            try:
                return f(*args, **kw)
            except Exception as e:
                # Save exception since it can be clobbered during processing
                # below before we can re-raise
                # exc_info = sys.exc_info()

                if notifier:
                    payload = dict(args=args, exception=e)
                    payload.update(kw)

                    # Use a temp vars so we don't shadow outer definitions.
                    temp_level = level
                    if not temp_level:
                        temp_level = notifier.ERROR

                    temp_type = event_type
                    if not temp_type:
                        # If f has multiple decorators, they must use
                        # functools.wraps to ensure the name is
                        # propagated.
                        temp_type = f.__name__

                    notifier.notify(publisher_id, temp_type, temp_level,
                                    payload)

                # re-raise original exception since it may have been clobbered
                # raise exc_info[0], exc_info[1], exc_info[2]
                raise

        return functools.wraps(f)(wrapped)
    return inner


class SenlinException(Exception):
    '''Base Senlin Exception.

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.
    '''

    message = _("An unknown exception occurred.")

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.__context__ = None

        try:
            self.message = self.msg_fmt % kwargs
        except KeyError:
            # exc_info = sys.exc_info()
            # if kwargs doesn't match a variable in the message
            # log the issue and the kwargs
            LOG.exception(_LE('Exception in string format operation'))
            for name, value in six.iteritems(kwargs):
                LOG.error("%s: %s" % (name, value))  # noqa

            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise
                # raise exc_info[0], exc_info[1], exc_info[2]

    def __str__(self):
        return six.text_type(self.message)

    def __unicode__(self):
        return six.text_type(self.message)

    def __deepcopy__(self, memo):
        return self.__class__(**self.kwargs)


class NotAuthenticated(SenlinException):
    msg_fmt = _("You are not authenticated.")


class Forbidden(SenlinException):
    msg_fmt = _("You are not authorized to complete this action.")


class SenlinBadRequest(SenlinException):
    msg_fmt = _("The request is malformed: %(msg)s")


class MultipleChoices(SenlinException):
    msg_fmt = _("Multiple results found matching the query criteria %(arg)s. "
                "Please be more specific.")


class InvalidParameter(SenlinException):
    msg_fmt = _("Invalid value '%(value)s' specified for '%(name)s'")


class ClusterNotFound(SenlinException):
    msg_fmt = _("The cluster (%(cluster)s) could not be found.")


class NodeNotFound(SenlinException):
    msg_fmt = _("The node (%(node)s) could not be found.")


class NodeStatusError(SenlinException):
    msg_fmt = _("Node in error status - '%(status)s' due to '%(reason)s'.")


class ProfileTypeNotFound(SenlinException):
    msg_fmt = _("Profile type (%(profile_type)s) is not found.")


class ProfileTypeNotMatch(SenlinException):
    msg_fmt = _("%(message)s")


class ProfileNotFound(SenlinException):
    msg_fmt = _("The profile (%(profile)s) could not be found.")


class ProfileNotSpecified(SenlinException):
    msg_fmt = _("Profile not specified.")


class ProfileValidationFailed(SenlinException):
    msg_fmt = _("%(message)s")


class ProfileOperationFailed(SenlinException):
    msg_fmt = _("%(message)s")


class ProfileOperationTimeout(SenlinException):
    msg_fmt = _("%(message)s")


class PolicyNotSpecified(SenlinException):
    msg_fmt = _("Policy not specified.")


class PolicyTypeNotFound(SenlinException):
    msg_fmt = _("Policy type (%(policy_type)s) is not found.")


class PolicyValidationFailed(SenlinException):
    msg_fmt = _("%(message)s")


class PolicyNotFound(SenlinException):
    msg_fmt = _("The policy (%(policy)s) could not be found.")


class PolicyExists(SenlinException):
    msg_fmt = _("The policy type (%(policy_type)s) already exists.")


class PolicyNotAttached(SenlinException):
    msg_fmt = _("The policy (%(policy)s) is not attached to the specified "
                "cluster (%(cluster)s).")


class InvalidSchemaError(SenlinException):
    msg_fmt = _("%(message)s")


class SpecValidationFailed(SenlinException):
    msg_fmt = _("%(message)s")


class NotSupported(SenlinException):
    msg_fmt = _("%(feature)s is not supported.")


class Error(SenlinException):
    msg_fmt = "%(message)s"

    def __init__(self, msg):
        super(Error, self).__init__(message=msg)


class InvalidContentType(SenlinException):
    msg_fmt = _("Invalid content type %(content_type)s")


class RequestLimitExceeded(SenlinException):
    msg_fmt = _('Request limit exceeded: %(message)s')


class WebhookNotFound(SenlinException):
    msg_fmt = _("The webhook (%(webhook)s) could not be found.")


class WebhookCredentialInvalid(SenlinException):
    msg_fmt = _("Webhook (%(webhook)s) credential is invalid.")


class ActionNotFound(SenlinException):
    msg_fmt = _("The action (%(action)s) could not be found.")


class ActionNotSupported(SenlinException):
    msg_fmt = _('Action "%(action)s" not supported by %(object)s')


class ActionInProgress(SenlinException):
    msg_fmt = _("Cluster %(cluster_name)s already has an action (%(action)s) "
                "in progress.")


class ActionIsOwned(SenlinException):
    msg_fmt = _("Worker %(owner)s is working on this action.")


class ActionIsStolen(SenlinException):
    msg_fmt = _("Worker %(owner)s has stolen the action.")


class ActionBeingWorked(SenlinException):
    msg_fmt = _("Worker %(owner)s is working on this action.")


class EventNotFound(SenlinException):
    msg_fmt = _("The event (%(event)s) could not be found.")


class HTTPExceptionDisguise(Exception):
    """Disguises HTTP exceptions.

    The purpose is to let them be handled by the webob fault application
    in the wsgi pipeline.
    """

    def __init__(self, exception):
        self.exc = exception
        self.tb = sys.exc_info()[2]
