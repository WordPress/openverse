import { defineStore } from 'pinia'

import {
  FetchState,
  initialFetchState,
  updateFetchState,
} from '~/composables/use-fetch-state'
import { services } from '~/stores/media/services'
import type { Media } from '~/models/media'
import type { SupportedMediaType } from '~/constants/media'

interface RelatedMediaState {
  mainMediaId: null | string
  media: Media[]
  fetchState: FetchState
}

export const useRelatedMediaStore = defineStore('related-media', {
  state: (): RelatedMediaState => ({
    mainMediaId: null,
    fetchState: { ...initialFetchState },
    media: [],
  }),

  getters: {
    getItemById:
      (state) =>
      (id: string): Media | undefined =>
        state.media.find((item) => item.id === id),
  },

  actions: {
    async fetchMedia(mediaType: SupportedMediaType, id: string) {
      this.mainMediaId = id
      this.fetchState = updateFetchState(this.fetchState, 'start')
      this.media = []
      try {
        this.media = (
          await services[mediaType].getRelatedMedia<typeof mediaType>(id)
        ).results
        this.fetchState = updateFetchState(this.fetchState, 'end')
      } catch (error) {
        this.fetchState = updateFetchState(
          this.fetchState,
          'end',
          `Could not fetch related ${mediaType} for id ${id}`
        )
      }
    },
  },
})
