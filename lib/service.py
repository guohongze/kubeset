#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author guohongze@126.com
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class Service(object):
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    @staticmethod
    def k8s_init():
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        return api_instance

    def create(self):
        api_instance = self.k8s_init()
        svc = client.V1Service()
        svc.api_version = "v1"
        svc.kind = "Service"
        svc.metadata = client.V1ObjectMeta(name=self.name)
        spec = client.V1ServiceSpec()
        spec.selector = {"app": self.name}
        spec.type = "NodePort"
        spec.ports = [client.V1ServicePort(protocol="TCP", port=80, target_port=80)]
        svc.spec = spec
        api_response = api_instance.create_namespaced_service(namespace=self.namespace, body=svc)
        return api_response.status

    def delete(self):
        api_instance = self.k8s_init()
        body = client.V1DeleteOptions()
        api_response = api_instance.delete_namespaced_service(self.name, self.namespace, body=body, grace_period_seconds=10)
        return api_response.status

