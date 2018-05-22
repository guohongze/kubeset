#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author guohongze@126.com
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class Deployment(object):
    def __init__(self, name, namespace, replicas=None, img=None):
        self.name = name
        self.namespace = namespace
        self.replicas = replicas
        self.img = img

    @staticmethod
    def k8s_init():
        config.load_kube_config()
        extensions_v1beta1 = client.ExtensionsV1beta1Api()
        return extensions_v1beta1

    def create_deployment_object(self, status):
        # Configureate Pod template container
        container = client.V1Container(
            name=self.name,
            image=self.img,
            ports=[client.V1ContainerPort(container_port=80)])
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": self.name}),
            spec=client.V1PodSpec(containers=[container]))
        # Create the specification of deployment
        if status == "update":
            spec = client.ExtensionsV1beta1DeploymentSpec(
                template=template)
        if status == "create":
            spec = client.ExtensionsV1beta1DeploymentSpec(
                replicas=self.replicas,
                template=template)
        # Instantiate the deployment object
        deployment = client.ExtensionsV1beta1Deployment(
            api_version="extensions/v1beta1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=self.name),
            spec=spec)
        return deployment

    def create(self):
        status = "create"
        api_instance = self.k8s_init()
        deployment = self.create_deployment_object(status)
        # Update the deployment
        if self.img:
            deployment.spec.template.spec.containers[0].image = self.img
        if self.replicas:
            replicas = int(self.replicas)
            deployment.spec.replicas = replicas
        api_response = api_instance.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment)
        return api_response

    def update(self):
        # Update container image
        status = "update"
        api_instance = self.k8s_init()
        deployment = self.create_deployment_object(status)
        # Update the deployment
        if self.img:
            deployment.spec.template.spec.containers[0].image = self.img
        if self.replicas:
            replicas = int(self.replicas)
            deployment.spec.replicas = replicas
        api_response = api_instance.patch_namespaced_deployment(
            name=self.name,
            namespace=self.namespace,
            body=deployment)
        return api_response

    def view(self):
        api_instance = self.k8s_init()
        try:
            dep_instance = api_instance.read_namespaced_deployment_status(self.name, namespace=self.namespace, exact=True, export=True)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_service:% s\n" % e)
        return dep_instance.status

    def delete(self):
        # Delete deployment
        api_instance = self.k8s_init()
        api_response = api_instance.delete_namespaced_deployment(
            name=self.name,
            namespace=self.namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        return api_response
