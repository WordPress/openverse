#!/usr/bin/env python3
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
        1) Running tests doesn't interfere with your development environment.   
        2) The file stays up-to-date without manual copy-pasting.
        3) We don't blow up running containers on Travis CI.
"""

this_dir = os.path.dirname(os.path.realpath(__file__))
outname = this_dir + '/integration-test-docker-compose.yml'
parent_docker_compose = this_dir + '/../../docker-compose.yml'

with open(parent_docker_compose, 'r') as docker_compose_file:
    docker_compose = yaml.safe_load(docker_compose_file)
    try:
        db = docker_compose['services']['db']
        es = docker_compose['services']['es']
        ingestion_server = docker_compose['services']['ingestion-server']
        upstream_db = docker_compose['services']['upstream_db']

        # Delete services we're not testing.
        desired_services = {'es', 'db', 'ingestion-server', 'upstream_db'}
        for service in dict(docker_compose['services']):
            if service not in desired_services:
                del docker_compose['services'][service]
        del docker_compose['services']['es']['healthcheck']

        # Expose alternate ports. Use the same internal port defined in the 
        # original docker-compose file.
        upstream_db_port = upstream_db['ports'][0].split(':')[1]
        upstream_db['ports'][0] = '59999' + ':' + upstream_db_port
        db['ports'][0] = '60000' + ':' + db['ports'][0].split(':')[1]
        es['ports'][0] = '60001' + ':' + es['ports'][0].split(':')[1]
        ingestion_api_port = ingestion_server['ports'][0].split(':')[1]
        ingestion_server['ports'][0] = '60002' + ':' + ingestion_api_port

        # Configure ingestion server to point to integration containers.
        upstream_name = 'integration-upstream'
        ingestion_server['environment']['DATABASE_HOST'] = 'integration-db'
        ingestion_server['environment']['ELASTICSEARCH_URL'] = 'integration-es'
        ingestion_server['environment']['UPSTREAM_DB_HOST'] = upstream_name
        ingestion_server['depends_on'] = ['integration-es', 'integration-db']
        ingestion_server['build'] = '../'

        # Set the directory correctly in the volume
        ingestion_server['volumes'] = ['../:/ingestion_server']

        # Create a volume for the mock data
        db['volumes'] = ['./mock_data:/mock_data']
        upstream_db['volumes'] = ['./mock_data:/mock_data']

        # Rename the services and update ports.
        for service in dict(docker_compose['services']):
            if service in desired_services:
                del docker_compose['services'][service]
        docker_compose['services']['integration-db'] = db
        docker_compose['services']['integration-es'] = es
        docker_compose['services']['integration-ingestion'] = ingestion_server
        docker_compose['services']['integration-upstream'] = upstream_db

        # Start the document with a warning message
        warning_message = '\n'.join(textwrap.wrap(
            'This docker-compose file was generated from '
            + parent_docker_compose + '. Do not modify this file directly. '
            'Your changes will be overwritten. Last update: '
            + str(datetime.datetime.now()), width=79,
            initial_indent='# ', subsequent_indent='# ')) + '\n\n'

        with open(outname, 'w') as integration_docker_compose:
            integration_docker_compose.truncate()
            integration_docker_compose.write(warning_message)
            yaml.dump(docker_compose, integration_docker_compose,
                      default_flow_style=False)

    except KeyError as e:
        print(traceback.format_exc())
        print('Failed to parse docker-compose.yml due to missing key. No file'
              ' was written to disk. Missing key: ' + str(e))
        sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        print('Failed to generate', outname, 'due to exception:', e)
