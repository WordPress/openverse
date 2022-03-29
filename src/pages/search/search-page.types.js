export const propTypes = {
  resultItems: {
    type: /** @type {import('../../store/types').Media[]} */ (Object),
    required: true,
  },
  fetchState: {
    type: /** @type {import('../../store/types').FetchState[]} */ (Object),
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

/** @typedef {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} Props */
