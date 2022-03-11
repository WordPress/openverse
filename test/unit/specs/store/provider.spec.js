import { createPinia, setActivePinia } from 'pinia'

import { state, mutations, createActions } from '~/store/provider'
import {
  FETCH_MEDIA_PROVIDERS_END,
  FETCH_MEDIA_PROVIDERS_START,
  SET_MEDIA_PROVIDERS,
  SET_PROVIDER_FETCH_ERROR,
} from '~/constants/mutation-types'
import { FETCH_MEDIA_TYPE_PROVIDERS } from '~/constants/action-types'
import { IMAGE } from '~/constants/media'

describe('Image Provider Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      expect(state().imageProviders).toHaveLength(0)
      expect(state().isFetchingImageProvidersError).toBeFalsy()
      expect(state().isFetchingImageProviders).toBeFalsy()
    })
  })

  describe('mutations', () => {
    let store = {}
    let serviceMock = null

    beforeEach(() => {
      serviceMock = jest.fn()
      store = {
        state: state(),
        mutations: mutations,
        actions: createActions(serviceMock),
      }
    })

    it('FETCH_MEDIA_PROVIDERS_START sets isFetchingImageProviders to true', () => {
      store.mutations[FETCH_MEDIA_PROVIDERS_START](store.state, {
        mediaType: 'image',
      })

      expect(store.state.isFetchingImageProviders).toBeTruthy()
    })

    it('FETCH_MEDIA_PROVIDERS_END sets isFetchingImageProviders to false', () => {
      store.mutations[FETCH_MEDIA_PROVIDERS_END](store.state, {
        mediaType: 'image',
      })

      expect(store.state.isFetchingImageProviders).toBeFalsy()
    })

    it('SET_PROVIDER_FETCH_ERROR sets isFetchingImageProvidersError', () => {
      const params = {
        mediaType: 'image',
        error: true,
      }
      store.mutations[SET_PROVIDER_FETCH_ERROR](store.state, params)

      expect(store.state.isFetchingImageProvidersError).toBe(params.error)
    })
  })

  describe('actions', () => {
    const data = [{ source_name: 'foo' }, { source_name: 'bar' }]
    const imageProviderServiceMock = {
      getProviderStats: jest.fn(() => Promise.resolve({ data })),
    }
    const services = { [IMAGE]: imageProviderServiceMock }
    const commit = jest.fn()
    const dispatch = jest.fn()

    it('FETCH_MEDIA_TYPE_PROVIDERS on success', (done) => {
      setActivePinia(createPinia())
      const action = createActions(services)[FETCH_MEDIA_TYPE_PROVIDERS]
      action({ commit, dispatch }, { mediaType: 'image' }).then(() => {
        expect(commit).toBeCalledWith(SET_PROVIDER_FETCH_ERROR, {
          error: false,
          mediaType: 'image',
        })
        expect(commit).toBeCalledWith(FETCH_MEDIA_PROVIDERS_START, {
          mediaType: 'image',
        })

        expect(imageProviderServiceMock.getProviderStats).toBeCalled()

        expect(commit).toBeCalledWith(FETCH_MEDIA_PROVIDERS_END, {
          mediaType: 'image',
        })
        expect(commit).toBeCalledWith(SET_MEDIA_PROVIDERS, {
          mediaType: 'image',
          providers: data,
        })
        done()
      })
    })
  })
})
