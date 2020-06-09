def create_mapping(table_name):
    """
    Return the Elasticsearch mapping for a given table in the database.

    :param table_name: The name of the table in the upstream database.
    :return:
    """
    mapping = {
        'image': {
            "settings": {
                "index": {
                    "number_of_shards": 18,
                    "number_of_replicas": 0,
                    "refresh_interval": "-1"
                }
            },
            "mappings": {
                "properties": {
                    "license_version": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "provider": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "source": {
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "license": {
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "url": {
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        },
                        "type": "text"
                    },
                    "license_url": {
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        },
                        "type": "text"
                    },
                    "tags": {
                        "properties": {
                            "accuracy": {
                                "type": "float"
                            },
                            "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                    }
                                },
                                "analyzer": "english"
                            }
                        }
                    },
                    "foreign_landing_url": {
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "id": {
                        "type": "long"
                    },
                    "identifier": {
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        },
                        "type": "text"
                    },
                    "title": {
                        "type": "text",
                        "similarity": "boolean",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        },
                        "analyzer": "english"
                    },
                    "creator": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "created_on": {
                        "type": "date"
                    },
                    "description": {
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "similarity": "boolean"
                            }
                        },
                        "type": "text",
                        "analyzer": "english"
                    },
                    "extension": {
                        "fields": {
                            "keyword": {
                                "ignore_above": 8,
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "aspect_ratio": {
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "size": {
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        },
                        "type": "text"
                    },
                    "normalized_popularity": {
                        "type": "rank_feature"
                    },
                    "authority_boost": {
                        "type": "rank_feature"
                    },
                    "authority_penalty": {
                        "type": "rank_feature",
                        "positive_score_impact": False
                    },
                    "mature": {
                        "type": "boolean"
                    }
                }
            }
        }
    }
    return mapping[table_name]
