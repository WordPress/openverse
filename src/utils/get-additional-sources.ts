import buildUrl from 'build-url'

import type { MediaType } from '~/constants/media'
import type { ApiQueryParams } from '~/utils/search-query-transform'

import type { BuildUrlOptions } from 'build-url'

/**
 * Describes the query format used by the URL builder functions of additional
 * sources. This includes the query string and the usage filters.
 */
interface AdditionalSearchQuery {
  q: string
  filters: {
    commercial: boolean
    modify: boolean
  }
}

/**
 * Convert the ApiQueryParams object from the store to a format used by all the
 * URL builder functions of all additional sources.
 *
 * @param query - the ApiQueryParams object
 * @returns the query and filters in the format used by the URL builders
 */
const transformSearchQuery = (
  query: ApiQueryParams
): AdditionalSearchQuery => ({
  q: query.q ?? '',
  filters: {
    commercial: query.license_type?.includes('commercial') ?? false,
    modify: query.license_type?.includes('modification') ?? false,
  },
})

type SearchFunctions = {
  [k in MediaType]?: (
    search: AdditionalSearchQuery
  ) => BuildUrlOptions & { url: string }
}

/**
 * Describes an additional source builder, which contains a display name,
 * whether the source supports use filters and a mapping of media type to a URL
 * builder function that leads to the search results for that media type.
 */
interface AdditionalSourceBuilder extends SearchFunctions {
  name: string
  supportsUseFilters: boolean
}

/**
 * Describes an additional source, consisting of the source name and the
 * pre-populated URL.
 */
interface AdditionalSource {
  name: string
  url: string
}

/**
 * Maps each additional source with search URL builder functions for each
 * content type.
 *
 * @see {@link https://github.com/creativecommons/cccatalog-frontend/issues/315}
 */
