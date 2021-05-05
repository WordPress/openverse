<!-- TITLE: Metmuseum -->
<!-- SUBTITLE: Imformation about the provider Met Museum-->

# Met Museum API

We call the `objects` endpoint from the Met Museum's API in two ways:

1. `https://collectionapi.metmuseum.org/public/collection/v1/objects/?metadataDate=YYYY-MM-DD`
2. `https://collectionapi.metmuseum.org/public/collection/v1/objects/XXXXX`

The only information we use from the first type of call is a list of object IDs, which we use in the second call in place of `XXXXX`. The second type of call returns a json of the following form:

```json
{
  "objectID": 786829,
  "isHighlight": false,
  "accessionNumber": "2019.66.1a–o–.95",
  "isPublicDomain": true,
  "primaryImage": "https://images.metmuseum.org/CRDImages/es/original/ESDA Kalimian Temple.jpg",
  "primaryImageSmall": "https://images.metmuseum.org/CRDImages/es/web-large/ESDA Kalimian Temple.jpg",
  "additionalImages": [
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-001.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-002.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-003.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-004.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-005.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-006.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-007.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-008.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-009.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-010.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-011.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-012.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-013.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-014.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-015.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-016.jpg",
    "https://images.metmuseum.org/CRDImages/es/original/LC-2019_66_1a–o_95-017.jpg"
  ],
  "constituents": [
    {
      "role": "Designer",
      "name": "After a design by Thomas Newberry"
    },
    {
      "role": "Maker",
      "name": "Carved and gilded by Messrs. Bartlet, King Street, London"
    },
    {
      "role": "Maker",
      "name": "Gilded silver and brass appurtenances by W. Spurrier"
    }
  ],
  "department": "European Sculpture and Decorative Arts",
  "objectName": "Architectural Model",
  "title": "Architectural model of the temple of King Solomon in Jerusalem",
  "culture": "",
  "period": "",
  "dynasty": "",
  "reign": "",
  "portfolio": "",
  "artistRole": "Designer",
  "artistPrefix": "After a design by",
  "artistDisplayName": "Thomas Newberry",
  "artistDisplayBio": "",
  "artistSuffix": "",
  "artistAlphaSort": "Newberry, Thomas",
  "artistNationality": "",
  "artistBeginDate": "",
  "artistEndDate": "",
  "objectDate": "1883",
  "objectBeginDate": 1883,
  "objectEndDate": 1883,
  "medium": "Gilded wood, gilded carton pierre; gilded silver, gilded bronze; enamel, linen",
  "dimensions": "Temple Alone: Height: 26\" (66 cm); Width: 46\" (117 cm); Depth: 48\" (122 cm).\r\nOverall measurement, including forecourt: Length: 7' 8\" (234 cm); Width: 3' 8\" (112 cm)-",
  "creditLine": "Gift of Albert Kalimian, in honor of Victoria Kalimian and in memory of Rouhollah Kalimian, and in celebration of the Museum's 150th Anniversary, 2019",
  "geographyType": "",
  "city": "",
  "state": "",
  "county": "",
  "country": "",
  "region": "",
  "subregion": "",
  "locale": "",
  "locus": "",
  "excavation": "",
  "river": "",
  "classification": "Woodwork",
  "rightsAndReproduction": "",
  "linkResource": "",
  "metadataDate": "2019-11-28T04:41:18.51Z",
  "repository": "Metropolitan Museum of Art, New York, NY",
  "objectURL": "https://www.metmuseum.org/art/collection/search/786829",
  "tags": []
}
```

Below is a table showing the mapping from metadata returned by the API to columns in the `image` table in PostgreSQL. Fields from the above json are preceded by '$' to mark them.

```text
        DB Column        |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $objectID + idx (see note below)
 foreign_landing_url     | $objectURL
 url                     | $primaryImage or $additional_images[i] (see note below)
 thumbnail               | constructed from url
 license                 | only 'CC0'
 license_version         | only '1.0'
 creator                 | $artistDisplayName
 title                   | $title
 meta_data               | Specified below
```

## metadata field

The metadata field in the DB is a json field with the following information:

```text
{
  "set": $objectURL
  "date": $objectDate,
  "medium": $medium,
  "culture": $culture,
  "credit_line": $creditLine,
  "classification": $classification,
  "accession_number": $accession_number
}
```
