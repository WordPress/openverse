import yaml
import datetime
import os
import sys
import traceback
import textwrap

"""
Parses docker-compose file and generates an integration-test-docker-compose.yml.
The generated file is written to the same directory this script resides in.

Q: Why didn't you just use multiple docker-compose files and inheritance?

A: If you are running the development docker-compose file already, launching 
   an inherited elasticsearch/postgres service will result in the containers
   being destroyed and recreated. Using this approach ensures that:
        1) Running the tests doesn't interfere with your development environment.   
        2) The file stays up to date without manual copy-pasting.
"""


this_dir = os.path.dirname(__file__)

parent_docker_compose = this_dir + '../../../docker-compose.yml'
with open(this_dir + parent_docker_compose, 'r') as  docker_compose_file:
    docker_compose = yaml.safe_load(docker_compose_file)
    try:
        db = docker_compose['services']['db']
        es = docker_compose['services']['es']
        # Delete all services except for the database and Elasticsearch
        for service in dict(docker_compose['services']):
            if service != 'es' and service != 'db':
                del docker_compose['services'][service]
        del docker_compose['services']['es']['healthcheck']

        # Expose alternate ports. Use the same internal port defined in the 
        # original docker-compose file.
        db['ports'][0] = '60000' + ':' + db['ports'][0].split(':')[1]
        es['ports'][0] = '60001' + ':' + es['ports'][0].split(':')[1]

        # Rename the services and update ports.
        del docker_compose['services']['db']
        del docker_compose['services']['es']
        docker_compose['services']['integration-db'] = db
        docker_compose['services']['integration-es'] = es

        # Start the document with a warning message 
        name = this_dir + 'integration-test-docker-compose.yml'
        warning_message = '\n'.join(textwrap.wrap(
            'This docker-compose file was generated from '\
            + parent_docker_compose + '. Do not modify this file directly. '\
            'Your changes will be overwritten. Last update: '\
            + str(datetime.datetime.now()), width=79, 
            initial_indent='# ', subsequent_indent='# ')) + '\n\n'

        with open(name, 'w') as integration_docker_compose:
            integration_docker_compose.truncate()
            integration_docker_compose.write(warning_message)
            yaml.dump(docker_compose, integration_docker_compose,\
                default_flow_style=False)
            
    except KeyError as e:
        print(traceback.format_exc())
        print('Failed to parse docker-compose.yml due to missing key. No file'
              ' was written to disk. Missing key: ' + str(e))
        sys.exit(1)