const additionalSourceBuilders: AdditionalSourceBuilder[] = [
  {
    name: 'Centre For Ageing Better',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://ageingbetter.resourcespace.com/pages/search.php',
      queryParams: {
        search: search.q,
      },
    }),
  },
  {
    name: 'EDU images',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://images.all4ed.org',
      queryParams: {
        s: search.q,
      },
    }),
  },
  {
    name: 'Google Images',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://www.google.com/search',
      queryParams: {
        q: search.q,
        tbm: 'isch', // this means 'search images'
        tbs: 'il:cl',
      },
    }),
  },
  {
    name: 'Images of Empowerment',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://www.imagesofempowerment.org/',
      queryParams: {
        s: search.q,
      },
    }),
  },
  {
    name: 'Open Clip Art Library',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'http://www.openclipart.org/search/',
      queryParams: {
        query: search.q,
      },
    }),
  },
  {
    name: 'Nappy',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://www.nappy.co/',
      queryParams: {
        s: search.q,
      },
    }),
  },
  {
    name: 'The Greats',
    supportsUseFilters: false,
    image: (search) => ({
      url: 'https://www.thegreats.co/artworks/',
      queryParams: {
        theme: '0',
        search: search.q,
      },
    }),
  },
  {
    name: 'ccMixter',
    supportsUseFilters: false,
    audio: (search) => ({
      // no https :(
      url: 'http://dig.ccmixter.org/search',
      queryParams: {
        lic: 'open',
        searchp: search.q,
      },
    }),
  },
  {
    name: 'SoundCloud',
    supportsUseFilters: true,
    audio: (search) => {
      let license = 'to_share'

      if (search.filters && search.filters.commercial) {
        if (search.filters.commercial) license = 'to_use_commercially'
        if (search.filters.modify) license = 'to_modify_commercially'
      }

      return {
        url: 'https://soundcloud.com/search/sounds',
        queryParams: {
          q: search.q,
          'filter.license': license, // @todo: choose which type from the search object
        },
      }
    },
  },
  {
    name: 'Europeana',
    supportsUseFilters: true,
    audio: (search) => {
      let query = `${search.q} AND RIGHTS:*creative*` // search cc licensed works

      if (search.filters && search.filters.commercial) {
        if (search.filters.commercial) query = `${query} AND NOT RIGHTS:*nc*`
        if (search.filters.modify) query = `${query} AND NOT RIGHTS:*nd*`
      }

      return {
        url: 'https://www.europeana.eu/en/search',
        queryParams: {
          page: '1',
          qf: 'TYPE:"SOUND"',
          query,
        },
      }
    },
    video(search) {
      let query = `${search.q} AND RIGHTS:*creative*` // search cc licensed works

      if (search.filters && search.filters.commercial) {
        if (search.filters.commercial) query = `${query} AND NOT RIGHTS:*nc*`
        if (search.filters.modify) query = `${query} AND NOT RIGHTS:*nd*`
      }

      return {
        url: 'https://www.europeana.eu/en/search',
        queryParams: {
          page: '1',
          qf: 'TYPE:"VIDEO"',
          query,
        },
      }
    },
  },
  {
    name: 'Vimeo',
    supportsUseFilters: false,
    video: (search) => ({
      url: 'https://vimeo.com/search',
      queryParams: {
        license: 'by',
        q: search.q,
      },
    }),
  },
  {
    name: 'Wikimedia Commons',
    supportsUseFilters: false,
    video: (search) => ({
      url: 'https://commons.wikimedia.org/w/index.php',
      queryParams: {
        search: `${search.q}`,
        title: 'Special:MediaSearch',
        type: 'video',
      },
    }),
  },
  {
    name: 'YouTube',
    supportsUseFilters: false,
    video: (search) => ({
      url: 'https://www.youtube.com/results',
      queryParams: {
        search_query: search.q,
        sp: 'EgIwAQ%3D%3D', // this interesting line filters by cc license
      },
    }),
  },
  {
    name: 'Sketchfab',
    supportsUseFilters: false,
    model_3d(search) {
      // TODO: Use actual license from filters
      const licenseCodes: string[] = [
        '322a749bcfa841b29dff1e8a1bb74b0b', // CC BY
        'b9ddc40b93e34cdca1fc152f39b9f375', // CC BY-SA
        '72360ff1740d419791934298b8b6d270', // CC BY-ND
        'bbfe3f7dbcdd4122b966b85b9786a989', // CC BY-NC
        '2628dbe5140a4e9592126c8df566c0b7', // CC BY-NC-SA
        '34b725081a6a4184957efaec2cb84ed3', // CC BY-NC-ND
        '7c23a1ba438d4306920229c12afcb5f9', // CC0
      ]
      return {
        url: 'https://sketchfab.com/search',
        queryParams: {
          q: search.q,
          licenses: licenseCodes,
        },
        disableCSV: true,
      }
    },
  },
  {
    name: 'Thingiverse',
    supportsUseFilters: false,
    model_3d(search) {
      return {
        url: 'https://www.thingiverse.com/search',
        queryParams: {
          type: 'things',
          q: search.q,
        },
      }
    },
  },
]

/**
 * Get a list of source builders for a given media type.
 *
 * @param mediaType - the media type by which to filter source builders
 * @returns a list of additional source builders
 */
export const getAdditionalSourceBuilders = (
  mediaType: MediaType
): AdditionalSourceBuilder[] =>
  additionalSourceBuilders.filter((source) => source[mediaType])

/**
 * Get a list of sources for a given media type with the URL populated to show
 * the results of the given query.
 *
 * @param mediaType - the media type by which to filter source builders
 * @param query - the query to show results for in the additional sources
 * @returns a list of additional sources with pre-populated URLs
 */
export const getAdditionalSources = (
  mediaType: MediaType,
  query: ApiQueryParams
) =>
  getAdditionalSourceBuilders(mediaType).map((source) => {
    const urlFunc = source[mediaType]

    if (!urlFunc) return undefined // type-guard, never occurs

    const urlInfo = urlFunc(transformSearchQuery(query))
    return {
      url: buildUrl(urlInfo.url, urlInfo),
      name: source.name,
      supportsUseFilters: source.supportsUseFilters,
    }
  }) as AdditionalSource[]
