"""
Functions for processing data when it is imported into the catalog.

This includes cleaning up malformed URLs and filtering out undesirable tags.
"""

import csv
import logging as log
import multiprocessing
import time
import uuid
from urllib.parse import urlparse

import requests as re
import tldextract
from psycopg2.extras import DictCursor, Json

from ingestion_server.db_helpers import database_connect
from ingestion_server.indexer import DB_BUFFER_SIZE


# Number of records to buffer in memory at once
CLEANUP_BUFFER_SIZE = DB_BUFFER_SIZE

# Filter out tags that exactly match these terms. All terms should be lowercase.
TAG_DENYLIST = {
    "no person",
    "squareformat",
    "uploaded:by=flickrmobile",
    "uploaded:by=instagram",
    "flickriosapp:filter=flamingo",
}

# Filter out tags that contain the following terms. All entrees should be
# lowercase.
TAG_CONTAINS_DENYLIST = {
    "flickriosapp",
    "uploaded",
    ":",
    "=",
    "cc0",
    "by",
    "by-nc",
    "by-nd",
    "by-sa",
    "by-nc-nd",
    "by-nc-sa",
    "pdm",
}

# Filter out low-confidence tags, which indicate that the machine-generated tag
# may be inaccurate.
TAG_MIN_CONFIDENCE = 0.90

# We know that flickr and wikimedia support TLS, so we can add them here
TLS_CACHE = {
    "www.flickr.com": True,
    "commons.wikimedia.org": True,
    ".geograph.org.uk": True,
    "www.geograph.org.uk": True,
    ".eol.org": True,
    "www.eol.org": True,
    ".digitaltmuseum.org": True,
    "collections.musee-mccord.qc.ca": False,
}


def _tag_denylisted(tag):
    """Check if a tag is banned or contains a banned substring."""

    if tag in TAG_DENYLIST:
        return True
    for denylisted_substring in TAG_CONTAINS_DENYLIST:
        if denylisted_substring in tag:
            return True
    return False


class CleanupFunctions:
    """
    This class is a loose collection of static cleanup functions.

    A cleanup function takes one parameter and returns the "cleaned" version if
    an update is required, otherwise None.

    Cleanup functions are dispatched in the _cleanup_config dictionary.
    """

    @staticmethod
    def cleanup_url(url, tls_support):
        """
        Add protocols to the URI if they are missing.

        :return: the URL with the protocol if an update is needed, ``None`` otherwise
        """

        parsed = urlparse(url)
        if parsed.scheme == "":
            _tld = tldextract.extract(url)
            _tld = f"{_tld.subdomain}.{_tld.domain}.{_tld.suffix}"
            try:
                tls_supported = tls_support[_tld]
            except KeyError:
                tls_supported = TlsTest.test_tls_supported(url)
                tls_support[_tld] = tls_supported
                log.debug(f"Tested domain {_tld}")

            if tls_supported:
                return f"'https://{url}'"
            else:
                return f"'http://{url}'"
        else:
            return None

    @staticmethod
    def cleanup_tags(tags):
        """
        Delete denylisted and low-accuracy tags.

        :return: an SQL fragment if an update is needed, ``None`` otherwise
        """

        update_required = False
        tag_output = []
        if not tags:
            return None
        for tag in tags:
            below_threshold = False
            if "accuracy" in tag and float(tag["accuracy"]) < TAG_MIN_CONFIDENCE:
                below_threshold = True
            if "name" in tag and isinstance(tag["name"], str):
                lower_tag = tag["name"].lower()
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
    "tables": {
        "image": {
            "sources": {
                # Applies to all sources.
                "*": {
                    "fields": {
                        "tags": CleanupFunctions.cleanup_tags,
                        "url": CleanupFunctions.cleanup_url,
                        "creator_url": CleanupFunctions.cleanup_url,
                        "foreign_landing_url": CleanupFunctions.cleanup_url,
                    }
                }
            }
        }
    }
}


def _get_cleanable_fields(table):
    """
    Extract global and sources-specific field names from
    _cleanup_config for specific table.
    """
    cleanable_fields = []
    for source in _cleanup_config["tables"][table]["sources"].values():
        cleanable_fields += list(source["fields"].keys())
    return cleanable_fields


class TlsTest:
    """
    Test URLs to add the correct protocol when missing and use HTTPS when available.

    URLs crawled from upstream are often lacking protocol information, or
    use HTTP when HTTPS is available. We have to test a small sample of the
    URLs to determine what protocol should be appended to each URL in the
    event that it is missing or incorrect.
    """

    @classmethod
    def test_tls_supported(cls, url):
        # No protocol provided
        if "https://" not in url and "http://" not in url:
            fixed_url = "http://" + url
            return cls.test_tls_supported(fixed_url)
        # HTTP provided, but we want to check if HTTPS is supported as well.
        elif "http://" in url:
            https = url.replace("http://", "https://")
            try:
                res = re.get(https, timeout=2)
                log.info(f"{https}:{res.status_code}")
                return 200 <= res.status_code < 400
            except re.RequestException:
                return False
        # If HTTPS is in the URL already, we're going to trust that HTTPS is
        # supported.
        return True


