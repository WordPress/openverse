<!-- TITLE: Thingiverse -->
<!-- SUBTITLE: Information about the provider Thingiverse -->

# Thingiverse API

The thingiverse API is queried in a number of different ways. First, to get a list of 'things' to retrieve, and then in a series of steps for each 'thing' in the list.

## Initial API Query

The initial query sends a GET of the form

```
https://api.thingiverse.com/newest?access_token=REDACTED&per_page=30&page=1
```

This returns the following json:

```json
[
  {
    "id": 4002927,
    "name": "Beer can coster",
    "url": "https://api.thingiverse.com/things/4002927",
    "public_url": "https://www.thingiverse.com/thing:4002927",
    "thumbnail": "https://cdn.thingiverse.com/site/img/default/Gears_thumb_medium.jpg",
    "creator": {
      "id": 3158466,
      "name": "nwasicsko",
      "first_name": "Nicholas",
      "last_name": "Wasicsko",
      "url": "https://api.thingiverse.com/users/nwasicsko",
      "public_url": "https://www.thingiverse.com/nwasicsko",
      "thumbnail": "https://cdn.thingiverse.com/site/img/default/avatar/avatar_default_thumb_medium.jpg",
      "accepts_tips": false
    },
    "is_private": false,
    "is_purchased": false,
    "is_published": true
  },
  {
    "id": 4002928,
    "name": "Cylinder",
    "url": "https://api.thingiverse.com/things/4002928",
    "public_url": "https://www.thingiverse.com/thing:4002928",
    "thumbnail": "https://cdn.thingiverse.com/assets/a3/a1/00/d1/f3/medium_thumb_Tremendous_Elzing.stl",
    "creator": {
      "id": 1558711,
      "name": "LvdBroek",
      "first_name": "Lars",
      "last_name": "van den Broek",
      "url": "https://api.thingiverse.com/users/LvdBroek",
      "public_url": "https://www.thingiverse.com/LvdBroek",
      "thumbnail": "https://cdn.thingiverse.com/renders/ac/ab/d6/1e/67/57ae93338bcfb5e224a1148603443ef9_thumb_medium.jpg",
      "accepts_tips": false
    },
    "is_private": false,
    "is_purchased": false,
    "is_published": true
  }
]
```

The only thing we use from this response is the id for each 'thing'. These ids are collected, and used to construct the requests in the following stages.

## Second Stage

Next, the script makes three requests for each 'thing' found in the initialization step, extracting information from each response. These queries are HTTP GET requests:

1. `https://api.thingiverse.com/things/3730558?access_token=REDACTED`
2. `https://api.thingiverse.com/things/3730558/tags?access_token=REDACTED`
3. `https://api.thingiverse.com/things/3730558/files?access_token=REDACTED`

In these examples, `3730558` is one of the ids gathered from the first stage. We will document the information gathered from the response to each query in order.

### REQUEST: `https://api.thingiverse.com/things/3730558?access_token=REDACTED`

This request returns a json of the following form:

