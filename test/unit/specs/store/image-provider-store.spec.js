import store from '~/store-modules/image-provider-store'
import {
  FETCH_IMAGE_PROVIDERS_END,
  SET_FETCH_IMAGES_ERROR,
  FETCH_IMAGE_PROVIDERS_START,
  SET_IMAGE_PROVIDERS,
} from '~/store-modules/mutation-types'
import { FETCH_IMAGE_PROVIDERS } from '~/store-modules/action-types'

describe('Image Provider Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      expect(store.state.imageProviders).toHaveLength(0)
      expect(store.state.isFetchingImageProvidersError).toBeFalsy()
      expect(store.state.isFetchingImageProviders).toBeFalsy()
    })
  })

  describe('mutations', () => {
    let state = null

    beforeEach(() => {
      state = {}
    })

    it('FETCH_IMAGE_PROVIDERS_START sets isFetchingImageProviders to true', () => {
      store.mutations[FETCH_IMAGE_PROVIDERS_START](state)

      expect(state.isFetchingImageProviders).toBeTruthy()
    })

    it('FETCH_IMAGE_PROVIDERS_END sets isFetchingImageProviders to false', () => {
      store.mutations[FETCH_IMAGE_PROVIDERS_END](state)

      expect(state.isFetchingImageProviders).toBeFalsy()
    })

    it('SET_FETCH_IMAGES_ERROR sets isFetchingImageProvidersError', () => {
      const params = {
        isFetchingImageProvidersError: true,
      }
      store.mutations[SET_FETCH_IMAGES_ERROR](state, params)

      expect(state.isFetchingImageProvidersError).toBe(
        params.isFetchingImageProvidersError
      )
    })

    it('SET_IMAGE_PROVIDERS sets imageProviders', () => {
      const params = {
        imageProviders: true,
      }
      store.mutations[SET_IMAGE_PROVIDERS](state, params)

      expect(state.imageProviders).toBe(params.imageProviders)
    })
  })

  describe('actions', () => {
    const data = [{ source_name: 'foo' }, { source_name: 'bar' }]
    const imageProviderServiceMock = {
      getProviderStats: jest.fn(() => Promise.resolve({ data })),
    }
    const commit = jest.fn()
    it('FETCH_IMAGE_PROVIDERS on success', (done) => {
      const action = store.actions(imageProviderServiceMock)[
        FETCH_IMAGE_PROVIDERS
      ]
      action({ commit }, {}).then(() => {
        expect(commit).toBeCalledWith(SET_FETCH_IMAGES_ERROR, {
          isFetchingImageProvidersError: false,
        })
        expect(commit).toBeCalledWith(FETCH_IMAGE_PROVIDERS_START)

        expect(imageProviderServiceMock.getProviderStats).toBeCalled()

        expect(commit).toBeCalledWith(FETCH_IMAGE_PROVIDERS_END)
        expect(commit).toBeCalledWith(SET_IMAGE_PROVIDERS, {
          imageProviders: data,
        })
        done()
      })
    })

    it('FETCH_IMAGE_PROVIDERS on failure', (done) => {
      const failedServiceMock = {
        getProviderStats: jest.fn(() => Promise.reject('error')),
      }
      const action = store.actions(failedServiceMock)[FETCH_IMAGE_PROVIDERS]
      action({ commit }, {}).catch(() => {
        expect(imageProviderServiceMock.getProviderStats).toBeCalled()
        expect(commit).toBeCalledWith(SET_FETCH_IMAGES_ERROR, {
          isFetchingImageProvidersError: true,
        })
        done()
      })
    })
  })
})
