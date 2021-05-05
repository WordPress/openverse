<!-- TITLE: Rawpixel -->
<!-- SUBTITLE: Information about the Rawpixel Provider -->

# RawPixel API

We call the following endpoint from [rawpixel.com](https://rawpixel.com):

`https://api.rawpixel.com/api/v1/search?freecc0=1&html=0&page=X`

Here `X` is a page offset. Such a request returns a json of the following form:

```text
{
  "html": "",
  "spellcheck": [],
  "total": 20586,
  "uid": 0,
  "context": {
    "context": "",
    "masterContext": ""
  },
  "results": [
    {
      "sort": "[739,154,1,1571387376]",
      "nid": 1232608,
      "id": 1232608,
      "view_mode": "photo_grid",
      "attributes": "",
      "keywords_raw": "antique, art, arts, artwork, background, bloom, blooming, blossom, botanical, card, cc0, classic, creative commons, creative commons 0, daisy, decor, decoration, decorative, design, drawing, fine art, floral, flower, graphic, historic, historical, history, illustration, leaves, old, painting, postcard, public domain, retro, vintage, wallpaper, white",
      "image_title": "Colorful flower illustration",
      "image_alt": "Card Depicting Flowers in Blue Background (1865&ndash;1899) by L. Prang & Co. Original from The New York Public Library.…",
      "image_type": "Image",
      "image_type_icon": [
        "<span class=\"icon-galleries-circle-bg\"></span>"
      ],
      "exclusive": false,
      "url": "https://www.rawpixel.com/image/1232608/colorful-flower-illustration",
      "pinterest_share_url": "https://www.rawpixel.com/image/1232608/colorful-flower-illustration",
      "artist_names": "New York Public Library (Source)",
      "artist_twitters": "New%20York%20Public%20Library%20%28Source%29",
      "search_views_month": 588,
      "search_views_max": 1,
      "search_views": 247,
      "field_rating": 7,
      "image_uri": "s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg",
      "original_width": 948,
      "original_height": 1085,
      "image_opengraph": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1200&h=630&fit=crop&dpr=1.5&crop=entropy&fm=pjpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.1.2&s=47efeac53d89a3a2d11201f194a9057f",
      "image_retina": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?h=370&dpr=1.5&fit=default&crop=default&auto=format&fm=pjpg&q=50&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=2bfba172d3486b056660dae02eaafb8d",
      "image": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?h=370&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=6059dd67b7341ecf32a4fa1a9f7342a3",
      "image_pinterest": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=jpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.1.2&s=3865b5e387e483d0bec80abf77626b8d",
      "image_width": "323",
      "image_height": "370",
      "image_big": false,
      "image_2500": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=2500&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=d15667dba1d654afce4417b43a7211a5",
      "image_2000": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=2000&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=b1c7496f68bc10984fb6ecf0816e8bd8",
      "image_1600": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1600&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=6476e2377f2c42579a2ab8c7348aec71",
      "image_1400": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=23d5cb3a8dfb333e6ce6cc88372676fd",
      "image_1200": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1200&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=2cc139754cdb4d6ccef881db7b18db89",
      "image_1000": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1000&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=9b83c859e1943b04cb8d9a7d353ee46e",
      "image_800": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=800&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=b68584269912c68195f69f70aee2a6ef",
      "image_600": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=600&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=b55c2a99779c30b71eafcbc3c1f12ee0",
      "image_400": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=93f8166ae152d496d51e9f150accf517",
      "image_200": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=200&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=f87ea8fa9d74b4d956d87016b0c42c63",
      "image_full": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&bg=F4F4F3&ixlib=js-2.1.2&s=8c3a0512be251f024ed161d5f3d0eaba",
      "image_full_width": "323",
      "image_full_height": "370",
      "figure_style": "\n      flex-grow: 87.37327188940091;\n      width: 218.4331797235023px;\n    ",
      "image_style": "\n    padding-bottom: 114.45147679324894%;\n  ",
      "art": false,
      "art_class": "",
      "free_image": true,
      "freecc0": true,
      "free_or_cc0": true,
      "pinterest_description": "Card Depicting Flowers in Blue Background (1865&ndash;1899) by L. Prang & Co. Original from The New York Public Library. Digitally enhanced by rawpixel. | free image by rawpixel.com / New York Public Library (Source)",
      "logged_in": false,
      "field_image_flag": 14,
      "webbanner": false,
      "artist_account": false,
      "starred": false,
      "showcase": false
    },
    ...,
    {
      "sort": "[703,5330938,1,1554199741]",
      "nid": 600045,
      "id": 600045,
      "view_mode": "photo_grid",
      "attributes": "",
      "keywords_raw": "autumn, brown, cc0, cluster, color, creative commons, creative commons 0, crisp, dried, dry, dying, fall, floor, forest, free, ground, leaf, leaves, natural, nature, old, orange, public domain, season, weathered",
      "image_title": "Autumn forest floor",
      "image_alt": "Cluster of crisp leaves",
      "image_type": "Photo",
      "image_type_icon": [
        "<span class=\"icon-galleries-circle-bg\"></span>"
      ],
      "exclusive": false,
      "url": "https://www.rawpixel.com/image/600045/autumn-forest-floor",
      "pinterest_share_url": "https://www.rawpixel.com/image/600045/autumn-forest-floor",
      "artist_names": "Markus Spiske",
      "artist_twitters": "Markus%20Spiske",
      "search_views_month": 588,
      "search_views_max": 1,
      "search_views": 155,
      "field_rating": 7,
      "image_uri": "s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg",
      "original_width": 5760,
      "original_height": 3840,
      "image_opengraph": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1200&h=630&fit=crop&dpr=1.5&crop=entropy&fm=pjpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.1.2&s=212455222ec6754a2149c3d7d77b93fc",
      "image_retina": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?h=370&dpr=1.5&fit=default&crop=default&auto=format&fm=pjpg&q=50&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=acbfa3ab295c37cbbe4ceac596c91398",
      "image": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?h=370&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=7d1d373033e301708f2e450aa64a56d9",
      "image_pinterest": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=jpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.1.2&s=daee44243509addca78c5c1cdc27ff17",
      "image_width": "555",
      "image_height": "370",
      "image_big": false,
      "image_2500": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=2500&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=b12fab31c027c306f840ce5b021e1f40",
      "image_2000": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=2000&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=daee829eb27e9733e23f7b517e272d50",
      "image_1600": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1600&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=a4f86800f6cb7f0d484a732cf8fedb6d",
      "image_1400": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=e1523740d19e3dd0fee244acdeb81548",
      "image_1200": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1200&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=943464a4700b3c858170d95858235449",
      "image_1000": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1000&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=153664f12c344927ab03c5a009fca2bf",
      "image_800": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=800&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=48ca53c4329131a51a47ba1c257e4dba",
      "image_600": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=600&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=374bb9ddfc275069cc9ed4f2955173d3",
      "image_400": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=f4e6daec413a9457b034a3eb7e8a87fd",
      "image_200": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=200&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&bg=F4F4F3&ixlib=js-2.1.2&s=775b1b4e97d2579883d10cef31feb345",
      "image_full": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/a010-markusspiske-jan19-msp_1811_1110.jpg?w=1400&dpr=1&fit=default&crop=default&auto=format&fm=pjpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&bg=F4F4F3&ixlib=js-2.1.2&s=b7c69583ae7c436e6187522323e15fc0",
      "image_full_width": "555",
      "image_full_height": "370",
      "figure_style": "\n      flex-grow: 150;\n      width: 375px;\n    ",
      "image_style": "\n    padding-bottom: 66.66666666666667%;\n  ",
      "art": false,
      "art_class": "",
      "free_image": true,
      "freecc0": true,
      "free_or_cc0": true,
      "pinterest_description": "Cluster of crisp leaves | free image by rawpixel.com / Markus Spiske",
      "logged_in": false,
      "field_image_flag": 8,
      "webbanner": false,
      "artist_account": false,
      "starred": false,
      "showcase": false
    }
  ],
  "pager": null,
  "title": "Search Free Stock Photos, PSD Mockups & Vectors",
  "blurb": "Search Free and Premium stock photos, vectors and psd mockups",
  "cover_image": "https://img.rawpixel.com/s3fs-private/rawpixel_images/website_content/pdxmas-nypl-89-chim-a.jpg?w=1200&h=630&fit=crop&dpr=1.5&crop=entropy&fm=pjpg&q=75&vib=3&con=3&usm=15&markpad=13&markalpha=90&markscale=10&markx=25&mark=rawpixel-watermark.png&cs=srgb&bg=F4F4F3&ixlib=js-2.1.2&s=47efeac53d89a3a2d11201f194a9057f"
}
```

Note that we have elided some of the returned data for brevity. The rawpixel API returns the information about a number of pictures in the same json, so exercise caution. Also, for this API, the license information is set by the request, and not extracted from the returned json.

Below is a table showing the mapping from metadata returned by the API to columns in the `image` table in PostgreSQL. Fields from the above json are preceded by a `$` to mark them. Also, we will omit `$results[i]` from the paths, as it is simply the path to a given picture's information within the returned json, and would be included in every entry.

```text
         Column          |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $id
 foreign_landing_url     | $url
 url                     | $image_opengraph
 thumbnail               | $image_400
 width                   | $image_opengraph (query parameter w)
 height                  | $image_opengraph (query parameter h)
 license                 | set by initial request to CC0
 license_version         | set by initial request to 1.0
 creator                 | $artists
 creator_url             | metadata
 title                   | metadata
 meta_data               | Not Used
 tags                    | See below
```

The `tags` field consists of a json with the following form:

```text
{
  "name": $keywords_raw (split at ',')
  "provider": "rawpixel"
}
```