```json
{
  "id": 3730558,
  "name": "Alfawise U30 - Guida filamento",
  "thumbnail": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_thumb_medium.jpg",
  "url": "https://api.thingiverse.com/things/3730558",
  "public_url": "https://www.thingiverse.com/thing:3730558",
  "creator": {
    "id": 2712150,
    "name": "scigola",
    "first_name": "Andrea",
    "last_name": "Baratella",
    "url": "https://api.thingiverse.com/users/scigola",
    "public_url": "https://www.thingiverse.com/scigola",
    "thumbnail": "https://cdn.thingiverse.com/renders/ec/04/68/f3/52/5b4c4a2362ec274db2e6f54cdf1ed02a_thumb_medium.jpg",
    "accepts_tips": false
  },
  "added": "2019-10-15T13:12:43+00:00",
  "modified": "2019-10-15T13:12:43+00:00",
  "is_published": true,
  "is_wip": false,
  "is_featured": false,
  "like_count": 0,
  "is_liked": false,
  "collect_count": 1,
  "is_collected": false,
  "is_watched": false,
  "default_image": {
    "id": 11335348,
    "url": "https://cdn.thingiverse.com/assets/aa/30/22/95/2f/Guida_con_fermaguaina_removibile_01.jpg",
    "name": "Guida_con_fermaguaina_removibile_01.jpg",
    "sizes": [
      {
        "type": "thumb",
        "size": "large",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_thumb_large.jpg"
      },
      {
        "type": "thumb",
        "size": "medium",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_thumb_medium.jpg"
      },
      {
        "type": "thumb",
        "size": "small",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_thumb_small.jpg"
      },
      {
        "type": "thumb",
        "size": "tiny",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_thumb_tiny.jpg"
      },
      {
        "type": "preview",
        "size": "featured",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_featured.jpg"
      },
      {
        "type": "preview",
        "size": "card",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_card.jpg"
      },
      {
        "type": "preview",
        "size": "large",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_large.jpg"
      },
      {
        "type": "preview",
        "size": "medium",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_medium.jpg"
      },
      {
        "type": "preview",
        "size": "small",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_small.jpg"
      },
      {
        "type": "preview",
        "size": "birdwing",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_birdwing.jpg"
      },
      {
        "type": "preview",
        "size": "tiny",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_tiny.jpg"
      },
      {
        "type": "preview",
        "size": "tinycard",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_preview_tinycard.jpg"
      },
      {
        "type": "display",
        "size": "large",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_display_large.jpg"
      },
      {
        "type": "display",
        "size": "medium",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_display_medium.jpg"
      },
      {
        "type": "display",
        "size": "small",
        "url": "https://cdn.thingiverse.com/renders/10/64/d6/81/dd/41ae1bdb59f5a16ec9329a2a7cf65942_display_small.jpg"
      }
    ],
    "added": "2019-08-09T11:41:53+00:00"
  },
  "description": "guidafilo per Alfawise U30 con 4 rulli con possibilità di direzionare il filamento in varie direzioni sù giù, destra e sinistra estraendo e ruotando le testa con i rulli.\r\n\r\nPer i perni dei rulli ho utilizzato dei semplici stuzzicadenti molto facili da tagliare, ma si possono utilizzare altri materiali (i rulli vanno forati in base al diametro dei perni utilizzati).\r\n\r\nPer i distanziali ho utilizzato ranelle M3.\r\n\r\nLa base non necessita di viti viene tenuta da una clip collegata ai rulli del asse Z\r\n\r\nCaffè - https://www.paypal.me/laprimaidea",
  "instructions": "",
  "description_html": "<p>guidafilo per Alfawise U30 con 4 rulli con possibilità di direzionare il filamento in varie direzioni sù giù, destra e sinistra estraendo e ruotando le testa con i rulli.</p>\n<p>Per i perni dei rulli ho utilizzato dei semplici stuzzicadenti molto facili da tagliare, ma si possono utilizzare altri materiali (i rulli vanno forati in base al diametro dei perni utilizzati).</p>\n<p>Per i distanziali ho utilizzato ranelle M3.</p>\n<p>La base non necessita di viti viene tenuta da una clip collegata ai rulli del asse Z</p>\n<p>Caffè - <a rel=\"nofollow\" href=\"https://www.paypal.me/laprimaidea\">https://www.paypal.me/laprimaidea</a></p>",
  "instructions_html": "",
  "details": "<h1 class=\"thing-component-header summary summary\">Summary</h1>\n<div><p>guidafilo per Alfawise U30 con 4 rulli con possibilit&agrave; di direzionare il filamento in varie direzioni s&ugrave; gi&ugrave;, destra e sinistra estraendo e ruotando le testa con i rulli.</p>\n<p>Per i perni dei rulli ho utilizzato dei semplici stuzzicadenti molto facili da tagliare, ma si possono utilizzare altri materiali (i rulli vanno forati in base al diametro dei perni utilizzati).</p>\n<p>Per i distanziali ho utilizzato ranelle M3.</p>\n<p>La base non necessita di viti viene tenuta da una clip collegata ai rulli del asse Z</p>\n<p>Caff&egrave; - <a rel=\"nofollow\" href=\"https://www.paypal.me/laprimaidea\">https://www.paypal.me/laprimaidea</a></p></div>\n",
  "details_parts": [
    {
      "type": "summary",
      "name": "Summary",
      "required": "required",
      "data": [
        {
          "content": "guidafilo per Alfawise U30 con 4 rulli con possibilità di direzionare il filamento in varie direzioni sù giù, destra e sinistra estraendo e ruotando le testa con i rulli.\r\n\r\nPer i perni dei rulli ho utilizzato dei semplici stuzzicadenti molto facili da tagliare, ma si possono utilizzare altri materiali (i rulli vanno forati in base al diametro dei perni utilizzati).\r\n\r\nPer i distanziali ho utilizzato ranelle M3.\r\n\r\nLa base non necessita di viti viene tenuta da una clip collegata ai rulli del asse Z\r\n\r\nCaffè - https://www.paypal.me/laprimaidea"
        }
      ]
    },
    {
      "type": "settings",
      "name": "Print Settings"
    },
    {
      "type": "tips",
      "name": "Post-Printing"
    },
    {
      "type": "design",
      "name": "How I Designed This"
    },
    {
      "type": "custom",
      "name": "Custom Section"
    }
  ],
  "edu_details": "",
  "edu_details_parts": [
    {
      "type": "grades",
      "name": "Grade",
      "required": "recommended",
      "save_as_component": false,
      "template": "taglist_select",
      "fieldname": "grades",
      "default": "Choose a range, help teachers see if this is a fit for their class",
      "opts": {
        "15": "Kindergarten",
        "16": "1st Grade",
        "17": "2nd Grade",
        "18": "3rd Grade",
        "19": "4th Grade",
        "20": "5th Grade",
        "21": "6th Grade",
        "22": "7th Grade",
        "23": "8th Grade",
        "24": "9th Grade",
        "25": "10th Grade",
        "26": "11th Grade",
        "27": "12th Grade",
        "28": "Higher Education"
      }
    },
    {
      "type": "subjects",
      "name": "Subject",
      "required": "recommended",
      "save_as_component": false,
      "template": "taglist_select",
      "fieldname": "subjects",
      "default": "Choose a Subject, Make your project more findable",
      "opts": {
        "11": "Science",
        "12": "Math",
        "13": "Engineering",
        "14": "History",
        "15": "Geography",
        "16": "Art",
        "17": "Languages",
        "18": "Music",
        "19": "Technology",
        "20": "Special Ed"
      }
    },
    {
      "type": "standards",
      "name": "Standards",
      "required": "recommended",
      "save_as_component": false,
      "template": "taglist_select",
      "fieldname": "standards",
      "default": "Choose a Requirement this lesson meets",
      "opts": {
        "3": "NGSS",
        "4": "CCSS"
      }
    },
    {
      "type": "overview",
      "name": "Overview and Background",
      "required": "required"
    },
    {
      "type": "plan",
      "name": "Lesson Plan and Activity",
      "required": "required"
    },
    {
      "type": "materials",
      "name": "Materials Needed",
      "required": "recommended"
    },
    {
      "type": "skills",
      "name": "Skills Learned",
      "label": "Enter each skill and press enter to add it as a tagged skill",
      "required": false,
      "template": "taglist",
      "fieldname": "skills",
      "default": "Choose Skills",
      "opts": []
    },
    {
      "type": "duration",
      "name": "Duration of Lesson",
      "template": "textfield"
    },
    {
      "type": "prep",
      "name": "Preparation"
    },
    {
      "type": "assets",
      "name": "Handouts and Assets",
      "save_as_component": false,
      "label": "Upload any files, docs, etc. They will be found under the Files tab on the Thing Page.",
      "template": "upload"
    },
    {
      "type": "assessment",
      "name": "Rubric and Assessment"
    },
    {
      "type": "references",
      "name": "References"
    }
  ],
  "license": "Creative Commons - Public Domain Dedication",
  "files_url": "https://api.thingiverse.com/things/3730558/files",
  "images_url": "https://api.thingiverse.com/things/3730558/images",
  "likes_url": "https://api.thingiverse.com/things/3730558/likes",
  "ancestors_url": "https://api.thingiverse.com/things/3730558/ancestors",
  "derivatives_url": "https://api.thingiverse.com/things/3730558/derivatives",
  "tags_url": "https://api.thingiverse.com/things/3730558/tags",
  "categories_url": "https://api.thingiverse.com/things/3730558/categories",
  "file_count": 5,
  "layout_count": 0,
  "layouts_url": "https://api.thingiverse.com/layouts/3730558",
  "is_private": false,
  "is_purchased": false,
  "in_library": false,
  "print_history_count": 0,
  "app_id": null,
  "download_count": 27,
  "view_count": 104,
  "education": {
    "grades": [],
    "subjects": []
  }
}
```

