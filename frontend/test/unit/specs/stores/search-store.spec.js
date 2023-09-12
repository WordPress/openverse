import { nextTick } from "vue"

import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { env } from "~/utils/env"

import { filterData, mediaFilterKeys } from "~/constants/filters"
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  searchPath,
  supportedSearchTypes,
  VIDEO,
} from "~/constants/media"
import { INCLUDE_SENSITIVE_QUERY_PARAM } from "~/constants/content-safety"

import { computeQueryParams, useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

describe("Search Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  describe("state", () => {
    it("sets initial filters to filterData", () => {
      const searchStore = useSearchStore()
      expect(searchStore.filters).toEqual(filterData)
    })
  })
  describe("getters", () => {
    /**
     * Check for some special cases:
     * - `fetch_sensitive` feature flag filter.
     * - several options for single filter.
     * - media specific filters that are unique (durations).
     * - media specific filters that have the same API param (extensions)
     */
    it.each`
      sensitivityFlag | query                                          | searchType   | filterCount
      ${"on"}         | ${{ licenses: ["by"] }}                        | ${IMAGE}     | ${1}
      ${"off"}        | ${{ licenses: ["cc0", "pdm", "by", "by-nc"] }} | ${ALL_MEDIA} | ${4}
      ${"off"}        | ${{ lengths: ["medium"] }}                     | ${AUDIO}     | ${1}
      ${"off"}        | ${{ imageExtensions: ["svg"] }}                | ${IMAGE}     | ${1}
      ${"off"}        | ${{ audioExtensions: ["mp3"] }}                | ${AUDIO}     | ${1}
    `(
      "returns correct filter status for $query and searchType $searchType",
      ({ sensitivityFlag, query, searchType, filterCount }) => {
        const featureFlagStore = useFeatureFlagStore()
        featureFlagStore.toggleFeature("fetch_sensitive", sensitivityFlag)
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        for (let [filterType, values] of Object.entries(query)) {
          values.forEach((val) =>
            searchStore.toggleFilter({ filterType, code: val })
          )
        }

        expect(searchStore.appliedFilterCount).toEqual(filterCount)
        expect(searchStore.isAnyFilterApplied).toBe(filterCount > 0)
      }
    )

    /**
     * If type or query are not provided, uses the current state values.
     * Uses the query as is, if provided. Otherwise, uses the store state
     * as the query, omitting parameters that are not relevant for the search type.
     */
    it.each`
      type         | currentState                                                                                | expected
      ${undefined} | ${{ path: "/search/audio", urlQuery: { q: "cat", license: "by,by-sa", extension: "ogg" } }} | ${{ path: "/search/audio", query: { q: "cat", license: "by,by-sa", extension: "ogg" } }}
      ${IMAGE}     | ${{ path: "/search/audio", urlQuery: { q: "cat", license: "by,by-sa" } }}                   | ${{ path: "/search/image", query: { q: "cat", license: "by,by-sa" } }}
      ${AUDIO}     | ${{ path: "/search/image", urlQuery: { q: "cat", license: "by,by-sa" } }}                   | ${{ path: "/search/audio", query: { q: "cat", license: "by,by-sa" } }}
      ${AUDIO}     | ${{ path: "/search/image", urlQuery: { q: "cat", extension: "svg" } }}                      | ${{ path: "/search/audio", query: { q: "cat" } }}
      ${IMAGE}     | ${{ path: "/search/image", urlQuery: { q: "cat", extension: "svg" } }}                      | ${{ path: "/search/image", query: { q: "cat", extension: "svg" } }}
      ${IMAGE}     | ${{ path: "/search/audio", urlQuery: { q: "cat", duration: "medium" } }}                    | ${{ path: "/search/image", query: { q: "cat" } }}
      ${VIDEO}     | ${{ path: "/search/audio", urlQuery: { q: "cat", extension: "ogg" } }}                      | ${{ path: "/search/video", query: { q: "cat" } }}
    `(
      "getSearchPath returns $expected.path, $expected.query for $type and current state $currentState.path, $currentState.urlQuery",
      ({ type, query, currentState, expected }) => {
        const searchStore = useSearchStore()

        searchStore.setSearchStateFromUrl(currentState)

        searchStore.getSearchPath({ type, query })

        expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith(expected)
      }
    )

    it.each`
      type         | query                          | currentState                                      | expected
      ${undefined} | ${{ unknownParam: "dropped" }} | ${{ path: "/search/image", urlQuery: { q: "" } }} | ${{ path: "/search/image", query: { unknownParam: "dropped" } }}
    `(
      "getSearchPath returns $expected.path, $expected.query for query $query $type and current state $currentState.path, $currentState.urlQuery",
      ({ type, query, currentState, expected }) => {
        const searchStore = useSearchStore()

        searchStore.setSearchStateFromUrl(currentState)

        searchStore.getSearchPath({ type, query })

        expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith(expected)
      }
    )

    /**
     * For non-supported search types, the filters fall back to 'All content' filters.
     * Number of displayed filters is one less than the number of mediaFilterKeys
     * because `includeSensitiveResults` filter is not displayed.
     */
    it.each`
      searchType   | filterTypeCount
      ${IMAGE}     | ${mediaFilterKeys[IMAGE].length}
      ${AUDIO}     | ${mediaFilterKeys[AUDIO].length}
      ${ALL_MEDIA} | ${mediaFilterKeys[ALL_MEDIA].length}
      ${VIDEO}     | ${mediaFilterKeys[VIDEO].length}
    `(
      "mediaFiltersForDisplay returns $filterTypeCount filters for $searchType",
      ({ searchType, filterTypeCount }) => {
        const featureFlagStore = useFeatureFlagStore()
        featureFlagStore.toggleFeature("additional_search_types", "on")

        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        const filtersForDisplay = searchStore.searchFilters

        expect(Object.keys(filtersForDisplay).length).toEqual(filterTypeCount)
      }
    )
    /**
     * Check for some special cases:
     * - `fetch_sensitive` feature flag.
     * - several options for single filter.
     * - media specific filters that are unique (durations).
     * - media specific filters that have the same API param (extensions)
     * - no 'q' parameter in the query.
     * - more than one value for a parameter in the query (q=cat&q=dog).
     */
    it.each`
      sensitivityFlag | query                                            | expectedQueryParams                                                     | searchType
      ${"on"}         | ${{ q: "cat", license: "by" }}                   | ${{ q: "cat", license: "by", [INCLUDE_SENSITIVE_QUERY_PARAM]: "true" }} | ${IMAGE}
      ${"on"}         | ${{ license: "by" }}                             | ${{ q: "", license: "by", [INCLUDE_SENSITIVE_QUERY_PARAM]: "true" }}    | ${IMAGE}
      ${"off"}        | ${{ license: "" }}                               | ${{ q: "" }}                                                            | ${IMAGE}
      ${"off"}        | ${{ q: "cat", license: "pdm,cc0,by,by-nc" }}     | ${{ q: "cat", license: "pdm,cc0,by,by-nc" }}                            | ${ALL_MEDIA}
      ${"off"}        | ${{ q: "cat", length: "medium" }}                | ${{ q: "cat" }}                                                         | ${IMAGE}
      ${"off"}        | ${{ q: "cat", length: "medium" }}                | ${{ q: "cat", length: "medium" }}                                       | ${AUDIO}
      ${"off"}        | ${{ q: "cat", extension: "svg" }}                | ${{ q: "cat", extension: "svg" }}                                       | ${IMAGE}
      ${"off"}        | ${{ q: "cat", extension: "mp3" }}                | ${{ q: "cat", extension: "mp3" }}                                       | ${AUDIO}
      ${"off"}        | ${{ q: "cat", extension: "svg" }}                | ${{ q: "cat" }}                                                         | ${AUDIO}
      ${"off"}        | ${{ q: ["cat", "dog"], license: ["by", "cc0"] }} | ${{ q: "cat", license: "by" }}                                          | ${IMAGE}
    `(
      "returns correct apiSearchQueryParams and filter status for $query and searchType $searchType",
      ({ sensitivityFlag, query, expectedQueryParams, searchType }) => {
        const featureFlagStore = useFeatureFlagStore()
        featureFlagStore.toggleFeature("fetch_sensitive", sensitivityFlag)
        const searchStore = useSearchStore()
        // It should discard the values that are not applicable for the search type:

        searchStore.setSearchStateFromUrl({
          path: searchPath(searchType),
          urlQuery: query,
        })

        expect(searchStore.apiSearchQueryParams).toEqual(expectedQueryParams)
      }
    )
  })

  describe("actions", () => {
    it.each(["foo", ""])(
      "`setSearchTerm correctly updates the searchTerm",
      (searchTerm) => {
        const searchStore = useSearchStore()
        const expectedSearchTerm = searchTerm
        searchStore.setSearchTerm(searchTerm)
        expect(searchStore.searchTerm).toEqual(expectedSearchTerm)
      }
    )
    it.each(supportedSearchTypes)(
      "setSearchType correctly updates the searchType",
      (type) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(type)

        expect(searchStore.searchType).toEqual(type)
      }
    )
    it("throws an error for additional search types if the feature flag is off", () => {
      const searchStore = useSearchStore()
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("additional_search_types", "off")

      expect(() => searchStore.setSearchType(VIDEO)).toThrow(
        "Please enable the 'additional_search_types' flag to use the video"
      )
    })

    it("sets an additional search types if the feature flag is on", () => {
      const searchStore = useSearchStore()
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("additional_search_types", "on")

      searchStore.setSearchType(VIDEO)
      expect(searchStore.searchType).toEqual(VIDEO)
    })

    // TODO: add support for video path
    it.each`
      searchType | path
      ${"all"}   | ${"/search/"}
      ${"image"} | ${"/search/image/"}
      ${"audio"} | ${"/search/audio/"}
      ${"video"} | ${"/search/video"}
    `(
      "`setSearchStateFromUrl` should set searchType '$searchType' from path '$path'",
      ({ searchType, path }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchStateFromUrl({ path: path, urlQuery: {} })

        expect(searchStore.searchType).toEqual(searchType)
      }
    )

    it.each`
      sensitivityFlag | query                                                      | path                | searchType
      ${"off"}        | ${{ license: "cc0,by", q: "cat" }}                         | ${"/search/"}       | ${ALL_MEDIA}
      ${"off"}        | ${{ q: "dog" }}                                            | ${"/search/image/"} | ${IMAGE}
      ${"on"}         | ${{ [INCLUDE_SENSITIVE_QUERY_PARAM]: "true", q: "galah" }} | ${"/search/audio/"} | ${AUDIO}
      ${"off"}        | ${{ length: "medium" }}                                    | ${"/search/image"}  | ${IMAGE}
    `(
      "`setSearchStateFromUrl` should set '$searchType' from query $query and path '$path'",
      ({ sensitivityFlag, query, path, searchType }) => {
        const featureFlagStore = useFeatureFlagStore()
        featureFlagStore.toggleFeature("fetch_sensitive", sensitivityFlag)
        const searchStore = useSearchStore()
        const expectedQuery = { ...searchStore.apiSearchQueryParams, ...query }
        // The values that are not applicable for the search type should be discarded
        if (searchType === IMAGE) {
          delete expectedQuery.length
        }

        searchStore.setSearchStateFromUrl({ path: path, urlQuery: query })

        expect(searchStore.searchType).toEqual(searchType)
        expect(searchStore.apiSearchQueryParams).toEqual(expectedQuery)
      }
    )

    it("updateSearchPath updates searchType and query", () => {
      const searchStore = useSearchStore()
      searchStore.updateSearchPath({ type: "audio", searchTerm: "cat" })

      expect(searchStore.searchType).toEqual("audio")
      expect(searchStore.apiSearchQueryParams).toEqual({ q: "cat" })
      expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith({
        path: "/search/audio",
        query: { q: "cat" },
      })
    })

    it("updateSearchPath keeps searchType and query if none provided", () => {
      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")
      searchStore.setSearchType("audio")
      searchStore.updateSearchPath()

      expect(searchStore.searchType).toEqual("audio")
      expect(searchStore.apiSearchQueryParams).toEqual({ q: "cat" })
      expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith({
        path: "/search/audio",
        query: { q: "cat" },
      })
    })

    it("updateSearchPath updates searchType and query", () => {
      const searchStore = useSearchStore()
      searchStore.updateSearchPath({ type: "audio", searchTerm: "cat" })

      expect(searchStore.searchType).toEqual("audio")
      expect(searchStore.searchQueryParams).toEqual({ q: "cat" })
      expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith({
        path: "/search/audio",
        query: { q: "cat" },
      })
    })

    it("updateSearchPath keeps searchType and query if none provided", () => {
      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")
      searchStore.setSearchType("audio")
      searchStore.updateSearchPath()

      expect(searchStore.searchType).toEqual("audio")
      expect(searchStore.searchQueryParams).toEqual({ q: "cat" })
      expect(searchStore.$nuxt.localePath).toHaveBeenCalledWith({
        path: "/search/audio",
        query: { q: "cat" },
      })
    })

    it.each`
      filters                                                               | query
      ${[["licenses", "by"], ["licenses", "by-nc-sa"]]}                     | ${["license", "by,by-nc-sa"]}
      ${[["licenseTypes", "commercial"], ["licenseTypes", "modification"]]} | ${["license_type", "commercial,modification"]}
      ${[["sizes", "large"]]}                                               | ${["size", undefined]}
    `(
      "toggleFilter updates the query values to $query",
      ({ filters, query }) => {
        const searchStore = useSearchStore()
        for (const filterItem of filters) {
          const [filterType, code] = filterItem
          searchStore.toggleFilter({ filterType, code })
        }
        expect(searchStore.apiSearchQueryParams[query[0]]).toEqual(query[1])
      }
    )

    it.each([ALL_MEDIA, IMAGE, AUDIO, VIDEO])(
      "Clears filters when search type is %s",
      (searchType) => {
        const searchStore = useSearchStore()
        const expectedQueryParams = { q: "cat" }
        searchStore.setSearchStateFromUrl({
          path: `/search/${searchType === ALL_MEDIA ? "" : searchType}`,
          urlQuery: {
            q: "cat",
            license: "cc0",
            sizes: "large",
            extension: "jpg,mp3",
          },
        })
        if (supportedSearchTypes.includes(searchType)) {
          // eslint-disable-next-line jest/no-conditional-expect
          expect(searchStore.apiSearchQueryParams).not.toEqual(
            expectedQueryParams
          )
        }
        searchStore.clearFilters()
        expect(searchStore.apiSearchQueryParams).toEqual(expectedQueryParams)
      }
    )

    it.each`
      filterType           | codeIdx
      ${"licenses"}        | ${0}
      ${"licenseTypes"}    | ${0}
      ${"imageExtensions"} | ${0}
      ${"imageCategories"} | ${0}
      ${"aspectRatios"}    | ${0}
      ${"sizes"}           | ${0}
    `(
      "toggleFilter updates $filterType filter state",
      ({ filterType, codeIdx }) => {
        const searchStore = useSearchStore()

        searchStore.toggleFilter({ filterType, codeIdx })
        const filterItem = searchStore.filters[filterType][codeIdx]
        expect(filterItem.checked).toEqual(true)
      }
    )

    it("toggleFilter updates isFilterApplied with provider", () => {
      const searchStore = useSearchStore()
      searchStore.setSearchType(IMAGE)
      searchStore.updateProviderFilters({
        mediaType: IMAGE,
        providers: [{ source_name: "met", display_name: "Met" }],
      })

      searchStore.toggleFilter({ filterType: "imageProviders", code: "met" })
      expect(searchStore.appliedFilterCount).toEqual(1)
      expect(searchStore.isAnyFilterApplied).toEqual(true)
    })

    it("toggleFilter updates isFilterApplied with license type", () => {
      const searchStore = useSearchStore()
      searchStore.toggleFilter({ filterType: "licenseTypes", codeIdx: 0 })

      expect(searchStore.isAnyFilterApplied).toEqual(true)
    })

    it("updateProviderFilters merges with existing provider filters", () => {
      const searchStore = useSearchStore()
      const existingProviderFilters = [{ code: "met", checked: true }]

      searchStore.$patch({
        filters: { imageProviders: existingProviderFilters },
      })
      const providers = [
        { source_name: "met", display_name: "Metropolitan" },
        { source_name: "flickr", display_name: "Flickr" },
      ]

      searchStore.updateProviderFilters({
        mediaType: "image",
        providers: providers,
      })

      expect(searchStore.filters.imageProviders).toEqual([
        { code: "met", name: "Metropolitan", checked: true },
        { code: "flickr", name: "Flickr", checked: false },
      ])
    })

    it("clearFilters resets filters to initial state", () => {
      const searchStore = useSearchStore()
      searchStore.toggleFilter({ filterType: "licenses", code: "by" })
      searchStore.toggleFilter({ filterType: "licenses", code: "by-nc" })
      searchStore.toggleFilter({ filterType: "licenses", code: "by-nd" })

      searchStore.clearFilters()
      expect(searchStore.filters).toEqual(filterData)
    })

    it("clearFilters sets providers filters checked to false", () => {
      const searchStore = useSearchStore()
      searchStore.filters.imageProviders = [
        { code: "met", name: "Metropolitan", checked: true },
        { code: "flickr", name: "Flickr", checked: false },
      ]

      searchStore.clearFilters()
      const expectedFilters = {
        ...searchStore.filters,
        imageProviders: [
          { code: "met", name: "Metropolitan", checked: false },
          { code: "flickr", name: "Flickr", checked: false },
        ],
      }
      expect(searchStore.filters).toEqual(expectedFilters)
    })

    it.each`
      filterType           | code              | idx
      ${"licenses"}        | ${"cc0"}          | ${1}
      ${"licenseTypes"}    | ${"modification"} | ${1}
      ${"imageExtensions"} | ${"svg"}          | ${3}
      ${"imageCategories"} | ${"photograph"}   | ${0}
      ${"aspectRatios"}    | ${"tall"}         | ${0}
      ${"sizes"}           | ${"medium"}       | ${1}
    `(
      "toggleFilter should set filter '$code' of type '$filterType",
      ({ filterType, code, idx }) => {
        const searchStore = useSearchStore()
        searchStore.toggleFilter({ filterType: filterType, code: code })

        const filterItem = searchStore.filters[filterType][idx]

        expect(filterItem.checked).toEqual(true)
      }
    )
    it.each`
      item                                                    | dependency                                              | disabled
      ${{ code: "by-nc", filterType: "licenses" }}            | ${{ filterType: "licenseTypes", code: "commercial" }}   | ${true}
      ${{ code: "by-nc-nd", filterType: "licenses" }}         | ${{ filterType: "licenseTypes", code: "commercial" }}   | ${true}
      ${{ code: "by-nc-sa", filterType: "licenses" }}         | ${{ filterType: "licenseTypes", code: "commercial" }}   | ${true}
      ${{ code: "by-nd", filterType: "licenses" }}            | ${{ filterType: "licenseTypes", code: "modification" }} | ${true}
      ${{ code: "by-nc-nd", filterType: "licenses" }}         | ${{ filterType: "licenseTypes", code: "modification" }} | ${true}
      ${{ code: "by-nc", filterType: "licenses" }}            | ${{ filterType: "licenseTypes", code: "modification" }} | ${false}
      ${{ code: "by-nd", filterType: "licenses" }}            | ${{ filterType: "licenseTypes", code: "commercial" }}   | ${false}
      ${{ code: "commercial", filterType: "licenseTypes" }}   | ${{ filterType: "licenses", code: "by-nc" }}            | ${true}
      ${{ code: "commercial", filterType: "licenseTypes" }}   | ${{ filterType: "licenses", code: "by-nc-nd" }}         | ${true}
      ${{ code: "commercial", filterType: "licenseTypes" }}   | ${{ filterType: "licenses", code: "by-nc-sa" }}         | ${true}
      ${{ code: "modification", filterType: "licenseTypes" }} | ${{ filterType: "licenses", code: "by-nd" }}            | ${true}
      ${{ code: "modification", filterType: "licenseTypes" }} | ${{ filterType: "licenses", code: "by-nc-nd" }}         | ${true}
      ${{ code: "jpg", filterType: "imageExtensions" }}       | ${{ filterType: "imageExtensions", code: "png" }}       | ${false}
    `(
      "isFilterDisabled for $item.code should return $disabled when $dependency.code is checked",
      ({ item, dependency, disabled }) => {
        const searchStore = useSearchStore()
        searchStore.toggleFilter({
          filterType: dependency.filterType,
          code: dependency.code,
        })
        const isDisabled = searchStore.isFilterDisabled(item, item.filterType)
        expect(isDisabled).toBe(disabled)
      }
    )

    it("toggleFilter without code or codeIdx parameters warns about it", () => {
      const searchStore = useSearchStore()
      const expectedFilters = searchStore.filters

      expect(() =>
        searchStore.toggleFilter({ filterType: "licenses" })
      ).toThrow(
        "Cannot update filter of type licenses. Use code or codeIdx parameter"
      )

      expect(searchStore.filters).toEqual(expectedFilters)
    })

    it.each`
      searchType   | nextSearchType | expectedFilterCount
      ${AUDIO}     | ${IMAGE}       | ${23}
      ${IMAGE}     | ${ALL_MEDIA}   | ${10}
      ${IMAGE}     | ${AUDIO}       | ${28}
      ${ALL_MEDIA} | ${VIDEO}       | ${10}
      ${VIDEO}     | ${AUDIO}       | ${28}
      ${ALL_MEDIA} | ${IMAGE}       | ${23}
    `(
      "changing searchType from $searchType clears all but $expectedFilterCount $nextSearchType filters",
      async ({ searchType, nextSearchType, expectedFilterCount }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)

        const featureFlagStore = useFeatureFlagStore()
        featureFlagStore.toggleFeature("additional_search_types", "on")

        // Set all filters to checked
        for (let ft in searchStore.filters) {
          for (let f of searchStore.filters[ft]) {
            searchStore.toggleFilter({ filterType: ft, code: f.code })
          }
        }
        searchStore.setSearchType(nextSearchType)
        await nextTick()

        const checkedFilterCount = Object.keys(searchStore.filters)
          .map(
            (key) => searchStore.filters[key].filter((f) => f.checked).length
          )
          .reduce((partialSum, count) => partialSum + count, 0)
        expect(checkedFilterCount).toEqual(expectedFilterCount)
      }
    )

    it("Does not set filter or count filter as applied, and does not raise error for unsupported search types", () => {
      const searchStore = useSearchStore()
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("additional_search_types", "on")
      searchStore.toggleFilter({
        filterType: "licenseTypes",
        code: "commercial",
      })
      expect(searchStore.isAnyFilterApplied).toEqual(true)

      searchStore.setSearchType(VIDEO)
      searchStore.toggleFilter({
        filterType: "licenseTypes",
        code: "commercial",
      })
      expect(searchStore.isAnyFilterApplied).toEqual(false)
    })

    describe("Recent searches", () => {
      it("are saved, without duplication and not exceeding the limit.", () => {
        const searchStore = useSearchStore()
        searchStore.setSearchTerm("boop")
        searchStore.setSearchTerm("bar")
        searchStore.setSearchTerm("foo")
        searchStore.setSearchTerm("baz")
        searchStore.setSearchTerm("boom")
        searchStore.setSearchTerm("foo")

        expect(searchStore.recentSearches).toEqual([
          "foo",
          "boom",
          "baz",
          "bar",
        ])
        expect(searchStore.recentSearches.length).toEqual(
          parseInt(env.savedSearchCount)
        )
      })
      it("can be cleared", () => {
        const searchStore = useSearchStore()
        // Clear up front in case of any preserved searches
        searchStore.clearRecentSearches()

        searchStore.setSearchTerm("boop")
        searchStore.setSearchTerm("bar")

        expect(searchStore.recentSearches).toEqual(["bar", "boop"])

        searchStore.clearRecentSearches()

        expect(searchStore.recentSearches).toEqual([])
      })
    })
  })

  describe("computeQueryParams", () => {
    it("should return only `q` if search type is not supported", () => {
      const params = computeQueryParams(VIDEO, {}, "cat", "frontend")
      expect(params).toEqual({ q: "cat" })
    })

    it("should not set sensitive query param if mode is `frontend`", () => {
      const searchStore = useSearchStore()
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("fetch_sensitive", "on")

      const params = computeQueryParams(
        IMAGE,
        searchStore.filters,
        "cat",
        "frontend"
      )
      expect(params).toEqual({ q: "cat" })
    })
    it("should set sensitive query param if mode is `API`", () => {
      const searchStore = useSearchStore()
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("fetch_sensitive", "on")

      const params = computeQueryParams(
        IMAGE,
        searchStore.filters,
        "cat",
        "API"
      )
      expect(params).toEqual({
        q: "cat",
        unstable__include_sensitive_results: "true",
      })
    })
  })
})
