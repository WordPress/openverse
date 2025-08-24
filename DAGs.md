| DAG ID                                                                      | Schedule Interval |
| --------------------------------------------------------------------------- | ----------------- |
| [`prod_elasticsearch_health_check`](#prod_elasticsearch_health_check)       | `*/15 * * * *`    |
| [`staging_elasticsearch_health_check`](#staging_elasticsearch_health_check) | `*/15 * * * *`    |

---

### `prod_elasticsearch_health_check`

This DAG checks the health of the **production** Elasticsearch cluster every 15
minutes. On failure, it sends a Slack alert (throttled to once every 6 hours).
On success, it clears the "in-alarm" variable.

---

### `staging_elasticsearch_health_check`

This DAG checks the health of the **staging** Elasticsearch cluster every 15
minutes. On failure, it sends a Slack alert (throttled to once every 6 hours).
On success, it clears the "in-alarm" variable.| DAG ID | Schedule Interval | |
------------------------------------ | ----------------- | |
[`prod_elasticsearch_health_check`](#prod_elasticsearch_health_check) |
`*/15 * * * *` | |
[`staging_elasticsearch_health_check`](#staging_elasticsearch_health_check) |
`*/15 * * * *` |

---

### `prod_elasticsearch_health_check`

This DAG checks the health of the **production** Elasticsearch cluster every 15
minutes.  
On failure, it sends a Slack alert (throttled to once every 6 hours).  
On success, it clears the "in-alarm" variable.

---

### `staging_elasticsearch_health_check`

This DAG checks the health of the **staging** Elasticsearch cluster every 15
minutes.  
On failure, it sends a Slack alert (throttled to once every 6 hours).  
On success, it clears the "in-alarm" variable.
