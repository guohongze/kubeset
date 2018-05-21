#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author guohongze@126.com


import click
from kubernetes import client, config
import json
from kubernetes.client.rest import ApiException
from pprint import pprint
config.load_kube_config()


def k8s_init():
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    return extensions_v1beta1


@click.group()
def cli():
    pass


@click.command()
def list_pod():
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


@click.command()
def list_node():
    v1 = client.CoreV1Api()
    ret = v1.list_node()
    for i in ret.items:
        print("%s\t%s" % (i.status.addresses, i.metadata.name))


@click.command()
@click.option('--name', help='service name')
@click.option('--ns', help='namespace name')
def create_svc(name, ns="default"):
    api_instance = client.CoreV1Api()
    svc = client.V1Service()
    svc.api_version = "v1"
    svc.kind = "Service"
    svc.metadata = client.V1ObjectMeta(name=name)
    spec = client.V1ServiceSpec()
    spec.selector = {"app": "nginx-dep"}
    spec.type = "NodePort"
    spec.ports = [client.V1ServicePort(protocol="TCP", port=80, target_port=80)]
    svc.spec = spec
    api_response = api_instance.create_namespaced_service(namespace=ns, body=svc)
    print("Deployment updated. status='%s'" % str(api_response.status))


def create_deployment_object(name, status, replicas=3):
    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image="gtest.com/myproj/cent_nginx:3.0",
        ports=[client.V1ContainerPort(container_port=80)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    if status == "update":
        spec = client.ExtensionsV1beta1DeploymentSpec(
            template=template)
    if status == "create":
        spec = client.ExtensionsV1beta1DeploymentSpec(
            replicas=replicas,
            template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    return deployment


@click.command()
@click.option('--name', help='deployment name')
@click.option('--img', help='docker images address')
@click.option('--replicas', help='pod replica number')
@click.option('--ns', default="default", help='namespace name')
def update_dep(name, replicas, img, ns):
    # Update container image
    status = "update"
    api_instance = k8s_init()
    deployment = create_deployment_object(name, status)
    # Update the deployment
    if img:
        deployment.spec.template.spec.containers[0].image = img
    if replicas:
        replicas = int(replicas)
        deployment.spec.replicas = replicas
    api_response = api_instance.patch_namespaced_deployment(
        name=name,
        namespace=ns,
        body=deployment)
    print("Deployment updated. status='%s'" % str(api_response.status))


@click.command()
@click.option('--name', help='deployment name')
@click.option('--image', help='docker images address')
@click.option('--replicas', help='pod replica number')
@click.option('--ns', default="default", help='namespace name')
def create_dep(name, replicas, img, ns):
    # Update container image
    status = "create"
    api_instance = k8s_init()
    deployment = create_deployment_object(name, status)
    # Update the deployment
    if img:
        deployment.spec.template.spec.containers[0].image = img
    if replicas:
        replicas = int(replicas)
        deployment.spec.replicas = replicas
    api_response = api_instance.create_namespaced_deployment(
        namespace=ns,
        body=deployment)
    print("Deployment updated. status='%s'" % str(api_response.status))


@click.command()
@click.option('--name', help='application name')
@click.option('--ns', default="default", help='namespace name')
def view(name, ns):
    dep_api_instance = k8s_init()
    svc_api_instance = client.CoreV1Api()
    try:
        dep_instance = dep_api_instance.read_namespaced_deployment_status(name, namespace=ns, exact=True, export=True)
        svc_instance = svc_api_instance.read_namespaced_service(name, namespace=ns, exact=True, export=True)
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_service:% s\n" % e)
    print(dep_instance.status)
    print("==================")
    print(svc_instance.status)


if __name__ == '__main__':
    cli.add_command(list_pod)
    cli.add_command(list_node)
    cli.add_command(create_dep)
    cli.add_command(update_dep)
    cli.add_command(create_svc)
    cli.add_command(view)
    cli()