From the information returned by this request, we extract the following DB fields in the following ways:

```text
        DB Column        |    Comes From
-------------------------|-------------------------------
 foreign_landing_url     | $public_url
 license                 | Derived from $license (we throw out all but CC0)
 license_version         | Generated based on $license (always 1.0)
 creator                 | $creator.first_name + $creator_last_name or $creator.name (first non-empty in that order is taken)
 creator_url             | $creator.public_url
 title                   | $name
 meta_data               | See below
```

The `meta_data` field contains a json. Because the json contains information gathered from multiple requests, we will discuss its content [below](## `meta_data` field).

### REQUEST: `https://api.thingiverse.com/things/3730558/tags?access_token=REDACTED`

This request returns a json of the following form:

```json
[
  {
    "name": "Alfawise_U30",
    "url": "https://api.thingiverse.com/tags/alfawise_u30",
    "count": 207
  },
  {
    "name": "filament",
    "url": "https://api.thingiverse.com/tags/filament",
    "count": 5617
  },
  {
    "name": "filamento",
    "url": "https://api.thingiverse.com/tags/filamento",
    "count": 76
  },
  {
    "name": "guida",
    "url": "https://api.thingiverse.com/tags/guida",
    "count": 5
  },
  {
    "name": "guide",
    "url": "https://api.thingiverse.com/tags/guide",
    "count": 1198
  },
  {
    "name": "rollers",
    "url": "https://api.thingiverse.com/tags/rollers",
    "count": 23
  },
  {
    "name": "rulli",
    "url": "https://api.thingiverse.com/tags/rulli",
    "count": 2
  },
  {
    "name": "rulli",
    "url": "https://api.thingiverse.com/tags/rulli",
    "count": 1
  }
]
```

From the information returned by this request, we construct the `tags` field in the DB, which is a json of the form:

```json
[
  {
    "name": $name{1},
    "provider": "thingiverse"
  },
  {
    "name": $name{2},
    "provider": "thingiverse"
  }
]
```

Here, `$name{1}` and `$name{2}` represent the name fields from two members of the array in the response. There will be as many tag objects in the resulting field as there are in the response itself.

### REQUEST: `https://api.thingiverse.com/things/3730558/files?access_token=REDACTED`

This request returns a json of the following form:

```json
[
  {
    "id": 6867550,
    "name": "Clip_di_tenuta.stl",
    "size": 11084,
    "url": "https://api.thingiverse.com/files/6867550",
    "public_url": "https://www.thingiverse.com/download:6867550",
    "download_url": "https://api.thingiverse.com/files/6867550/download",
    "threejs_url": "https://cdn.thingiverse.com/threejs_json/fd/70/59/17/f4/Clip_di_tenuta.js",
    "thumbnail": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_thumb_medium.jpg",
    "default_image": {
      "id": 11335389,
      "url": "https://cdn.thingiverse.com/assets/56/db/03/63/24/Clip_di_tenuta.stl",
      "name": "6ee7d80e9da98914f6385ac39f439665.png",
      "sizes": [
        {
          "type": "thumb",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_thumb_large.jpg"
        },
        {
          "type": "thumb",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_thumb_medium.jpg"
        },
        {
          "type": "thumb",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_thumb_small.jpg"
        },
        {
          "type": "thumb",
          "size": "tiny",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_thumb_tiny.jpg"
        },
        {
          "type": "preview",
          "size": "featured",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_featured.jpg"
        },
        {
          "type": "preview",
          "size": "card",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_card.jpg"
        },
        {
          "type": "preview",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_large.jpg"
        },
        {
          "type": "preview",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_medium.jpg"
        },
        {
          "type": "preview",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_small.jpg"
        },
        {
          "type": "preview",
          "size": "birdwing",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_birdwing.jpg"
        },
        {
          "type": "preview",
          "size": "tiny",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_tiny.jpg"
        },
        {
          "type": "preview",
          "size": "tinycard",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_preview_tinycard.jpg"
        },
        {
          "type": "display",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_display_large.jpg"
        },
        {
          "type": "display",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_display_medium.jpg"
        },
        {
          "type": "display",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/22/20/13/77/3c/6ee7d80e9da98914f6385ac39f439665_display_small.jpg"
        }
      ],
      "added": "2019-08-09T11:49:19+00:00"
    },
    "date": "2019-08-09 11:41:43",
    "formatted_size": "10 kb",
    "meta_data": [],
    "download_count": 87
  },
  {
    "id": 6867552,
    "name": "Cont_rulli.stl",
    "size": 50084,
    "url": "https://api.thingiverse.com/files/6867552",
    "public_url": "https://www.thingiverse.com/download:6867552",
    "download_url": "https://api.thingiverse.com/files/6867552/download",
    "threejs_url": "https://cdn.thingiverse.com/threejs_json/8f/e6/30/d0/7c/Cont_rulli.js",
    "thumbnail": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_thumb_medium.jpg",
    "default_image": {
      "id": 11335393,
      "url": "https://cdn.thingiverse.com/assets/ee/f0/b3/6d/81/Cont_rulli.stl",
      "name": "a018629be9548116490b230913f6dd39.png",
      "sizes": [
        {
          "type": "thumb",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_thumb_large.jpg"
        },
        {
          "type": "thumb",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_thumb_medium.jpg"
        },
        {
          "type": "thumb",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_thumb_small.jpg"
        },
        {
          "type": "thumb",
          "size": "tiny",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_thumb_tiny.jpg"
        },
        {
          "type": "preview",
          "size": "featured",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_featured.jpg"
        },
        {
          "type": "preview",
          "size": "card",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_card.jpg"
        },
        {
          "type": "preview",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_large.jpg"
        },
        {
          "type": "preview",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_medium.jpg"
        },
        {
          "type": "preview",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_small.jpg"
        },
        {
          "type": "preview",
          "size": "birdwing",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_birdwing.jpg"
        },
        {
          "type": "preview",
          "size": "tiny",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_tiny.jpg"
        },
        {
          "type": "preview",
          "size": "tinycard",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_preview_tinycard.jpg"
        },
        {
          "type": "display",
          "size": "large",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_display_large.jpg"
        },
        {
          "type": "display",
          "size": "medium",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_display_medium.jpg"
        },
        {
          "type": "display",
          "size": "small",
          "url": "https://cdn.thingiverse.com/renders/9d/c3/f1/f5/2d/a018629be9548116490b230913f6dd39_display_small.jpg"
        }
      ],
      "added": "2019-08-09T11:49:46+00:00"
    },
    "date": "2019-08-09 11:41:47",
    "formatted_size": "48 kb",
    "meta_data": [],
    "download_count": 87
  },
  {
    "id": 6867554,
    "name": "Guidafilo4_rulli_removibile.FCStd",
    "size": 154826,
    "url": "https://api.thingiverse.com/files/6867554",
    "public_url": "https://www.thingiverse.com/download:6867554",
    "download_url": "https://api.thingiverse.com/files/6867554/download",
    "threejs_url": "",
    "thumbnail": "https://cdn.thingiverse.com/site/img/default/Gears_thumb_medium.jpg",
    "default_image": null,
    "date": "2019-08-09 11:42:06",
    "formatted_size": "151 kb",
    "meta_data": [],
    "download_count": 85
  }
]
```

We loop through the returned array, and for each image with a non-null `$default_image`, we fill the following fields in the DB:

```text
        DB Column        |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | $default_image.id
 url                     | $default_image.sizes[i].url (see note below)
 thumbnail               | $default_image.sizes[i].url (see note below)
 meta_data               | See below
```

For the `url` and `thumbnail` fields, we only consider images of type `$display`, and we prefer `$large` for `url`, and `$medium` for `thumbnail`. Recall that we will discuss the `meta_data` field [below](## `meta_data` field).

## `meta_data` field

The `meta_data` field is a json with the following form:

```
{
  "3d_model": $r3.default_image.url
  "description": $r1.description
}
```

Here, `$r1` represents the root json returned by the root request for the thing's data, and $`r3` is the json returned by the request to the /files endpoint.

Below is a table collecting the above information about the mapping from metadata returned by the Thingiverse API to columns in the image table in PostgreSQL. Fields from the above json are preceded by '$' to mark them.
