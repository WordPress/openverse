<!-- TITLE: Wikimedia Commons -->
<!-- SUBTITLE: Information about the Wikimedia Commons provider -->

# Wikimedia Commons API

We call the following endpoints from [Wikimedia Commons](https://commons.wikimedia.org):

1. `https://commons.wikimedia.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=40&gaisort=timestamp&gaistart=YYYY-MM-DDT00:00:00Z&gaiend=YYYY-MM-DDT00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json`
1. `https://commons.wikimedia.org/w/api.php?action=query&generator=allimages&prop=imageinfo&gailimit=40&gaisort=timestamp&gaistart=YYYY-MM-DDT00:00:00Z&gaiend=YYYY-MM-DDT00:00:00Z&iiprop=url|user|dimensions|extmetadata&iiurlwidth=300&format=json&gaicontinue=SOME_PICTURE.jpg`

For both of these, we replace `YYYY-MM-DD` with dates (we only pull data for images uploaded / updated between these dates). We use the second query if there are more than 40 images between the specified dates, giving a continue location as the next picture (represented by `SOME_PICTURE.jpg`). These requests each return a json of the following form:

```json
{
  "batchcomplete": "",
  "continue": {
    "gaicontinue": "20191101000510|James_Allen_da_Luz.png",
    "continue": "gaicontinue||"
  },
  "query": {
    "pages": {
      "83547663": {
        "pageid": 83547663,
        "ns": 6,
        "title": "File:'Buurpraatje', SK-A-2607.jpg",
        "imagerepository": "local",
        "imageinfo": [
          {
            "user": "Mr.Nostalgic",
            "size": 1353326,
            "width": 3746,
            "height": 2400,
            "thumburl": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/%27Buurpraatje%27%2C_SK-A-2607.jpg/300px-%27Buurpraatje%27%2C_SK-A-2607.jpg",
            "thumbwidth": 300,
            "thumbheight": 192,
            "url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/%27Buurpraatje%27%2C_SK-A-2607.jpg",
            "descriptionurl": "https://commons.wikimedia.org/wiki/File:%27Buurpraatje%27,_SK-A-2607.jpg",
            "descriptionshorturl": "https://commons.wikimedia.org/w/index.php?curid=83547663",
            "extmetadata": {
              "DateTime": {
                "value": "2019-11-01 00:04:22",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "ObjectName": {
                "value": "'Buurpraatje', SK-A-2607",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "CommonsMetadataExtension": {
                "value": 1.2,
                "source": "extension",
                "hidden": ""
              },
              "Categories": {
                "value": "1897 paintings|19th-century paintings in the Rijksmuseum Amsterdam|CC-Zero|Paintings by Jozef Israëls in the Rijksmuseum Amsterdam",
                "source": "commons-categories",
                "hidden": ""
              },
              "Assessments": {
                "value": "",
                "source": "commons-categories",
                "hidden": ""
              },
              "ImageDescription": {
                "value": "<br><br><big><b>Identificatie</b></big><br><b>Titel(s): '</b>Buurpraatje'<br><b>Objecttype:</b> schilderij <br><b>Objectnummer:</b> SK-A-2607<br><b>Opschriften / Merken:</b> signatuur, linksonder: ‘Jozef Israels’<br><b>Omschrijving:</b> 'Buurpraatje'. Twee vrouwen maken een praatje voor een boerenwoning. De linker vrouw is geleund op het houten hek om het erf van de woning. Bij het hek staan enkele dunne bomen.<br><br><big><b>Vervaardiging</b></big><br><b>Vervaardiger:</b> schilder: Jozef Israëls<br><b>Datering:</b> 1897<br><b>Fysieke kenmerken:</b> olieverf op doek<br><b>Materiaal:</b> doek olieverf <br><b>Afmetingen:</b> drager: h 40,5 cm.  × b 62,8 cm.  × d 3,4 cm.  (incl. achterkantbescherming)buitenmaat: d 12,5 cm.  (drager incl. SK-L-3257)<br><br><big><b>Verwerving en rechten</b></big><br><b>Credit line:</b> Schenking van de heer en mevrouw Drucker-Fraser, Montreux<br><b>Verwerving:</b> schenking 4-mei-1912<br><b>Copyright:</b> Publiek domein",
                "source": "commons-desc-page"
              },
              "DateTimeOriginal": {
                "value": "1897",
                "source": "commons-desc-page"
              },
              "Credit": {
                "value": "<a rel=\"nofollow\" class=\"external free\" href=\"http://hdl.handle.net/10934/RM0001.COLLECT.7868\">http://hdl.handle.net/10934/RM0001.COLLECT.7868</a>",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Artist": {
                "value": "Rijksmuseum",
                "source": "commons-desc-page"
              },
              "LicenseShortName": {
                "value": "CC0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "UsageTerms": {
                "value": "Creative Commons Zero, Public Domain Dedication",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "AttributionRequired": {
                "value": "false",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "LicenseUrl": {
                "value": "http://creativecommons.org/publicdomain/zero/1.0/deed.en",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Copyrighted": {
                "value": "True",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Restrictions": {
                "value": "",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "License": {
                "value": "cc0",
                "source": "commons-templates",
                "hidden": ""
              }
            }
          }
        ]
      },

      ...

      "83547651": {
        "pageid": 83547651,
        "ns": 6,
        "title": "File:Wuppertal, Marienstr. 99.jpg",
        "imagerepository": "local",
        "imageinfo": [
          {
            "user": "Im Fokus",
            "size": 4395166,
            "width": 2736,
            "height": 3648,
            "thumburl": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Wuppertal%2C_Marienstr._99.jpg/300px-Wuppertal%2C_Marienstr._99.jpg",
            "thumbwidth": 300,
            "thumbheight": 400,
            "url": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Wuppertal%2C_Marienstr._99.jpg",
            "descriptionurl": "https://commons.wikimedia.org/wiki/File:Wuppertal,_Marienstr._99.jpg",
            "descriptionshorturl": "https://commons.wikimedia.org/w/index.php?curid=83547651",
            "extmetadata": {
              "DateTime": {
                "value": "2019-11-01 00:02:50",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "ObjectName": {
                "value": "Wuppertal, Marienstr. 99",
                "source": "mediawiki-metadata",
                "hidden": ""
              },
              "CommonsMetadataExtension": {
                "value": 1.2,
                "source": "extension",
                "hidden": ""
              },
              "Categories": {
                "value": "2019 photographs of Wuppertal|Marienstraße 99 (Wuppertal)|Self-published work",
                "source": "commons-categories",
                "hidden": ""
              },
              "Assessments": {
                "value": "",
                "source": "commons-categories",
                "hidden": ""
              },
              "ImageDescription": {
                "value": "Wuppertal, Wohnquartier Nordstadt, Marienstr. 99",
                "source": "commons-desc-page"
              },
              "DateTimeOriginal": {
                "value": "2019-10-24 14:03:52",
                "source": "commons-desc-page"
              },
              "Credit": {
                "value": "<span class=\"int-own-work\" lang=\"en\">Own work</span>",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Artist": {
                "value": "<a href=\"//commons.wikimedia.org/wiki/User:Im_Fokus\" title=\"User:Im Fokus\">Im Fokus</a>",
                "source": "commons-desc-page"
              },
              "LicenseShortName": {
                "value": "CC BY-SA 4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "UsageTerms": {
                "value": "Creative Commons Attribution-Share Alike 4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "AttributionRequired": {
                "value": "true",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "LicenseUrl": {
                "value": "https://creativecommons.org/licenses/by-sa/4.0",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Copyrighted": {
                "value": "True",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "Restrictions": {
                "value": "",
                "source": "commons-desc-page",
                "hidden": ""
              },
              "License": {
                "value": "cc-by-sa-4.0",
                "source": "commons-templates",
                "hidden": ""
              }
            }
          }
        ]
      }
    }
  }
}
```

We have elided a number of entries for brevity. Note the `continue.gaicontinue` field in the json. This will be used in the second request listed above. Below is a table showing the mapping from the data contained in such a json to columns in the `image` table in PostgreSQL. Fields from the json are preceded by `$` to mark them. We have omitted the prefix `query.pages.XXXXXX` (where `XXXXXX` is the key for a given page) since it is identical for each field.

```text
         Column          |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $pageid
 foreign_landing_url     | $imageinfo[0].descriptionshorturl
 url                     | $imageinfo[0].url
 thumbnail               | $imageinfo[0].thumburl
 width                   | $imageinfo[0].width
 height                  | $imageinfo[0].height
 license                 | derived from $imageinfo[0].extmetadata.LicenseUrl.value
 license_version         | derived from $imageinfo[0].extmetadata.LicenseUrl.value
 creator                 | derived from $imageinfo[0].extmetadata.Artist.value
 creator_url             | derived from $imageinfo[0].extmetadata.Artist.value
 title                   | $title
 meta_data               | See below
```

## `meta_data` field

The `meta_data` field is a json of the following form:

```text
{
  "description": $imageinfo[0].extmetadata.ImageDescription.value (stripped of html tags)
}
```
