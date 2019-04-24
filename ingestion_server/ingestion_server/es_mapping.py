def create_mapping(table_name):
    mapping = {
        'image': {
           "mappings": {
               "doc": {
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
                      "view_count": {
                         "type": "long"
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
                               }
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
                         }
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
                      }
                   }
               }
           }
        }
    }
    return mapping[table_name]
