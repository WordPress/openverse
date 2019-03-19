import logging as log
import time
from psycopg2.extras import DictCursor
from urllib.parse import urlparse


def _cleanup_url(url):
    """
    Add protocols to the URI if they are missing, else return none.
    :param url:
    :return:
    """
    parsed = urlparse(url)
    if parsed.scheme == '':
        return 'https://' + url
    else:
        return None


# Define which tables, providers, and fields require cleanup. Map the field
# to a cleanup function that returns either a cleaned version of the field
# or 'None' to signal that no update is required.
_cleanup_config = {
    'tables': {
        'image': {
            'providers': {
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

    temporary_table = 'temp_import_{}'.format(table)
    providers = _cleanup_config['tables'][table]['providers'].keys()
    providers = [str(provider) for provider in providers]
    cleaned_count = 0
    for provider in providers:
        cleanup_field_config = \
            _cleanup_config['tables'][table]['providers'][provider]['fields']
        cleanup_fields = list(cleanup_field_config.keys())
        cleanup_query = "SELECT id, {fields} from {table}" \
                        " where provider = '{provider}'".format(
                            fields=','.join(cleanup_fields),
                            table='temp_import_{}'.format(table),
                            provider=provider
        )
        log.info('Running cleanup "{}"'.format(cleanup_query))
        write_cur = conn.cursor(cursor_factory=DictCursor)
        iter_cur = conn.cursor(cursor_factory=DictCursor)
        iter_cur.execute(cleanup_query)
        for row in iter_cur:
            for field in cleanup_fields:
                row_id = row['id']
                to_clean = row[field]
                cleanup_function = cleanup_field_config[field]
                cleaned = cleanup_function(to_clean)
                if cleaned:
                    cleaned_count += 1
                    update_query = '''
                        UPDATE {temp_table} SET {field} = '{cleaned}'
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
