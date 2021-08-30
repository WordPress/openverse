## Adding new provider API script

Openverse Catalog uses APIs of sites that share openly-licensed media to collect the data about the media and save it to the database. We call the scripts that pull the data from these APIs "Provider API scripts". You can find examples in [`provider_api_scripts` folder](../dags/provider_api_scripts).

To add a Provider API script using this template, you will need to have Python 3 installed on your machine (preferably, version 3.9). You will also need to know the name of provider, and the type of media you are going to collect (`image` or `audio`).

To add a script for collecting audio data from provider named "MyProvider", open your terminal and run
```bash
python3 openverse_catalog/templates/create_api_script.py MyProvider -m audio
```
You should see output similar to this:
```bash
Creating files in path/to/openverse-catalog
API script: openverse_catalog/dags/provider_api_scripts/myprovider.py
API script test: openverse_catalog/dags/provider_api_scripts/test_myprovider.py
Airflow workflow file: openverse_catalog/dags/myprovider_workflow.py

```
The following files have been created:
1. Airflow workflow file. You will probably NOT need to edit it.
2. `myprovider.py` script. This is a template that  simplifies creating an API provider script by providing the basic structure. The scripts use small and easily-testable functions. Follow the instructions within the script comments, and complete all the TODOs. Make sure to look at sample `.json` files that will be saved for testing.
3. `test_myprovider.py`. This is a skeleton for your tests. Write tests for the functions in your Provider API script, using the `json` files with sample API responses.
