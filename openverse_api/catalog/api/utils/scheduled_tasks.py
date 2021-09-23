import logging as log
import time

from catalog.api.models import Image
from django.core.exceptions import ObjectDoesNotExist
from django_cron import CronJobBase, Schedule
from django_redis import get_redis_connection


"""
Cron-like tasks run at a set interval. `python3 manage.py runcrons` will
execute any scheduled tasks. This is intended to run on all instances of the
server.

Even though there may be multiple instances of the server running, a job is
guaranteed to execute only once. Jobs are not run unless it can acquire a lock
inside of the cache (shared by all instances of openverse_api).
"""
model_name_to_instance = {"Image": Image}


class SaveCachedTrafficStats(CronJobBase):
    """
    Traffic statistics (view count, API usage) are stored in Redis for fast
    updates and retrieval. In order to ensure durability of statistics and
    minimize cache memory requirements, they are intermittently replicated to
    the database in small batches and subsequently evicted from the cache if
    they exceed a certain age. Recently updated view data is replicated but not
    evicted.

    After traffic statistics have been stored in the database, they are
    replicated to Elasticsearch by es-syncer and used to compute trending views.
    """

    RUN_EVERY_MINS = 20
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    # Number of failures before notification is sent
    MIN_NUM_FAILURES = 5
    code = "catalog.api.utils.scheduled_tasks.SaveCachedTrafficStats"

    def do(self):
        log.info("Starting view count persistence job")
        redis = get_redis_connection("traffic_stats")
        one_day_ago = time.time() - 60 * 60 * 24
        last_save_time = time.time() - (self.RUN_EVERY_MINS * 60)
        old_view_data = redis.zrangebyscore("model-last-accessed", "-inf", one_day_ago)
        recent_view_data = redis.zrangebyscore(
            "model-last-accessed", last_save_time, "inf"
        )
        self._save_views_to_db(old_view_data, evict_from_cache=True)
        redis.zremrangebyscore("model-last-accessed", "-inf", one_day_ago)
        self._save_views_to_db(recent_view_data)
        log.info("Saved cached traffic stats")

    @staticmethod
    def _save_views_to_db(view_keys, evict_from_cache=False):
        if not view_keys:
            return
        redis = get_redis_connection("traffic_stats")
        view_keys = [x.decode("utf-8") for x in view_keys]
        for obj in view_keys:
            model_name, model_id = obj.split(":")
            if model_name in model_name_to_instance:
                model = model_name_to_instance[model_name]
                try:
                    instance = model.objects.get(id=model_id)
                    instance.view_count = redis.get(obj)
                    instance.save(update_fields=["view_count"])
                except ObjectDoesNotExist:
                    log.warning("Tried to save views of non-existent instance.")
            else:
                log.warning(
                    "Tried to persist views of non-existent model " + model_name
                )
        if evict_from_cache:
            redis.delete(*view_keys)
        log.info("Saved " + str(view_keys))
