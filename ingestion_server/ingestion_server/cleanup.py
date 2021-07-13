import logging as log
import time
import multiprocessing
import uuid
import requests as re
import tldextract
from psycopg2.extras import DictCursor, Json
from ingestion_server.indexer import database_connect, DB_BUFFER_SIZE
from urllib.parse import urlparse
"""
Functions for processing data when it is imported into the CC Catalog. This
includes cleaning up malformed URLs and filtering out undesirable tags.
"""

# Number of records to buffer in memory at once
CLEANUP_BUFFER_SIZE = DB_BUFFER_SIZE

# Filter out tags that exactly match these terms. All terms should be lowercase.
TAG_DENYLIST = {
    'no person',
    'squareformat',
    'uploaded:by=flickrmobile',
    'uploaded:by=instagram',
    'flickriosapp:filter=flamingo'
}

# Filter out tags that contain the following terms. All entrees should be
# lowercase.
TAG_CONTAINS_DENYLIST = {
    'flickriosapp',
    'uploaded',
    ':',
    '=',
    'cc0',
    'by',
    'by-nc',
    'by-nd',
    'by-sa',
    'by-nc-nd',
    'by-nc-sa',
    'pdm'
}

# Filter out low-confidence tags, which indicate that the machine-generated tag
# may be inaccurate.
TAG_MIN_CONFIDENCE = 0.90


def _tag_denylisted(tag):
    """ Tag is banned or contains a banned substring. """
    if tag in TAG_DENYLIST:
        return True
    for denylisted_substring in TAG_CONTAINS_DENYLIST:
        if denylisted_substring in tag:
            return True
    return False


class CleanupFunctions:
    """
    A cleanup function takes one parameter and returns the "cleaned" version if
    an update is required, otherwise None.

    Cleanup functions are dispatched in the _cleanup_config dictionary.
    """
    @staticmethod
    def cleanup_url(url, tls_support):
        """
        Add protocols to the URI if they are missing, else return None.
        """
        parsed = urlparse(url)
        if parsed.scheme == '':
            _tld = tldextract.extract(url)
            _tld = f'{_tld.subdomain}.{_tld.domain}.{_tld.suffix}'
            try:
                tls_supported = tls_support[_tld]
            except KeyError:
                tls_supported = TlsTest.test_tls_supported(url)
                tls_support[_tld] = tls_supported
                log.info(f'Tested domain {_tld}')

            if tls_supported:
                return f"'https://{url}'"
            else:
                return f"'http://{url}'"
        else:
            return None

    @staticmethod
    def cleanup_tags(tags):
        """
        Delete tags because they have low accuracy or because they are in the
        denylist. If no change is made, return None.
        :return: A SQL fragment if an update is required or None
        """
        update_required = False
        tag_output = []
        if not tags:
            return None
        for tag in tags:
            below_threshold = False
            if 'accuracy' in tag and tag['accuracy'] < TAG_MIN_CONFIDENCE:
                below_threshold = True
            if 'name' in tag:
                lower_tag = tag['name'].lower()
                should_filter = _tag_denylisted(lower_tag) or below_threshold
            else:
                log.warning(f'Filtering malformed tag "{tag}" in "{tags}"')
                should_filter = True
            if should_filter:
                update_required = True
            else:
                tag_output.append(tag)

        if update_required:
            fragment = Json(tag_output)
            return fragment
        else:
            return None


# Define which tables, sources, and fields require cleanup. Map the field
# to a cleanup function that returns either a cleaned version of the field
# or 'None' to signal that no update is required.
_cleanup_config = {
    'tables': {
        'image': {
            'sources': {
                # Applies to all sources.
                '*': {
                    'fields': {
                        'tags': CleanupFunctions.cleanup_tags,
                        'url': CleanupFunctions.cleanup_url,
                        'creator_url': CleanupFunctions.cleanup_url,
                        'foreign_landing_url': CleanupFunctions.cleanup_url
                    }
                }
            }
        },
        'audio': {
            'sources': {
                # Applies to all sources.
                '*': {
                    'fields': {
                        'tags': CleanupFunctions.cleanup_tags,
                        'url': CleanupFunctions.cleanup_url,
                        'creator_url': CleanupFunctions.cleanup_url,
                        'foreign_landing_url': CleanupFunctions.cleanup_url
                    }
                }
            }
        }
    }
}


class TlsTest:
    """
    URLs crawled from upstream are often lacking protocol information, or
    use HTTP when HTTPS is available. We have to test a small sample of the
    URLs to determine what protocol should be appended to each URL in the
    event that it is missing or incorrect.
    """
    @classmethod
    def test_tls_supported(cls, url):
        # No protocol provided
        if 'https://' not in url and 'http://' not in url:
            fixed_url = 'http://' + url
            return cls.test_tls_supported(fixed_url)
        # HTTP provided, but we want to check if HTTPS is supported as well.
        elif 'http://' in url:
            https = url.replace('http://', 'https://')
            try:
                res = re.get(https, timeout=2)
                log.info(f'{https}:{res.status_code}')
                return 200 <= res.status_code < 400
            except re.RequestException:
                return False
        # If HTTPS is in the URL already, we're going to trust that HTTPS is
        # supported.
        return True


