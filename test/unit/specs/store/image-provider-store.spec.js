import store from '~/store-modules/media-provider-store'
import {
  FETCH_MEDIA_PROVIDERS_END,
  FETCH_MEDIA_PROVIDERS_START,
  SET_MEDIA_PROVIDERS,
  SET_PROVIDER_FETCH_ERROR,
} from '~/store-modules/mutation-types'
// import { FETCH_MEDIA_PROVIDERS } from '~/store-modules/action-types'

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

    it('FETCH_MEDIA_PROVIDERS_START sets isFetchingImageProviders to true', () => {
      store.mutations[FETCH_MEDIA_PROVIDERS_START](state, {
        mediaType: 'image',
      })

      expect(state.isFetchingImageProviders).toBeTruthy()
    })

    it('FETCH_MEDIA_PROVIDERS_END sets isFetchingImageProviders to false', () => {
      store.mutations[FETCH_MEDIA_PROVIDERS_END](state, { mediaType: 'image' })

      expect(state.isFetchingImageProviders).toBeFalsy()
    })

    it('SET_PROVIDER_FETCH_ERROR sets isFetchingImageProvidersError', () => {
      const params = {
        mediaType: 'image',
        error: true,
      }
      store.mutations[SET_PROVIDER_FETCH_ERROR](state, params)

      expect(state.isFetchingImageProvidersError).toBe(params.error)
    })

    it('SET_IMAGE_PROVIDERS sets imageProviders', () => {
      const params = {
        mediaType: 'image',
        providers: [{ name: 'testProvider' }],
      }
      store.mutations[SET_MEDIA_PROVIDERS](state, params)

      expect(state.imageProviders).toBe(params.providers)
    })
  })

  // TODO: Fix the tests
  // describe('actions', () => {
  //   const data = [{ source_name: 'foo' }, { source_name: 'bar' }]
  //   const imageProviderServiceMock = {
  //     getProviderStats: jest.fn(() => Promise.resolve({ data })),
  //   }
  //   const commit = jest.fn()
  //   const dispatch = jest.fn()
  //   it('FETCH_MEDIA_PROVIDERS on success', (done) => {
  //     const action = store.actions(imageProviderServiceMock)[
  //       FETCH_MEDIA_PROVIDERS
  //     ]
  //     action({ commit, dispatch }, { mediaType: 'image' }).then(() => {
  //       expect(commit).toBeCalledWith(SET_PROVIDER_FETCH_ERROR, {
  //         error: false,
  //       })
  //       expect(commit).toBeCalledWith(FETCH_MEDIA_PROVIDERS_START)
  //
  //       expect(imageProviderServiceMock.getProviderStats).toBeCalled()
  //
  //       expect(commit).toBeCalledWith(FETCH_MEDIA_PROVIDERS_END)
  //       expect(commit).toBeCalledWith(SET_MEDIA_PROVIDERS, {
  //         providers: data,
  //       })
  //       done()
  //     })
  //   })

  // it('FETCH_MEDIA_PROVIDERS on failure', (done) => {
  //   const failedServiceMock = {
  //     getProviderStats: jest.fn(() => Promise.reject('error')),
  //   }
  //   const action = store.actions(failedServiceMock, failedServiceMock)[
  //     FETCH_MEDIA_PROVIDERS
  //   ]
  //   action({ commit, dispatch }, { mediaType: 'image' }).catch(() => {
  //     expect(imageProviderServiceMock.getProviderStats).toBeCalled()
  //     expect(commit).toBeCalledWith(SET_PROVIDER_FETCH_ERROR, {
  //       error: true,
  //     })
  //     done()
  //   })
  // })
  // })
})
