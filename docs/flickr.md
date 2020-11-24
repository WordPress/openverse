<!-- TITLE: Flickr -->
<!-- SUBTITLE: Information about the provider Flickr -->

We run an hourly job to pull the last hour's uploads from [Flickr](https://www.flickr.com) 

# Flickr API
You can find the documentation for Flickr API[here](https://www.flickr.com/services/api/).  We currently use the [flickr.photos.search](https://www.flickr.com/services/api/flickr.photos.search.html) method to query the API.  Here is an example showing the type of query string we use:

```text
https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=REDACTED&min_upload_date=2019-11-22%2017:10:00&max_upload_date=2019-11-22%2017:15:00&license=1&media=photos&content_type=1&extras=description,license,date_upload,date_taken,owner_name,tags,o_dims,url_t,url_s,url_m,url_l&per_page=500&format=json&nojsoncallback=1&page=1
```

Such a call to the flickr.photos.search method produces a result of the following format:

```json
{
  "photos": {
    "page": 1,
    "pages": 24306,
    "perpage": 5,
    "total": "121528",
    "photo": [
      {
        "id": "48499561892",
        "owner": "7702423@N04",
        "secret": "2fc41d65e3",
        "server": "65535",
        "farm": 66,
        "title": "Fox Squirrels on a Beautiful Summer Day at the University of Michigan - August 9th, 2019",
        "ispublic": 1,
        "isfriend": 0,
        "isfamily": 0,
        "license": "1",
        "description": {
          "_content": "Fox squirrels out and about at the University of Michigan in Ann Arbor.  Taken on a nice Summer day in Ann Arbor, Friday August 9th, 2019.  I did see my Dodgeball trio - Patches O'Houlihan is looking good, but Steve the Pirate is looking a bit shabby.  I will reach out to see if he needs more medicine.  Beautiful day in Ann Arbor.  "
        },
        "o_width": "6000",
        "o_height": "4000",
        "dateupload": "1565395643",
        "datetaken": "2019-08-09 09:21:44",
        "datetakengranularity": "0",
        "datetakenunknown": "0",
        "ownername": "cseeman",
        "tags": "gobluesquirrels squirrels foxsquirrels easternfoxsquirrels michiganfoxsquirrels universityofmichiganfoxsquirrels annarbor michigan animal campus universityofmichigan umsquirrels08092019 summer eating peanuts augustumsquirrel mange squirrelmange squirreltreatment justin stevethepirate patchesohoulihan",
        "url_t": "https://live.staticflickr.com/65535/48499561892_2fc41d65e3_t.jpg",
        "height_t": 67,
        "width_t": 100,
        "url_s": "https://live.staticflickr.com/65535/48499561892_2fc41d65e3_m.jpg",
        "height_s": 160,
        "width_s": 240,
        "url_m": "https://live.staticflickr.com/65535/48499561892_2fc41d65e3.jpg",
        "height_m": 333,
        "width_m": 500,
        "url_l": "https://live.staticflickr.com/65535/48499561892_2fc41d65e3_b.jpg",
        "height_l": 683,
        "width_l": 1024
      },
      {
        "id": "48499561547",
        "owner": "7702423@N04",
        "secret": "be92df1d66",
        "server": "65535",
        "farm": 66,
        "title": "Fox Squirrels on a Beautiful Summer Day at the University of Michigan - August 9th, 2019",
        "ispublic": 1,
        "isfriend": 0,
        "isfamily": 0,
        "license": "1",
        "description": {
          "_content": "Fox squirrels out and about at the University of Michigan in Ann Arbor.  Taken on a nice Summer day in Ann Arbor, Friday August 9th, 2019.  I did see my Dodgeball trio - Patches O'Houlihan is looking good, but Steve the Pirate is looking a bit shabby.  I will reach out to see if he needs more medicine.  Beautiful day in Ann Arbor.  "
        },
        "o_width": "6000",
        "o_height": "4000",
        "dateupload": "1565395644",
        "datetaken": "2019-08-09 09:22:08",
        "datetakengranularity": "0",
        "datetakenunknown": "0",
        "ownername": "cseeman",
        "tags": "gobluesquirrels squirrels foxsquirrels easternfoxsquirrels michiganfoxsquirrels universityofmichiganfoxsquirrels annarbor michigan animal campus universityofmichigan umsquirrels08092019 summer eating peanuts augustumsquirrel mange squirrelmange squirreltreatment justin stevethepirate patchesohoulihan",
        "url_t": "https://live.staticflickr.com/65535/48499561547_be92df1d66_t.jpg",
        "height_t": 67,
        "width_t": 100,
        "url_s": "https://live.staticflickr.com/65535/48499561547_be92df1d66_m.jpg",
        "height_s": 160,
        "width_s": 240,
        "url_m": "https://live.staticflickr.com/65535/48499561547_be92df1d66.jpg",
        "height_m": 333,
        "width_m": 500,
        "url_l": "https://live.staticflickr.com/65535/48499561547_be92df1d66_b.jpg",
        "height_l": 683,
        "width_l": 1024
      }
    ]
  },
  "stat": "ok"
}
```
# Metadata Mapping

Below is a table showing the mapping from metadata returned by the Flickr API to columns in the image table in PostgreSQL.  Fields from the above json are preceded by '$' to mark them.

```text
        DB Column        |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $id
 foreign_landing_url     | "www.flickr.com/photos/" + $owner + "/" + $id
 url                     | $url_l or $url_m or $url_s (largest which exists)
 thumbnail               | $url_s
 width                   | $width_l or $width_m or $width_s (matches url)
 height                  | $height_l or $height_m or $height_s (matches url)
 license                 | $license
 license_version         | Generated based on $license.  See note.
 creator                 | $ownername
 creator_url             | "www.flickr.com/photos/" + $owner
 title                   | $title
 meta_data               | Specified below
 tags                    | Specified below
```
## metadata field
The metadata field in the DB is a json field with the following information:

```text
{
  "pub_date": $dateupload (unix timestamp),
  "date_taken": $datetaken,
  "description": $description._content
}
```

## tags field
The tags field in the DB is a json field with the following information:
```text
[
  {
    "name": <tagname1>,
    "provider": "flickr"
  },
  {
    "name": <tagname2>,
    "provider": "flickr"
  }
]
```
Here, `<tagnameX>` is one of the tags from the $tags field in the API response.  There are a maximum of 20 tags stored in the tags field.
