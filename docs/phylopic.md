<!-- TITLE: Phylopic -->
<!-- SUBTITLE: Information about the provider Phylopic -->

# Phylopic API

We call the Phylopic API in two different ways:

1. `http://phylopic.org/api/a/image/list/modified/YYYY-MM-DD`
2. `http://phylopic.org/api/a/image/ITEM_UUID?options=credit+licenseURL+pngFiles+submitted+submitter+taxa+canonicalName+string+firstName+lastName`

We extract a list of UUIDs from the response to the first request, which we then use to construct subsequent requests (of the form shown second above filling in an extracted UUID for `ITEM_UUID`).

The response to a UUID-specified request is a json with the following form:

```json
{
  "result": {
    "uid": "311594cf-1cba-441f-951f-4803784a2356",
    "taxa": [
      {
        "canonicalName": {
          "uid": "43647af6-f07e-49b8-92ff-6a1268de70e7",
          "string": "Acanthophis rugosus"
        }
      }
    ],
    "submitted": "2019-11-27 20:00:18",
    "credit": "CNZdenek",
    "pngFiles": [
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.64.png",
        "width": 64,
        "height": 39
      },
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.128.png",
        "width": 128,
        "height": 78
      },
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.256.png",
        "width": 256,
        "height": 156
      },
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.512.png",
        "width": 512,
        "height": 312
      },
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.1024.png",
        "width": 1024,
        "height": 624
      },
      {
        "url": "/assets/images/submissions/311594cf-1cba-441f-951f-4803784a2356.original.png",
        "width": 3798,
        "height": 2316
      }
    ],
    "licenseURL": "http://creativecommons.org/licenses/by-nc/3.0/",
    "submitter": {
      "lastName": "Zdenek",
      "uid": "5aeb06d9-fc67-4a99-8579-7cac28701825",
      "firstName": "Christina"
    }
  },
  "success": true
}
```

Below is a table showing the mapping from metadata returned by the API to columns in the `image` table in PostgreSQL. Fields from the above json are preceded by '$' to mark them.

```text
         Column          |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $result.pngFiles[i].url (prefer the largest available)
 foreign_landing_url     | 'http://phylopic.org/image/' + $result.uid
 url                     | $result.pngFiles[i].url (prefer the largest available)
 thumbnail               | $result.pngFiles[i2].url (only take width 256)
 width                   | $result.pngFiles[i].width (same as url)
 height                  | $result.pngFiles[i].height (same as url)
 license                 | extracted from $result.licenseURL
 license_version         | extracted from $result.licenseURL
 creator                 | $result.submitter.firstName + ' ' + $result.submitter.lastName
 title                   | $result.taxa[0].canonicalName.string
 meta_data               | See below
```

## `meta_data` field

The `meta_data` field is a json of the following form:

```text
{
  "taxa": [
    $result.taxa[0].canonicalName.string,
    $result.taxa[1].canonicalName.string,
    ...,
  ],
  "pub_date": $result.submitted,
  "credit_line": $result.credit
}
```
