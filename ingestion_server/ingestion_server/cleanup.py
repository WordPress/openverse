import logging as log
import time
import multiprocessing
from psycopg2.extras import DictCursor, Json
from ingestion_server.indexer import database_connect
from urllib.parse import urlparse


# Number of records to buffer in memory at once
CLEANUP_BUFFER_SIZE = 50000

# Filter out automatically generated tags that aren't of any use to us.
# Note this list is case insensitive.
TAG_BLACKLIST = {
    'no person',
    'squareformat',
    'uploaded:by=flickrmobile',
    'uploaded:by=instagram',
    'cc0'
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
    :return: A SQL fragment if an update is required or None
    """
    update_required = False
    tag_output = []
    for tag in tags:
        below_threshold = False
        if 'accuracy' in tag and tag['accuracy'] < TAG_MIN_CONFIDENCE_THRESHOLD:
            below_threshold = True
        should_filter = (tag['name'].lower() in TAG_BLACKLIST or
                         below_threshold)
        if not should_filter:
            tag_output.append(tag)
            update_required = True

    if update_required:
        fragment = "tags ||  {}".format(Json(tag_output))
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


def _clean_data_worker(rows, temp_table, providers_config):
    log.info('Starting data cleaning worker')
    global_field_to_func = providers_config['*']['fields']
    conn = database_connect()
    log.info('Data cleaning worker connected to database')
    write_cur = conn.cursor(cursor_factory=DictCursor)
    log.info('Cleaning {} rows'.format(len(rows)))
    for row in rows:
        # Map fields that need updating to their cleaning functions
        provider = row['provider']
        _id = row['id']
        if provider in providers_config:
            provider_field_to_func = providers_config[provider]['fields']
            # Merge provider-local and global function field mappings
            fields_to_update = \
                {**global_field_to_func, **provider_field_to_func}
        else:
            fields_to_update = global_field_to_func
        # Map fields to their cleaned data
        cleaned_data = {}
        for update_field in fields_to_update:
            dirty_value = row[update_field]
            cleaning_func = fields_to_update[update_field]
            clean = cleaning_func(dirty_value)
            if clean:
                cleaned_data[update_field] = clean
        # Generate SQL update for all the fields we just cleaned
        update_field_expressions = []
        for field in cleaned_data:
            update_field_expressions.append(
                '{field} = {cleaned}'.format(
                    field=field,
                    cleaned=cleaned_data[field]
                )
            )
        if len(update_field_expressions) > 0:
            update_query = '''
                UPDATE {temp_table} SET {field_expressions} WHERE id = {_id}
            '''.format(
                temp_table=temp_table,
                field_expressions=', '.join(update_field_expressions),
                _id=_id
            )

            write_cur.execute(update_query)
    write_cur.close()
    conn.commit()
    conn.close()
    log.info('Worker finished batch')
    return


def clean_data(table):
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

    # Determine which fields will need updating
    fields_to_clean = set()
    for p in providers:
        _fields = list(table_config['providers'][p]['fields'])
        for f in _fields:
            fields_to_clean.add(f)

    cleanup_selection = "SELECT id, provider, {fields} from {table}".format(
                            fields=', '.join(fields_to_clean),
                            table='temp_import_{}'.format(table),
                        )
    log.info('Running cleanup on selection "{}"'.format(cleanup_selection))
    conn = database_connect()
    iter_cur = conn.cursor(cursor_factory=DictCursor)
    iter_cur.execute(cleanup_selection)

    # Clean each field as specified in _cleanup_config.
    provider_config = table_config['providers']

    batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
    jobs = []
    num_workers = multiprocessing.cpu_count() * 2
    while batch:
        # Divide updates into jobs for parallel execution.
        temp_table = 'temp_import_{}'.format(table)
        job_size = int(len(batch) / num_workers)
        last_end = -1
        for n in range(1, num_workers + 1):
            start = last_end + 1
            end = job_size * n
            last_end = end
            # Arguments for parallel _clean_data_worker calls
            jobs.append(
                (batch[start:end], temp_table, provider_config)
            )
        batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
    pool = multiprocessing.Pool(processes=num_workers)
    log.info('Starting {} cleaning jobs'.format(len(jobs)))
    pool.starmap(_clean_data_worker, jobs)
    pool.close()
    iter_cur.close()
    end_time = time.time()
    cleanup_time = end_time - start_time
    log.info('Cleaned all records in {} seconds'.format(
        cleanup_time)
    )