def _clean_data_worker(rows, temp_table, sources_config):
    log.info('Starting data cleaning worker')
    global_field_to_func = sources_config['*']['fields']
    worker_conn = database_connect()
    log.info('Data cleaning worker connected to database')
    write_cur = worker_conn.cursor(cursor_factory=DictCursor)
    log.info(f'Cleaning {len(rows)} rows')
    tls_cache = {}
    start_time = time.time()
    for row in rows:
        # Map fields that need updating to their cleaning functions
        source = row['source']
        _id = row['id']
        if source in sources_config:
            source_field_to_func = sources_config[source]['fields']
            # Merge source-local and global function field mappings
            fields_to_update = \
                {**global_field_to_func, **source_field_to_func}
        else:
            fields_to_update = global_field_to_func
        # Map fields to their cleaned data
        cleaned_data = {}
        for update_field in fields_to_update:
            dirty_value = row[update_field]
            if not dirty_value:
                continue
            cleaning_func = fields_to_update[update_field]
            if cleaning_func == CleanupFunctions.cleanup_url:
                clean = cleaning_func(url=dirty_value, tls_support=tls_cache)
            else:
                clean = cleaning_func(dirty_value)
            if clean:
                cleaned_data[update_field] = clean
        # Generate SQL update for all the fields we just cleaned
        update_field_expressions = []
        for field in cleaned_data:
            update_field_expressions.append(
                f'{field} = {cleaned_data[field]}'
            )
        if len(update_field_expressions) > 0:
            update_query = f"""UPDATE {temp_table} SET
            {', '.join(update_field_expressions)} WHERE id = {_id}
            """
            write_cur.execute(update_query)
    log.info(f'TLS cache: {tls_cache}')
    log.info('Worker committing changes...')
    worker_conn.commit()
    write_cur.close()
    worker_conn.close()
    end_time = time.time()
    total_time = end_time - start_time
    log.info(f'Worker finished batch in {total_time}')
    return True


def clean_image_data(table):
    """
    Data from upstream can be unsuitable for production for a number of reasons.
    Clean it up before we go live with the new data.

    :param table: The staging table for the new data
    :param upstream_db: A dict specifying the connection details of the upstream
    database.
    :return: None
    """
    # Map each table to the fields that need to be cleaned up. Then, map each
    # field to its cleanup function.
    log.info('Cleaning up data...')
    start_time = time.time()
    table_config = _cleanup_config['tables'][table]

    # Pull data from selected sources only.
    sources = list(_cleanup_config['tables'][table]['sources'])

    # Determine which fields will need updating
    fields_to_clean = set()
    for p in sources:
        _fields = list(table_config['sources'][p]['fields'])
        for f in _fields:
            fields_to_clean.add(f)

    cleanup_selection = f"SELECT id, source, "\
                        f"{', '.join(fields_to_clean)} from temp_import_{table}"
    log.info(f'Running cleanup on selection "{cleanup_selection}"')
    conn = database_connect(autocommit=True)
    cursor_name = f'{table}-{uuid.uuid4()}'
    with conn.cursor(
            name=cursor_name, cursor_factory=DictCursor, withhold=True
    ) as iter_cur:
        iter_cur.itersize = CLEANUP_BUFFER_SIZE
        iter_cur.execute(cleanup_selection)

        # Clean each field as specified in _cleanup_config.
        source_config = table_config['sources']

        log.info('Fetching first batch')
        batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
        jobs = []
        num_workers = multiprocessing.cpu_count()
        num_cleaned = 0
        while batch:
            # Divide updates into jobs for parallel execution.
            batch_start_time = time.time()
            temp_table = f'temp_import_{table}'
            job_size = int(len(batch) / num_workers)
            last_end = -1
            log.info('Dividing work')
            for n in range(1, num_workers + 1):
                log.info(f'Scheduling job {n}')
                start = last_end + 1
                end = job_size * n
                last_end = end
                # Arguments for parallel _clean_data_worker calls
                jobs.append(
                    (batch[start:end], temp_table, source_config)
                )
            pool = multiprocessing.Pool(processes=num_workers)
            log.info(f'Starting {len(jobs)} cleaning jobs')
            conn.commit()
            pool.starmap(_clean_data_worker, jobs)
            pool.close()
            num_cleaned += len(batch)
            batch_end_time = time.time()
            rate = len(batch) / (batch_end_time - batch_start_time)
            log.info(f'Batch finished, records/s: cleanup_rate={rate}')
            log.info(
                f'Fetching next batch. Records cleaned so far: {num_cleaned}'
            )
            jobs = []
            batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
    conn.commit()
    iter_cur.close()
    conn.close()
    end_time = time.time()
    cleanup_time = end_time - start_time
    log.info(f'Cleaned all records in {cleanup_time} seconds')
