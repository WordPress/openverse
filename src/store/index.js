import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'
import SearchStore from '~/store-modules/search-store'
import FilterStore from '~/store-modules/filter-store'
import { FETCH_MEDIA_PROVIDERS } from '~/constants/action-types'
import { PROVIDER } from '~/constants/store-modules'
import { AUDIO, IMAGE } from '~/constants/media'

const mediaServices = { [AUDIO]: AudioService, [IMAGE]: ImageService }

export const actions = Object.assign(
  SearchStore.actions(mediaServices),
  FilterStore.actions,
  {
    async nuxtServerInit({ dispatch }) {
      try {
        await dispatch(`${PROVIDER}/${FETCH_MEDIA_PROVIDERS}`)
      } catch (error) {
        // TODO: What happens if we do not have image providers?
        // How do we show the error to the user?
        console.error("Couldn't fetch media providers")
      }
    },
  }
)

export const state = () => Object.assign(SearchStore.state, FilterStore.state)

export const getters = Object.assign(FilterStore.getters)

export const mutations = Object.assign(
  SearchStore.mutations,
  FilterStore.mutations
)
