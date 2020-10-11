#!/usr/bin/python3
import argparse, os, subprocess, sys, yaml

def check_dependencies():
    """
    Checks that all the required dependencies (k3d, helm 3, kubectl 1.18+,...)
    are installed and available
    """
    print('check_dependencies')

def parse_yaml(filename='config.yaml'):
    """
    Loads the provided configuration file using the YAML module
    """
    try:
        config = yaml.load(open(filename), Loader=yaml.FullLoader)
    except FileNotFoundError as e:
        print('Unable to find the configuration file.')
    except yaml.YAMLError as e:
        print('Unable to load the configuration file, please check it for errors.')
    return config

def add_repositories(config):
    """
    Goes through the provided configuration and adds
    all the required Helm repositories
    """
    for chart in config['charts']:
        if config['charts'][chart]['enabled'] == True:
            repository_name = config['charts'][chart]['repository_name']
            repository_url = config['charts'][chart]['repository_url']
            process = subprocess.run(['helm', 'repo', 'add', repository_name, repository_url])

    process = subprocess.run(['helm', 'repo', 'update'])

def create_cluster(config):
    """
    Initializes the k3d cluster using the provided configuration
    """
    try:
        process = subprocess.run(['k3d', 'cluster', 'create', config['cluster']['name'], '--api-port', str(config['cluster']['ports']['apiserver']),
        '-p', str(config['cluster']['ports']['ingress']) + ':80@loadbalancer', '--servers', str(config['cluster']['masters']),
        '--agents', str(config['cluster']['workers'])
        ])
    except :
        print('Unexpected error:', sys.exc_info()[0])

def create_namespaces(config):
    """
    Goes through the provided configuration and creates
    all the required Kubernetes namespaces
    """

    existing_namespaces = str(subprocess.check_output(['kubectl', 'get', 'namespaces', '-o', 'name'])).split('\\n')
    for chart in config['charts']:
        if config['charts'][chart]['enabled'] == True :
            namespace = config['charts'][chart]['namespace']
            if 'namespace/'+namespace not in existing_namespaces :
                process = subprocess.run(['kubectl', 'create', 'namespace', namespace])
                existing_namespaces.append('namespace/'+namespace)

def install_charts(config):
    """
    Installing the charts enabled in the configuration
    """
    for chart in config['charts']:
        if config['charts'][chart]['enabled'] == True:
            chart_name = config['charts'][chart]['name']
            namespace = config['charts'][chart]['namespace']
            values = ''
            parameters = []
            if config['charts'][chart]['parameters']:
                for parameter in config['charts'][chart]['parameters']:
                    parameters.append(parameter + '=' + config['charts'][chart]['parameters'][parameter])
                values = ','.join(parameters)
                process = subprocess.run(['helm', 'install', chart, chart_name, '--namespace', namespace, '--set', values])
            else:
                process = subprocess.run(['helm', 'install', chart, chart_name, '--namespace', namespace])

def init():
    """
    Initializes a local kubernetes cluster for the current project
    and installs the different dependencies configured in the YAML file
    """
    check_dependencies()
    config = parse_yaml()

    create_cluster(config)
    create_namespaces(config)
    add_repositories(config)
    install_charts(config)

def deploy():
    """
    Deploys the current application into the local Kubernetes cluster
    so it is available behind the ingress controller
    """
    # put this in the create_namespace function
    process = subprocess.run(['kubectl', 'create', 'namespace', "app"])

    # put this in the add_repositories
    # qualifio "https://charts.k8s.qualif.io"

    config = parse_yaml()
    process = subprocess.run(['docker', 'build', '-t', 'localapp:dev', './../'])
    process = subprocess.run(['k3d', 'image', 'import', 'localapp:dev', '-c', config['cluster']['name']])
    # process = subprocess.run(['kubectl', '-n', 'app', 'create', 'deployment', 'test','--image=localapp:dev'])

def destroy():
    """
    Destroys the local Kubernetes cluster associated with the current project
    """
    config = parse_yaml()
    process = subprocess.run(['k3d', 'cluster', 'delete', config['cluster']['name']])

def main():
    """
    Main part of the script, checks for dependencies, parses arguments and launch
    the appropriate actions
    """

    # define allowed actions
    actions = { 'init': init, 'deploy': deploy, 'destroy': destroy }

    # define allowed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=actions.keys())

    # if no argument was provided, force help display
    if len(sys.argv) <= 1:
        sys.argv.append('--help')

    # parse the argument and call the associated function
    args = parser.parse_args()
    action = actions[args.action]
    action()

if __name__ == '__main__':
    main()
