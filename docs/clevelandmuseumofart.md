<!-- TITLE: Cleveland Museum of Art -->
<!-- SUBTITLE: Information about the Cleveland Museum of Art provider -->

# Cleveland Museum API

We call the following endpoint from the Cleveland Museum of Art:

`http://openaccess-api.clevelandart.org/api/artworks/?cc0=1&limit=X&skip=Y`

Here, `X` and `Y` are replaced with offset information (e.g., we request only 1000 pieces at a time, and move the offset by 1000 for each request).  Such a request returns a rather large json of the following form:
```text
{
  "info": {
    "total": 34911,
    "parameters": {
      "cc0": "1",
      "limit": "2",
      "skip": "0"
    }
  },
  "data": [
    {
      "id": 93014,
      "accession_number": "1335.1917",
      "share_license_status": "CC0",
      "tombstone": "View of Schroon Mountain, Essex County, New York, After a Storm, 1838. Thomas Cole (American, 1801-1848). Oil on canvas; framed: 132.5 x 193.5 x 13 cm (52 3/16 x 76 3/16 x 5 1/8 in.); unframed: 99.8 x 160.6 cm (39 5/16 x 63 1/4 in.). The Cleveland Museum of Art, Hinman B. Hurlbut Collection 1335.1917",
      "current_location": "206 American Landscape",
      "title": "View of Schroon Mountain, Essex County, New York, After a Storm",
      "title_in_original_language": null,
      "series": null,
      "series_in_original_language": null,
      "creation_date": "1838",
      "creation_date_earliest": 1838,
      "creation_date_latest": 1838,
      "creators": [
        {
          "description": "Thomas Cole (American, 1801-1848)",
          "extent": null,
          "qualifier": null,
          "role": "artist",
          "biography": null,
          "name_in_original_language": null,
          "birth_year": "1801",
          "death_year": "1848"
        }
      ],
      "culture": [
        "America, 19th century"
      ],
      "technique": "oil on canvas",
      "support_materials": [],
      "department": "American Painting and Sculpture",
      "collection": "American - Painting",
      "type": "Painting",
      "measurements": "Framed: 132.5 x 193.5 x 13 cm (52 3/16 x 76 3/16 x 5 1/8 in.); Unframed: 99.8 x 160.6 cm (39 5/16 x 63 1/4 in.)",
      "dimensions": {
        "framed": {
          "height": 1.325,
          "width": 1.935,
          "depth": 0.13
        },
        "unframed": {
          "height": 0.998,
          "width": 1.606
        }
      },
      "state_of_the_work": null,
      "edition_of_the_work": null,
      "creditline": "Hinman B. Hurlbut Collection",
      "copyright": null,
      "inscriptions": [
        {
          "inscription": "signed lower left:  T. Cole / Catskill 1838.",
          "inscription_translation": null,
          "inscription_remark": null
        }
      ],
      "exhibitions": {
        "current": [
          {
            "title": "A Century of American Landscape Painting 1800-1900",
            "description": "<i>A Century of American Landscape Painting 1800-1900</i>. Whitney Museum of American Art, New York, NY (organizer) (co-organizer) (January 19-February 25, 1938).",
            "opening_date": "1938-01-19T05:00:00"
          },
          ...,
          {
            "title": "Landscape Into History",
            "description": "<i>Landscape Into History</i>. National Museum of American Art, Washington, DC (organizer) (co-organizer) (March 18-August 7, 1994); Wadsworth Atheneum Museum of Art, Hartford, CT (September 11-December 4, 1994); The Brooklyn Museum, Brooklyn, NY (January 8-March 25, 1995).",
            "opening_date": "1994-03-18T05:00:00"
          }
        ],
        "legacy": [
          "New York, National Academy of Design, Thirteenth Annual Exhibition of the National Academy of Design (23 April 1838-?).<br>New York, Stuyvesant Institute, Dunlap Benefit Exhibition (19 November-December 1838), cat. no. 38.<br>New York, Apollo Gallery, January Exhibition of the Apollo Association for the Promotion of the Fine Arts in the United States (1839), no. 263.<br>New York, Gallery of the American Art-Union, Exhibition of the Paintings of the Late Thomas Cole, At the Gallery of the American Art-Union (27 March 1848-?), cat. no.75<br>Baltimore, The Picture Gallery, Maryland Historical Society, Second Annual Exhibition (1849), cat. no. 199 as Schroon Mountain, lent by J.S. Chapman.<br>Cleveland, The Cleveland Museum of Art, The Inaugural Exhibition (6 June-20 September 1916), cat. no.6 as Landscape, Lent by the Holland Galleries, p. 125.<br>New York, Whitney Museum of American Art, A Century of American Landscape Painting 1800-1900 (19 January-25 February 1938), cat. no. 20, listed p. 26 as The Catskill Mountains, 1833, illus.<br><br>Baltimore, The Baltimore Museum of Art, A Souvenir of Romanticism in America; or An Elegant Exposition of Taste and Fashion from 1812-to 1865 (10 May-10 June 1940), listed p. 23 as The Catskill Mountains.<br>Pittsburgh, Carnegie Institute, Survey of American Painting, (24 October-15 December 1940), cat. no. 107 as The Catskill Mountains.<br>Albany, N.Y., The Albany Institute of History and Art, The Works of Thomas Cole, 1801-1848 (1 November-15 December 1941), cat. not numbered, listed as The Catskill Mountains.<br>Chicago, The Art Institute of Chicago, The Hudson River School and the Early American Landscape Tradition (15 February-25 March 1945); traveled to New York, Whitney Museum of American Art (17 April-18 May 1945), cat. no. 48, listed p. 117 as The Catskill Mountains, ca. 1833; illus. p. 61, fig. 48, discussed p. 63.<br>Hartford, Wadsworth Athenaeum, Thomas Cole 1801-1848 One Hundred Years Later: A Loan Exhibition (12 November 1948-2 January 1949); traveled to New York, Whitney Museum of American Art (8 January-30 January 1949), cat. no. 22 as The Catskill Mountains, listed pp. 24-25.<br>Cleveland, The Cleveland Museum of Art, The Hudson River School (23 January-29 February 1962).<br>Peoria, Lakeview Center for the Arts and Sciences, 200 Years of American Painting (27 March-28 April1965).<br>Chapel Hill, NC, William Hayes Ackland Memorial Art Center, Arts of the Young Republic: The Age of William Dunlap (2 November-1 December 1968), cat. no. 106, illus., discussed p. 50.<br>Rochester, NY, Memorial Art Gallery of the University of Rochester, Thomas Cole (14 February-23 March 1969); traveled to Utica, NY, Munson-Williams-Proctor, Institute (7 April-4 May 1969); Albany, Albany Institute of History and Art (9 May-20 June 1969);  New York, Whitney Museum of American Art (30 June-1 September 1969); cat. no. 35, illus. p. 53, discussed p. 16, entry on p. 32.<br>Buffalo, Albright-Knox Art Gallery, Heritage and Horizon: American Painting 1776-1976 (6 March-11 April 1976); traveled to Detroit, The Detroit Institute of Arts (5 May-13 June 1976); Toledo, The Toledo Museum of Art (4 July-15 August 1976); Cleveland, The Cleveland Museum of Art (8 September-10 October 1976); cat. no. 8, illus.; pages not numbered.<br>Cleveland, The Cleveland Museum of Art, Visions of Landscape: East and West (17 February-21 March 1982). <br>Boston, Museum of Fine Arts, A New World: Masterpieces of American Painting 1760-1910 (7 September-13 November 1983); traveled to Washington, DC, The Corcoran Gallery of Art (7 December 1983-12 February 1984), cat. no. 30, illus. p. 76, listed p. 350, entry p. 230-231.<br>New York, The Metropolitan Museum of Art, American Paradise: The World of the Hudson River School (4 October 1987-3 January 1988), cat. not numbered; illus. p. 134, entry pp. 134-136.<br>Columbus, Columbus Museum of Art, A Nation's Legacy: 150 Years of American Art from Ohio Collections (19 January-15 March 1992), cat. no. 5, illus. p. 30 (color), 174 (black and white), discussed p. 22; did not travel to Japan.<br>Washington, D.C., National Museum of American Art, Thomas Cole, Landscape Into History (18 March-7 August 1994); traveled to Hartford, Wadsworth Atheneum (11 September-4 December 1994); Brooklyn, The Brooklyn Museum (8 January-25 March 1995), cat. not numbered, listed p. 171, illus. p. 69, fig. no. 84.<br>T.N. Grabenhorst, \"A River Runs Through It: Master Artists of the Hudson,\" The Compass: The Magazine of the Sea (2004), no. 2, pp. 30-35?, illus. p. 34"
        ]
      },
      "provenance": [
        {
          "description": "Dr. George Ackerly [d. 1842], New York, NY, to his daughter, Emma Ackerly1",
          "citations": [],
          "footnotes": [
            "1Ackerly was Cole's brother-in-law."
          ],
          "date": "1838"
        },
        ...,
        {
          "description": "The Cleveland Museum of Art, Cleveland, Ohio",
          "citations": [],
          "footnotes": [],
          "date": "1917-"
        }
      ],
      "find_spot": null,
      "related_works": [],
      "fun_fact": null,
      "digital_description": null,
      "wall_description": "Championing the unspoiled American wilderness, Cole declared, \"We are still in Eden,\" in his Essay on American Scenery, published two years before he painted this view of the Adirondacks. Cole sketched the scene in early summer, but when he created the painting in his Catskill studio, he rendered it in a dramatic blaze of fall colors. Such a choice likely had nationalistic overtones, for Cole once proclaimed that autumn was \"one season where the American forest surpasses all the world in gorgeousness.\" Cole further underscored the New World character of his scene by depicting Native Americans in the right foreground foliage. At this time, the presence of Native Americans in the Adirondacks-as in most areas east of the Mississippi River-was rapidly diminishing due to forced resettlement and repression.",
      "citations": [
        {
          "citation": "Hoffman, Charles Fenno. <em>New-York Mirror, </em>June 1838.",
          "page_number": "Mentioned: p. 367, 390",
          "url": null
        },
        ...,
        {
          "citation": "Prown, Jules David. <em>American Painting: From Its Beginnings to the Armory Show, vol. 1. </em>Geneva: Skira, distributed by World Publishing Company, 1969.",
          "page_number": "Mentioned: p. 64-75; Reproduced: p. 67",
          "url": null
        }
      ],
      "catalogue_raisonne": null,
      "url": "https://clevelandart.org/art/1335.1917",
      "images": {
        "web": {
          "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_web.jpg",
          "filename": "1335.1917_web.jpg",
          "filesize": "716717",
          "width": "1263",
          "height": "775"
        },
        "print": {
          "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_print.jpg",
          "filename": "1335.1917_print.jpg",
          "filesize": "5582485",
          "width": "3400",
          "height": "2086"
        },
        "full": {
          "url": "https://openaccess-cdn.clevelandart.org/1335.1917/1335.1917_full.tif",
          "filename": "1335.1917_full.tif",
          "filesize": "72628688",
          "width": "6280",
          "height": "3853"
        }
      },
      "updated_at": "2019-11-18 09:03:30.462000"
    },
    {
      "id": 94979,
      "accession_number": "1915.534",
      "share_license_status": "CC0",
      "tombstone": "Nathaniel Hurd, c. 1765. John Singleton Copley (American, 1738-1815). Oil on canvas; framed: 90.5 x 78 x 6.5 cm (35 5/8 x 30 11/16 x 2 9/16 in.); unframed: 76.2 x 64.8 cm (30 x 25 1/2 in.). The Cleveland Museum of Art, Gift of the John Huntington Art and Polytechnic Trust 1915.534",
      "current_location": "204 Colonial American",
      "title": "Nathaniel Hurd",
      "title_in_original_language": null,
      "series": null,
      "series_in_original_language": null,
      "creation_date": "c. 1765",
      "creation_date_earliest": 1760,
      "creation_date_latest": 1770,
      "creators": [
        {
          "description": "John Singleton Copley (American, 1738-1815)",
          "extent": null,
          "qualifier": null,
          "role": "artist",
          "biography": null,
          "name_in_original_language": null,
          "birth_year": "1738",
          "death_year": "1815"
        }
      ],
      "culture": [
        "America, 18th century"
      ],
      "technique": "oil on canvas",
      "support_materials": [],
      "department": "American Painting and Sculpture",
      "collection": "American - Painting",
      "type": "Painting",
      "measurements": "Framed: 90.5 x 78 x 6.5 cm (35 5/8 x 30 11/16 x 2 9/16 in.); Unframed: 76.2 x 64.8 cm (30 x 25 1/2 in.)",
      "dimensions": {
        "framed": {
          "height": 0.905,
          "width": 0.78,
          "depth": 0.065
        },
        "unframed": {
          "height": 0.762,
          "width": 0.648
        }
      },
      "state_of_the_work": null,
      "edition_of_the_work": null,
      "creditline": "Gift of the John Huntington Art and Polytechnic Trust",
      "copyright": null,
      "inscriptions": [],
      "exhibitions": {
        "current": [
          {
            "title": "Inaugural Exhibition",
            "description": "<i>Inaugural Exhibition</i>. The Cleveland Museum of Art, Cleveland, OH (organizer) (co-organizer) (June 6-September 20, 1916).",
            "opening_date": "1916-06-06T05:00:00"
          },
          ...,
          {
            "title": "Nathaniel Hurd",
            "description": "<i>Nathaniel Hurd</i>. Memorial Art Gallery of the University of Rochester, NY (November 22, 1999-April 10, 2000).",
            "opening_date": "1999-11-22T00:00:00"
          }
        ],
        "legacy": [
          "Cleveland, Cleveland Museum of Art, The Inaugural Exhibition (6 June-20 September, 1916); cat. p. 255.<br>Boston, Museum of Fine Arts, Boston, One Hundred Colonial Portraits (19 June-21 September 1930), cat. no. 50.<br>Cleveland, Cleveland Museum of Art, Catalogue of the Twentieth Anniversary Exhibition of the Cleveland Museum of Art: The Official Art Exhibit of the Great Lakes Exposition (26 June-4 October, 1936), illus. plate II, cat. no. 23, pp. 21-22.<br>New York, Metropolitan Museum of Art, An Exhibition of Paintings by John Singleton Copley: In Commemoration of the Two-Hundredth Anniversary of His Birth (22 December, 1936-14 February, 1937), illus. 16. <br>Baltimore, Baltimore Museum of Art, Two Hundred Years of American Painting, (15 January-28 February, 1938), no. 2.<br>New Haven, Yale University Gallery of Fine Arts, Masterpieces of New England Silver 1650-1800, (18 June-10 September, 1939), ill. no. 224, p. 94.<br>Flint, Mich., Flint Institute of Arts, Art Marches On: The Opening and Dedicating Exhibition of the New Flint Institute of Arts (14 November-31 December, 1941), illus no. 53, p. 30.<br>Oberlin, Ohio, The Dudley P. Allen Memorial Art Museum, The Arts in the Americas in the Eighteenth Century (1946), cat. no. 1 (see Bulletin of the Allen Memorial Art Museum, Oberlin College, vol. III, no. 3 (May, 1946).<br>Dallas, The Dallas Museum of Fine Arts, Survey of American Painting from 1700 to the Present (5 October - 3 November 1946); cat. 200 Years of American Painting.<br>Denver, The Denver Art Museum, American Heritage: An Exhibitions of Paintings and Crafts 1770-1790 (7 March-11 April 1948), ill. p. 9.<br>Denver, The Denver Art Museum, Portraiture Through the Ages (9 January - 15 February 1950).<br>Milwaukee, Milwaukee Art Institute, Silver and American Tradition (13 February - 19 March 1953).<br>Houston, Museum of Fine Arts, Houston, George Washington's World (15 January - 14 February 1954), cat. no. 5. <br>Boston, Museum of Fine Arts, Boston, Colonial Silversmiths, Masters and Apprentices (13 November - 30 December 1956).<br>Jewett Art Center, Wellesley College, Massachusetts, Four Boston Masters (10 April-11 May, 1959), cat. no. 8, repr. p. 25; traveled to Boston, Museum of Fine Arts (19 May - 26 June 1959).<br>Cleveland, The Cleveland Museum of Art, Style, Truth and the Portrait (1 October -10 November, 1963), ill. cat. no. 29.<br>New York, The Gallery at The Better Living Center, New York World's Fair, Four Centuries of American Masterpieces (22 May-18 October 1964), p. 18, illus. p. 18; (arranged by the Skowhegan School of Painting and Sculpture).<br>Washington, DC, National Gallery of Art, John Singleton Copley, 1738-1815 (18 September - 31 October 1965), pp. 45-9, illus. p. 47; traveled to New York, Metropolitan Museum of Art (20 November 1965 - 2 January 1966); traveled to Boston, Museum of Fine Arts (22 January - 6 February 1966).<br>Fort Worth, Amon Carter Museum of Western Art, The Face of Liberty: Founders of the United States  (23 December 1975 - 8 February 1976), illus. colorplate 16.<br>Cleveland, The Cleveland Museum of Art, Silver in American Life (24 June - 16 August 1981); exhibited in gallery but not in catalogue.<br>Boston, Museum of Fine Arts, John Singleton Copley in America (7 June - 27 August 1995), traveled to New York, Metropolitan Museum of Art (26 September 1995 - 7 January 1996), traveled to Houston, Museum of Fine Arts (4 February - 28 April 1996), did not travel to Milwaukee, Milwaukee Art Museum; cat. no. 21, p. 57, 93, 119, 208-11, 248, 300, 312.<br>Rochester, New York, Memorial Art Gallery of the University of Rochester, ABOUT FACE: Copley's Portrait of Nathaniel Hurd, Colonial Silversmith and Engraver, (1 November 1999-1 March 2000), see Porticus journal.<br>Allen Memorial Art Museum, Oberlin, OH (August 29 - December 17, 2006): \"CMA @ Oberlin - American Portraits\""
        ]
      },
      "provenance": [
        {
          "description": "Benjamin Hurd [1739-1781], Halifax, Nova Scotia, by descent to his son, John Hurd",
          "citations": [
            {
              "citation": "Walter Wesselhoeft, letter “To Whom It May Concern,” Septenber 1915, in CMA curatorial file.",
              "page_number": null,
              "url": null
            },
            {
              "citation": "W.H.D., “The Fine Arts: Fine Portrait by Copley,” <em>The Boston Transcript</em> (Oct. 1915).",
              "page_number": null,
              "url": null
            }
          ],
          "footnotes": [],
          "date": "-1781"
        },
        ...,
        {
          "description": "The Cleveland Museum of Art, Cleveland, Ohio",
          "citations": [],
          "footnotes": [],
          "date": "1915-"
        }
      ],
      "find_spot": null,
      "related_works": [],
      "fun_fact": "Had he been painted standing, you would be able to see Nathaniel Hurd's long silk robe, or banyan. He would not leave the house in this, or perform the work that gave him success as a silversmith.",
      "digital_description": null,
      "wall_description": "Hurd was a prominent silversmith and engraver in Boston, and the warm gaze and unforced smile in his portrait by Copley suggest the friendship between the two artists. Hurd's open-collared shirt, as well as the rakishly tilted turban that covers his shaved head in place of a ceremonial powdered wig, create an air of informality that is unusual for a portrait of this time.",
      "citations": [
        {
          "citation": "Perkins, Augustus Thorndike. <em>A Sketch of the Life and a List of Some of the Works of John Singleton Copley</em>. Boston: Priv. Print, 1873.",
          "page_number": "Mentioned: p. 17, 75-6",
          "url": null
        },
        ...,
        {
          "citation": "Ripley, Elizabeth. <em>Copley; A Biography</em>. Philadelphia: J. B. Lippincott Company, 1967.",
          "page_number": "Mentioned: p. 24; Reproduced: p. 25",
          "url": null
        }
      ],
      "catalogue_raisonne": null,
      "url": "https://clevelandart.org/art/1915.534",
      "images": {
        "web": {
          "url": "https://openaccess-cdn.clevelandart.org/1915.534/1915.534_web.jpg",
          "filename": "1915.534_web.jpg",
          "filesize": "402404",
          "width": "748",
          "height": "893"
        },
        "print": {
          "url": "https://openaccess-cdn.clevelandart.org/1915.534/1915.534_print.jpg",
          "filename": "1915.534_print.jpg",
          "filesize": "5904910",
          "width": "2849",
          "height": "3400"
        },
        "full": {
          "url": "https://openaccess-cdn.clevelandart.org/1915.534/1915.534_full.tif",
          "filename": "1915.534_full.tif",
          "filesize": "76080612",
          "width": "4609",
          "height": "5500"
        }
      },
      "updated_at": "2019-11-18 09:06:02.296000"
    }
  ]
}
```
Note that here, we retrieved the information of only 2 pieces of artwork for brevity, as well as elided some of the returned data.  For the Cleveland Museum's API, the information about each artwork listed is returned in the same json, so one must exercise caution.  Also, we set the license (and consequently version) information in the query string of the request itself.

Below is a table showing the mapping from metadata returned by the API to columns in the `image` table in PostgreSQL.  Fields from the above json are preceded by a `$` to mark them.  Also, we will omit `$data[i]` from the paths, as it is simply the path to a given artwork within the returned json.

```text
         Column          |    Comes From
-------------------------|-------------------------------
 foreign_identifier      | metadata
 foreign_landing_url     | $url
 url                     | $images.web or $images.print or $images.full (preferred in that order)
 width                   | $images.TYPE.width (TYPE is web, print, or full as above)
 height                  | $images.TYPE.height (TYPE is web, print, or full as above)
 license                 | $share_license_status
 license_version         | derived from $share_license_status
 creator                 | $creators[0].description
 title                   | $title
 meta_data               | See Below
```

## metadata field
The metadata field in the DB is a json field with the following information:

```text
{
  "accession_number": $accession_number,
  "technique": $technique,
  "date": $creation_date,
  "credit_line": $creditline
  "medium": $technique,
  "classification": $type,
  "culture": $culture,
  "tombstone": $tombstone
}
```
