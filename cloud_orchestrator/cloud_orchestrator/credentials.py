#!/usr/bin/env python

import os

from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session


# Assumes openrc file is sourced.
class Credentials(object):
    def __init__(self):
        self.password = None
        self.username = None
        self.tenant_name = None
        self.auth_url = None
        self.cacert = None
        self.region_name = None
        self.user_domain_name = None
        self.project_domain_name = None
        self.project_name = None
        self.identity_api_version = 2
        success = True

        if 'OS_IDENTITY_API_VERSION' in os.environ:
            self.identity_api_version = int(os.environ['OS_IDENTITY_API_VERSION'])
        if self.identity_api_version == 2:
            for varname in ['OS_USERNAME', 'OS_AUTH_URL', 'OS_TENANT_NAME']:
                if varname not in os.environ:
                    success = False
            if success:
                self.username = os.environ['OS_USERNAME']
                self.auth_url = os.environ['OS_AUTH_URL']
                self.tenant_name = os.environ['OS_TENANT_NAME']
            if 'OS_REGION_NAME' in os.environ:
                self.region_name = os.environ['OS_REGION_NAME']
        elif self.identity_api_version == 3:
            self.username = os.environ['OS_USERNAME']
            self.auth_url = os.environ['OS_AUTH_URL']
            self.project_name = os.environ['OS_PROJECT_NAME']
            self.project_domain_name = os.environ['OS_PROJECT_DOMAIN_NAME']
            self.user_domain_name = os.environ['OS_USER_DOMAIN_NAME']
        if 'OS_CACERT' in os.environ:
            self.cacert = os.environ['OS_CACERT']

        if 'OS_PASSWORD' in os.environ:
            self.password = os.environ['OS_PASSWORD']

    def get_session(self):
        dct = {
            'username': self.username,
            'password': self.password,
            'auth_url': self.auth_url
        }
        auth = None

        if self.identity_api_version == 3:
            dct.update({
                'project_name': self.project_name,
                'project_domain_name': self.project_domain_name,
                'user_domain_name': self.user_domain_name
            })
            auth = v3.Password(**dct)
        else:
            dct.update({
                'tenant_name': self.tenant_name
            })
            auth = v2.Password(**dct)
        return session.Session(auth=auth, verify=self.cacert)
