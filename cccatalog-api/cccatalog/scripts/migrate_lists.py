import csv
import requests
import json
import logging as log
"""
Tools for migrating legacy lists from CC Search Beta to the CC Catalog platform.
"""


def import_lists_to_catalog(parsed_lists):
    for _list in parsed_lists:
        _list = parsed_lists[_list]
        payload = {
            'title': _list['title'],
            'images': _list['images']
        }
        response = requests.post(
            'http://api-dev.creativecommons.engineering/list',
            data=payload
        )
        if 300 > response.status_code >= 200:
            json_response = json.loads(response.text)
            new_url = json_response['url']
            print(_list['email'], new_url, _list['title'], sep=',')
        else:
            # Ignore bad data.
            continue
    log.info('Migrated {} lists successfully'.format(len(parsed_lists)))


if __name__ == '__main__':
    with open('csvs/lists.csv', 'r') as lists, \
            open('csvs/list_images.csv', 'r') as list_images, \
            open('csvs/users.csv', 'r') as users:
        lists = csv.DictReader(lists)
        list_images = csv.DictReader(list_images)
        users = csv.DictReader(users)

        # Compile all of the data required to migrate the lists and find the
        # emails of their owners.
        users_dict = {row['id']: row['email'] for row in users}
        lists_dict = {}
        for row in lists:
            if row['owner_id'] == '':
                continue
            lists_dict[row['id']] = {
                'email': users_dict[row['owner_id']],
                'title': row['title'],
                'images': []
            }
        for row in list_images:
            if row['list_id'] in lists_dict:
                lists_dict[row['list_id']]['images'].append(row['image_id'])

        # Use the API to migrate the lists.
        import_lists_to_catalog(lists_dict)
