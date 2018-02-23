#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author guohongze@126.com


import click
from kubernetes import client, config


def k8s_init():
    config.load_kube_config()
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
def update(name, replicas, img, ns):
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
@click.option('--img', help='docker images address')
@click.option('--replicas', help='pod replica number')
@click.option('--ns', default="default", help='namespace name')
def create(name, replicas, img, ns):
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
if __name__ == '__main__':
    cli.add_command(list_pod)
    cli.add_command(list_node)
    cli.add_command(create)
    cli.add_command(update)
    cli()
