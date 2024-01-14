import { deepClone } from "~/utils/clone"
import {
  filtersToQueryData,
  queryToFilterData,
} from "~/utils/search-query-transform"
import { AUDIO, IMAGE } from "~/constants/media"

import { filterData, initFilters } from "~/constants/filters"

describe("searchQueryTransform", () => {
  it("converts initial filters to query data", () => {
    const filters = {
      ...filterData,
    }

    const result = filtersToQueryData(filters)
    expect(result).toEqual({})
  })
  it("converts filter to query data", () => {
    const filters = { ...filterData }
    const result = filtersToQueryData(filters)
    expect(result).toEqual({})
  })
  it("converts all filters to query data", () => {
    const filters = {
      licenses: [
        { code: "cc0", name: "filters.licenses.cc0", checked: true },
        { code: "pdm", name: "filters.licenses.pdm", checked: false },
        { code: "by", name: "filters.licenses.by", checked: false },
        { code: "by-sa", name: "filters.licenses.by-sa", checked: false },
        { code: "by-nc", name: "filters.licenses.by-nc", checked: false },
        { code: "by-nd", name: "filters.licenses.by-nd", checked: false },
        { code: "by-nc-sa", name: "filters.licenses.by-nc-sa", checked: false },
        { code: "by-nc-nd", name: "filters.licenses.by-nc-nd", checked: false },
      ],
      licenseTypes: [
        {
          code: "commercial",
          name: "filters.license-types.commercial",
          checked: true,
        },
        {
          code: "modification",
          name: "filters.license-types.modification",
          checked: false,
        },
      ],
      imageCategories: [
        {
          code: "photograph",
          name: "filters.image-categories.photograph",
          checked: true,
        },
        {
          code: "illustration",
          name: "filters.image-categories.illustration",
          checked: false,
        },
        {
          code: "digitized-artwork",
          name: "filters.image-categories.digitized-artwork",
          checked: false,
        },
      ],
      imageExtensions: [
        { code: "jpg", name: "filters.image-extensions.jpg", checked: true },
        { code: "png", name: "filters.image-extensions.png", checked: false },
        { code: "gif", name: "filters.image-extensions.gif", checked: false },
        { code: "svg", name: "filters.image-extensions.svg", checked: false },
      ],
      aspectRatios: [
        { code: "tall", name: "filters.aspect-ratios.tall", checked: true },
        { code: "wide", name: "filters.aspect-ratios.wide", checked: false },
        {
          code: "square",
          name: "filters.aspect-ratios.square",
          checked: false,
        },
      ],
      sizes: [
        { code: "small", name: "filters.sizes.small", checked: false },
        { code: "medium", name: "filters.sizes.medium", checked: true },
        { code: "large", name: "filters.sizes.large", checked: false },
      ],
      imageProviders: [
        { code: "animaldiversity", checked: true },
        { code: "brooklynmuseum", checked: true },
      ],
    }
    const expectedQueryData = {
      aspect_ratio: "tall",
      category: "photograph",
      extension: "jpg",
      license: "cc0",
      license_type: "commercial",
      size: "medium",
      source: "animaldiversity,brooklynmuseum",
    }
    const result = filtersToQueryData(filters, IMAGE)
    expect(result).toEqual(expectedQueryData) // toEqual checks for value equality
  })
  it("queryToFilterData blank", () => {
    const filters = {
      ...filterData,
    }
    const query = {}

    const result = queryToFilterData({ query, defaultFilters: filters })
    expect(result).toEqual(filters) // toEqual checks for value equality
  })
  it("queryToFilterData all image filters", () => {
    const filters = {
      licenses: [
        { code: "cc0", name: "filters.licenses.cc0", checked: true },
        { code: "pdm", name: "filters.licenses.pdm", checked: false },
        { code: "by", name: "filters.licenses.by", checked: false },
        { code: "by-sa", name: "filters.licenses.by-sa", checked: false },
        { code: "by-nc", name: "filters.licenses.by-nc", checked: false },
        { code: "by-nd", name: "filters.licenses.by-nd", checked: false },
        { code: "by-nc-sa", name: "filters.licenses.by-nc-sa", checked: false },
        { code: "by-nc-nd", name: "filters.licenses.by-nc-nd", checked: false },
      ],
      licenseTypes: [
        {
          code: "commercial",
          name: "filters.license-types.commercial",
          checked: true,
        },
        {
          code: "modification",
          name: "filters.license-types.modification",
          checked: false,
        },
      ],
      imageCategories: [
        {
          code: "photograph",
          name: "filters.image-categories.photograph",
          checked: true,
        },
        {
          code: "illustration",
          name: "filters.image-categories.illustration",
          checked: false,
        },
        {
          code: "digitized_artwork",
          name: "filters.image-categories.digitized-artwork",
          checked: false,
        },
      ],
      lengths: [
        {
          checked: false,
          code: "shortest",
          name: "filters.lengths.shortest",
        },
        {
          checked: false,
          code: "short",
          name: "filters.lengths.short",
        },
        {
          checked: true,
          code: "medium",
          name: "filters.lengths.medium",
        },
        {
          checked: false,
          code: "long",
          name: "filters.lengths.long",
        },
      ],
      imageExtensions: [
        { code: "jpg", name: "filters.image-extensions.jpg", checked: true },
        { code: "png", name: "filters.image-extensions.png", checked: false },
        { code: "gif", name: "filters.image-extensions.gif", checked: false },
        { code: "svg", name: "filters.image-extensions.svg", checked: false },
      ],
      aspectRatios: [
        { code: "tall", name: "filters.aspect-ratios.tall", checked: true },
        { code: "wide", name: "filters.aspect-ratios.wide", checked: false },
        {
          code: "square",
          name: "filters.aspect-ratios.square",
          checked: false,
        },
      ],
      sizes: [
        { code: "small", name: "filters.sizes.small", checked: false },
        { code: "medium", name: "filters.sizes.medium", checked: true },
        { code: "large", name: "filters.sizes.large", checked: false },
      ],
      imageProviders: [
        { code: "animaldiversity", checked: true },
        { code: "brooklynmuseum", checked: true },
      ],
      audioCategories: [
        {
          checked: true,
          code: "music",
          name: "filters.audio-categories.music",
        },
        {
          checked: false,
          code: "soundEffects",
          name: "filters.audio-categories.sound_effects",
        },
        {
          checked: false,
          code: "podcast",
          name: "filters.audio-categories.podcast",
        },
      ],
      audioExtensions: [
        {
          checked: true,
          code: "mp3",
          name: "filters.audio-extensions.mp3",
        },
        {
          checked: false,
          code: "ogg",
          name: "filters.audio-extensions.ogg",
        },
        {
          checked: false,
          code: "flac",
          name: "filters.audio-extensions.flac",
        },
      ],
      audioProviders: [
        {
          checked: true,
          code: "jamendo",
        },
        {
          checked: true,
          code: "wikimedia",
        },
      ],
    }
    const query = {
      q: "cat",
      license: "cc0",
      license_type: "commercial",
      category: "music",
      extension: "mp3",
      length: "medium",
      source: "jamendo",
      includeSensitiveResults: "true",
    }
    const testFilters = deepClone(filters)
    testFilters.audioProviders = [
      { code: "jamendo", checked: true },
      { code: "wikimedia", checked: true },
    ]
    const result = queryToFilterData({
      query,
      searchType: AUDIO,
      defaultFilters: testFilters,
    })
    expect(result).toEqual(filters) // toEqual checks for value equality
  })

  it("queryToFilterData discards all image filters when search type is audio", () => {
    const filters = initFilters()
    filters.audioProviders = [
      { code: "jamendo", checked: false },
      { code: "wikimedia_audio", checked: false },
    ]
    /**
     * `category` and `extension` parameter values will not be used because those
     * codes (`photograph` and `svg`) only exist for the `imageCategories` and `imageExtensions`
     * filter categories.
     * `source` will only use the `wikimedia_audio` and `jamendo` parameters because they
     * exist in `filters.audioProviders` list before. Other values either exist in
     * `filters.imageProviders` list, or do not exist at all, so they are discarded.
     * Valid filter items for categories that exist for all search types
     * (`license`, `license_type`) are set to checked.
     * Invalid filter items for valid categories (`nonexistent` in `license`)
     * are discarded.
     */
    const query = {
      q: "cat",
      license: "cc0,nonexistent",
      license_type: "commercial",
      category: "photograph",
      extension: "svg",
      length: "medium",
      source: "animaldiversity,wikimedia,nonexistent,wikimedia_audio,jamendo",
    }
    const expectedFilters = deepClone(filters)
    const setChecked = (code, filterCategory) => {
      const idx = expectedFilters[filterCategory].findIndex(
        (item) => item.code === code
      )
      expectedFilters[filterCategory][idx].checked = true
    }
    setChecked("cc0", "licenses")
    setChecked("commercial", "licenseTypes")
    setChecked("medium", "lengths")
    setChecked("jamendo", "audioProviders")
    setChecked("wikimedia_audio", "audioProviders")

    const result = queryToFilterData({
      query,
      searchType: AUDIO,
      defaultFilters: filters,
    })
    expect(result).toEqual(expectedFilters) // toEqual checks for value equality
  })
})
