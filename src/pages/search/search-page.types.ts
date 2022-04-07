import type { SupportedMediaType } from '~/constants/media'
import type { Media } from '~/models/media'
import type { FetchState } from '~/composables/use-fetch-state'

import type { ExtractPropTypes, PropType } from '@nuxtjs/composition-api'

export const propTypes = {
  resultItems: {
    type: Object as PropType<Record<SupportedMediaType, Media[]>>,
    required: true,
  },
  fetchState: {
    type: Object as PropType<FetchState>,
    required: true,
  },
  isFilterVisible: {
    type: Boolean,
    required: false,
  },
  searchTerm: {
    type: String,
    required: true,
  },
  supported: {
    type: Boolean,
    required: false,
  },
}
export type SearchPageProps = ExtractPropTypes<typeof propTypes>
