#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author guohongze@126.com


import click
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from lib.deployment import Deployment


def k8s_init():
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    return api_instance


@click.group()
def cli():
    pass


@click.command()
def pods():
    api_instance = k8s_init()
    print("Listing pods with their IPs:")
    ret = api_instance.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


@click.command()
def nodes():
    api_instance = k8s_init()
    ret = api_instance.list_node()
    for i in ret.items:
        print("%s\t%s" % (i.status.addresses, i.metadata.name))


@click.command()
@click.option('--ns', default="default", help='namespace name')
def deployment(ns):
    api_instance = Deployment.k8s_init()
    if ns == "all":
        ret = api_instance.list_deployment_for_all_namespaces()
    else:
        ret = api_instance.list_namespaced_deployment(ns)
    print("name\t    replicas\t    available\t    generation")
    for i in ret.items:
        print("{:<15} {:<15} {:<15} {:<15}".format(i.metadata.name, i.spec.replicas, i.status.available_replicas, i.metadata.generation))


@click.command()
@click.option('--name', help='deployment name')
@click.option('--img', default="nginx:1.11", help='docker images address')
@click.option('--replicas', default=1, help='pod replica number')
@click.option('--ns', default="default", help='namespace name')
def create_dep(name, replicas, img, ns):
    api_instance = Deployment(name, ns, replicas, img)
    create_response = api_instance.create()
    return create_response


@click.command()
@click.option('--name', help='deployment name')
@click.option('--ns', default="default", help='namespace name')
def delete_dep(name, ns):
    api_instance = Deployment(name, ns)
    delete_response = api_instance.delete()
    if delete_response:
        print(delete_response)
    return delete_response


@click.command()
@click.option('--name', help='deployment name')
@click.option('--img', help='docker images address')
@click.option('--replicas', help='pod replica number')
@click.option('--ns', default="default", help='namespace name')
def update(name, replicas, img, ns):
    api_instance = Deployment(name, ns, replicas, img)
    if img:
        update_response = api_instance.update()
    if replicas:
        update_response = api_instance.update()
    return update_response


@click.command()
@click.option('--name', help='deployment name')
@click.option('--ns', default="default", help='namespace name')
def delete_svc(name, ns):
    api_instance = Deployment(name, ns)
    delete_response = api_instance.delete()
    return delete_response


@click.command()
@click.option('--name', help='deployment name')
@click.option('--ns', default="default", help='namespace name')
def create(name, ns):
    pass


@click.command()
@click.option('--name', help='deployment name')
@click.option('--ns', default="default", help='namespace name')
def delete(name, ns):
    pass


@click.command()
@click.option('--name', help='application name')
@click.option('--ns', default="default", help='namespace name')
def view(name, ns):
    dep_api_instance = Deployment.k8s_init()
    svc_api_instance = client.CoreV1Api()
    try:
        dep_instance = dep_api_instance.read_namespaced_deployment_status(name, namespace=ns, exact=True, export=True)
        svc_instance = svc_api_instance.read_namespaced_service(name, namespace=ns, exact=True, export=True)
    except ApiException as e:
        print("Exception when calling CoreV1Api->read_namespaced_service:% s\n" % e)


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

if __name__ == '__main__':
    cli.add_command(pods)
    cli.add_command(nodes)
    cli.add_command(deployment)
    cli.add_command(create_dep)
    cli.add_command(delete_dep)
    cli.add_command(create_svc)
    cli.add_command(delete_svc)
    cli.add_command(create)
    cli.add_command(update)
    cli.add_command(delete)
    cli.add_command(view)
    cli()
