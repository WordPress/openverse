import { createPinia, setActivePinia } from 'pinia'

import { AUDIO, IMAGE, supportedMediaTypes } from '~/constants/media'
import { useSearchStore } from '~/stores/search'
import { useProviderStore } from '~/stores/provider'
import { providerServices } from '~/data/media-provider-service'
import { initialFetchState } from '~/composables/use-fetch-state'

jest.mock('axios', () => ({
  ...jest.requireActual('axios'),
  isAxiosError: jest.fn((obj) => 'response' in obj),
}))
jest.mock('@nuxtjs/composition-api', () => ({
  ...jest.requireActual('@nuxtjs/composition-api'),
  ssrRef: (v) => jest.fn(v),
}))
process.env.providerUpdateFrequency = '0'

const mockData = [
  {
    source_name: 'test_source',
    display_name: '',
    source_url: 'https://test.org',
    logo_url: null,
    media_count: 4,
  },
  {
    source_name: 'wikimedia',
    display_name: 'Wikimedia Commons',
    source_url: 'https://commons.wikimedia.org',
    logo_url: null,
    media_count: 47823833,
  },
  {
    source_name: 'wordpress',
    display_name: 'WP Photo Directory',
    source_url: 'https://wordpress.org/photos',
    logo_url: null,
    media_count: 154,
  },
]

jest.mock('~/data/media-provider-service', () => ({
  providerServices: {
    audio:
      /** @type {typeof import('~/data/media-provider-services').MediaProviderService} */ ({
        getProviderStats: jest.fn(),
      }),
    image:
      /** @type {typeof import('~/data/media-provider-services').MediaProviderService} */ ({
        getProviderStats: jest.fn(),
      }),
  },
}))
for (const mediaType of supportedMediaTypes) {
  providerServices[mediaType].getProviderStats.mockImplementation(() =>
    Promise.resolve({ data: [...mockData] })
  )
}

describe('Provider Store', () => {
  let providerStore
  beforeEach(() => {
    setActivePinia(createPinia())
    providerStore = useProviderStore()
  })
  afterEach(() => {
    providerServices.audio.getProviderStats.mockClear()
    providerServices.image.getProviderStats.mockClear()
  })
  it('sets the default state', () => {
    expect(providerStore.providers).toEqual({
      [AUDIO]: [],
      [IMAGE]: [],
    })
    expect(providerStore.fetchState).toEqual({
      [AUDIO]: initialFetchState,
      [IMAGE]: initialFetchState,
    })
  })

  it.each`
    providerCode     | displayName
    ${'wikimedia'}   | ${'Wikimedia Commons'}
    ${'wordpress'}   | ${'WP Photo Directory'}
    ${'test_source'} | ${'Test Source'}
  `(
    'getProviderName returns provider name or capitalizes providerCode',
    async ({ providerCode, displayName }) => {
      await providerStore.fetchMediaProviders()
      expect(providerStore.getProviderName(providerCode, IMAGE)).toEqual(
        displayName
      )
    }
  )

  it('fetchMediaProviders on success', async () => {
    const searchStore = useSearchStore()
    searchStore.setSearchType(IMAGE)

    const expectedFilters = [
      {
        checked: false,
        code: 'test_source',
        name: '',
      },
      {
        checked: false,
        code: 'wikimedia',
        name: 'Wikimedia Commons',
      },
      {
        checked: false,
        code: 'wordpress',
        name: 'WP Photo Directory',
      },
    ]
    await providerStore.fetchMediaProviders()
    expect(providerStore.fetchState[IMAGE]).toEqual({
      ...initialFetchState,
      hasStarted: true,
    })
    expect(providerStore.providers[IMAGE]).toEqual(mockData)

    expect(searchStore.filters[`${IMAGE}Providers`]).toEqual(expectedFilters)
  })

  it('fetchMediaProviders on error', async () => {
    for (const mediaType of supportedMediaTypes) {
      providerServices[mediaType].getProviderStats.mockImplementation(() =>
        Promise.reject(new Error('Not found'))
      )
    }
    const searchStore = useSearchStore()
    await providerStore.fetchMediaProviders()
    for (const mediaType of supportedMediaTypes) {
      expect(providerStore.fetchState[mediaType].fetchingError).toEqual(
        `There was an error fetching media providers for ${mediaType}: Not found`
      )
      expect(providerStore.providers[mediaType]).toEqual([])
      expect(searchStore.filters[`${mediaType}Providers`]).toEqual([])
    }
  })
})