def _clean_data_worker(rows, temp_table, sources_config, all_fields: list[str]):
    log.info("Starting data cleaning worker")
    global_field_to_func = sources_config["*"]["fields"]
    worker_conn = database_connect()
    log.info("Data cleaning worker connected to database")
    write_cur = worker_conn.cursor(cursor_factory=DictCursor)
    log.info(f"Cleaning {len(rows)} rows")

    start_time = time.perf_counter()
    cleaned_values = {field: [] for field in all_fields}
    for row in rows:
        source, _id, identifier = row["source"], row["id"], row["identifier"]

        # Map fields that need updating to their cleaning functions
        fields_to_update = {**global_field_to_func}
        if source in sources_config:
            source_field_to_func = sources_config[source]["fields"]
            # Merge source-local and global function field mappings
            fields_to_update |= {**source_field_to_func}

        # Map fields to their cleaned data
        cleaned_data = {}
        for update_field in fields_to_update:
            dirty_value = row[update_field]
            if not dirty_value:
                continue
            cleaning_func = fields_to_update[update_field]
            if cleaning_func == CleanupFunctions.cleanup_url:
                clean = cleaning_func(url=dirty_value, tls_support=TLS_CACHE)
            else:
                clean = cleaning_func(dirty_value)
            if clean:
                cleaned_data[update_field] = clean
                log.debug(
                    f"Updated {update_field} for {identifier} "
                    f"from '{dirty_value}' to '{clean}'"
                )
        # Generate SQL update for all the fields we just cleaned
        update_field_expressions = []
        for field, clean_value in cleaned_data.items():
            update_field_expressions.append(f"{field} = {clean_value}")
            # Save cleaned values for later
            # (except for tags, which take up too much space)
            if field == "tags":
                continue
            cleaned_values[field].append((identifier, clean_value))

        if len(update_field_expressions) > 0:
            update_query = f"""UPDATE {temp_table} SET
            {', '.join(update_field_expressions)} WHERE id = {_id}
            """
            write_cur.execute(update_query)
    log.info(f"TLS cache: {TLS_CACHE}")
    log.info("Worker committing changes...")
    worker_conn.commit()
    write_cur.close()
    worker_conn.close()
    end_time = time.perf_counter()
    total_time = end_time - start_time
    log.info(f"Worker finished batch in {total_time}")
    return cleaned_values


def save_cleaned_data(result: dict) -> dict[str, int]:
    log.info("Saving cleaned data...")
    start_time = time.perf_counter()

    cleanup_counts = {field: len(items) for field, items in result.items()}
    for field, cleaned_items in result.items():
        # Skip the tag field because the file is too large and fills up the disk
        if field == "tag":
            continue
        if cleaned_items:
            with open(f"{field}.tsv", "a") as f:
                csv_writer = csv.writer(f, delimiter="\t")
                csv_writer.writerows(cleaned_items)

    end_time = time.perf_counter()
    total_time = end_time - start_time
    log.info(f"Finished saving cleaned data in {total_time:.3f},\n{cleanup_counts}")
    return cleanup_counts


def clean_image_data(table):
    """
    Clean up data loaded from upstream that is unsuitable for prod before going live.

    :param table: The staging table for the new data
    :return: None
    """

    # Map each table to the fields that need to be cleaned up. Then, map each
    # field to its cleanup function.
    log.info("Cleaning up data...")
    start_time = time.perf_counter()
    table_config = _cleanup_config["tables"][table]

    # Pull data from selected sources only.
    sources = list(_cleanup_config["tables"][table]["sources"])

    # Determine which fields will need updating
    fields_to_clean = set()
    for p in sources:
        _fields = list(table_config["sources"][p]["fields"])
        fields_to_clean.update(_fields)

    cleanup_selection = (
        f"SELECT id, identifier, source, "
        f"{', '.join(fields_to_clean)} from temp_import_{table}"
    )
    log.info(f'Running cleanup on selection "{cleanup_selection}"')
    conn = database_connect(autocommit=True)
    cursor_name = f"{table}-{uuid.uuid4()}"
    with conn.cursor(
        name=cursor_name, cursor_factory=DictCursor, withhold=True
    ) as iter_cur:
        iter_cur.itersize = CLEANUP_BUFFER_SIZE
        iter_cur.execute(cleanup_selection)

        # Clean each field as specified in _cleanup_config.
        source_config = table_config["sources"]

        log.info("Fetching first batch")
        batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
        jobs = []
        num_workers = multiprocessing.cpu_count()
        num_cleaned = 0
        cleaned_counts_by_field = {field: 0 for field in fields_to_clean}
        cleanable_fields_for_table = _get_cleanable_fields("image")

        while batch:
            # Divide updates into jobs for parallel execution.
            batch_start_time = time.perf_counter()
            temp_table = f"temp_import_{table}"
            job_size = int(len(batch) / num_workers)
            last_end = -1
            log.info("Dividing work")
            for n in range(1, num_workers + 1):
                log.info(f"Scheduling job {n}")
                start = last_end + 1
                end = job_size * n
                last_end = end
                # Arguments for parallel _clean_data_worker calls
                jobs.append(
                    (
                        batch[start:end],
                        temp_table,
                        source_config,
                        cleanable_fields_for_table,
                    )
                )
            with multiprocessing.Pool(processes=num_workers) as pool:
                log.info(f"Starting {len(jobs)} cleaning jobs")

                for result in pool.starmap(_clean_data_worker, jobs):
                    batch_cleaned_counts = save_cleaned_data(result)
                    for field in batch_cleaned_counts:
                        cleaned_counts_by_field[field] += batch_cleaned_counts[field]
                pool.close()
                pool.join()

            num_cleaned += len(batch)
            batch_end_time = time.perf_counter()
            rate = len(batch) / (batch_end_time - batch_start_time)
            log.info(
                f"Batch finished, records/s: cleanup_rate={rate}, "
                f"items cleaned: {batch_cleaned_counts}.\n"
                f"Fetching next batch."
            )
            jobs = []
            batch = iter_cur.fetchmany(size=CLEANUP_BUFFER_SIZE)
    conn.commit()
    iter_cur.close()
    conn.close()
    end_time = time.perf_counter()
    cleanup_time = end_time - start_time
    log.info(
        f"Cleaned all records in {cleanup_time:.3f} seconds,"
        f"counts: {cleaned_counts_by_field}"
    )
