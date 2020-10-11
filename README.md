# localkube

## dependencies
* kubectl
* helm
* docker
* python3

## Optionals includes
* postgresql database
* pgadmin4
* redis
* rabbitMQ


## Usage

Getting started
First clone the repository into your local application:
```shell
git clone git@github.com:cmnrv/localkube.git .k8s
```
and add it to your gitignore:
```shell
echo ".k8s" >> .gitignore
```
Creating your cluster
```shell
python3 cluster.py init
```
Deploying an application
```shell
python3 cluster.py deploy
```
Destroying your cluster
```shell
python3 cluster.py destroy
```