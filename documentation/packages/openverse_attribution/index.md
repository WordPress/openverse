# `openverse-attribution`

`openverse-attribution` is a Python library that provides utilities related to
open licenses, tools, and attribution.

Refer to the in-code documentation for more in-depth information about each
property and function.

## Licenses and tools

This library provides a string enum `License` that enumerates all licenses,
tools and marks supported by Openverse. These include the following.

- Active CC licenses
  - CC BY (`by`)
  - CC BY-SA (`by-sa`)
  - CC BY-NC (`by-nc`)
  - CC BY-ND (`by-nd`)
  - CC BY-NC-SA (`by-nc-sa`)
  - CC BY-NC-ND (`by-nc-nd`)
- Deprecated CC licenses
  - CC Sampling+ (`sampling`)
  - CC NC-Sampling+ (`nc-sampling`)
- CC0 public domain dedication (`cc0`)
- PDM public domain mark (`pdm`)

A `License` object can be created from a valid license slug. This object then
provides access to a number of properties and methods about that particular
license.

```python
from openverse_attribution.license import License

lic = License("by")
lic.url()           # 'https://creativecommons.org/licenses/by/4.0/'
lic.name("2.0")     # 'CC BY 2.0'
lic.is_deprecated   # False
lic.is_pd           # False
lic.is_cc           # True

mark = License("pdm")
mark.url()          # 'https://creativecommons.org/publicdomain/mark/1.0/'
mark.name("2.0")    # 'Public Domain Mark 1.0'
mark.is_deprecated  # False
mark.is_pd          # True
mark.is_cc          # False
```

## Attribution

The library provides a function `get_attribution_text` to generate plain-text
English-language attribution strings for media items.

This function supports media items with partially known information and as such,
takes only one required parameter (`license_slug`) and a number of optional
arguments for title, creator etc. that can be populated, based on the known
information, to generate the most descriptive attribution string possible.

The second sentence with the URL to the deed is optional and can be disabled by
passing `False` to the `license_url` param.

```python
from openverse_attribution.attribution import get_attribution_text

get_attribution_text(
  "cc0",
  title="Wheat Field with Cypresses",
  creator="Vincent van Gogh",
)
# '"Wheat Field with Cypresses" by Vincent van Gogh is marked with CC0 1.0.
#  To view the terms, visit https://creativecommons.org/publicdomain/zero/1.0/.'

get_attribution_text("cc0")
# 'This work is marked with CC0 1.0.
#  To view the terms, visit https://creativecommons.org/publicdomain/zero/1.0/.'

get_attribution_text("by", license_version="2.0", license_url=False)
# 'This work is licensed under CC BY 2.0.'
```
