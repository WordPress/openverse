import logging as log
import time
from psycopg2.extras import DictCursor
from urllib.parse import urlparse


# Filter out automatically generated tags that aren't of any use to us.
# Note this list is case insensitive.
TAG_BLACKLIST = {
    'no person',
    'squareformat',
    'uploaded:by=flickrmobile',
    'uploaded:by=instagram'
}

# Filter out low-confidence tags, which indicate that the machine-generated tag
# may be inaccurate.
TAG_MIN_CONFIDENCE_THRESHOLD = 0.90


def _cleanup_url(url):
    """
    Add protocols to the URI if they are missing, else return None.
    """
    parsed = urlparse(url)
    if parsed.scheme == '':
        "'https://{}'".format(url)
    else:
        return None


def _cleanup_tags(tags):
    """
    Delete tags because they have low accuracy or because they are in the
    blacklist. If no change is made, return None.
    :return: A SQL fragment, such as
    """
    update_required = False
    tag_output = []
    for tag in tags:
        should_filter = (tag['name'].lower() in TAG_BLACKLIST or
                         tag['accuracy'] < TAG_MIN_CONFIDENCE_THRESHOLD)
        if not should_filter:
            tag_output.append(tag)
            update_required = True

    if update_required:
        to_sql_tags = str(tag_output)[1:-1]  # Discard list brackets
        fragment = "jsonb_set(tags, '{}'".format(to_sql_tags)
        return fragment
    else:
        return None


# Define which tables, providers, and fields require cleanup. Map the field
# to a cleanup function that returns either a cleaned version of the field
# or 'None' to signal that no update is required.
_cleanup_config = {
    'tables': {
        'image': {
            'providers': {
                # Applies to all tables.
                '*': {
                    'fields': {
                        'tags': _cleanup_tags
                    }
                },
                'floraon': {
                    'fields': {
                        'url': _cleanup_url
                    }
                }
            }
        }
    }
}


def clean_data(conn, table):
    """
    Data from upstream can be unsuitable for production for a number of reasons.
    Clean it up before we go live with the new data.

    :param conn: The database connection
    :param table: The staging table for the new data
    :return: None
    """
    # Map each table to the fields that need to be cleaned up. Then, map each
    # field to its cleanup function.
    log.info('Cleaning up data...')
    start_time = time.time()
    table_config = _cleanup_config['tables'][table]

    # Pull data from selected providers only.
    providers = list(_cleanup_config['tables'][table]['providers'])
    provider_equals = "provider = '{}'"
    all_providers_equal = [provider_equals.format(p) for p in providers]
    provider_condition = ' OR '.join(all_providers_equal)
    # Determine whether we should select every provider.
    global_fields = set()
    if '*' in table_config['providers']:
        _global_fields = list(table_config['providers']['*']['fields'])
        for f in _global_fields:
            global_fields.add(f)
        where_clause = ''
    else:
        where_clause = 'WHERE ' + provider_condition

    # Pull selected fields.
    fields = set()
    for p in providers:
        _fields = list(table_config['providers'][p]['fields'])
        for f in _fields:
            fields.add(f)

    cleanup_query = "SELECT id, provider, {fields} from {table}" \
                    " {where_clause}".format(
                        fields=', '.join(fields),
                        table='temp_import_{}'.format(table),
                        where_clause=where_clause
                    )
    log.info('Running cleanup on selection "{}"'.format(cleanup_query))
    write_cur = conn.cursor(cursor_factory=DictCursor)
    iter_cur = conn.cursor(cursor_factory=DictCursor)
    iter_cur.execute(cleanup_query)

    # Clean each field as specified in _cleanup_config.
    cleaned_count = 0
    provider_config = table_config['providers']
    for row in iter_cur:
        for field in fields:
            row_id = row['id']
            provider = row['provider']
            to_clean = row[field]

            # Select the right cleanup function.
            if field in provider_config['*']['fields']:
                cleanup_function = provider_config['*']['fields'][field]
            elif field in provider_config[provider]['fields']:
                cleanup_function = provider_config[provider]['fields'][field]
            else:
                continue

            cleaned = cleanup_function(to_clean)
            if cleaned:
                cleaned_count += 1
                temporary_table = 'temp_import_{}'.format(table)
                update_query = '''
                    UPDATE {temp_table} SET {field} = {cleaned}
                     WHERE id = {id};
                '''.format(
                    temp_table=temporary_table,
                    field=field,
                    cleaned=cleaned,
                    id=row_id
                )
                write_cur.execute(update_query)
    iter_cur.close()
    write_cur.close()

    end_time = time.time()
    cleanup_time = end_time - start_time
    log.info('Cleaned {} records in {} seconds'.format(
        cleaned_count,
        cleanup_time)
    )
