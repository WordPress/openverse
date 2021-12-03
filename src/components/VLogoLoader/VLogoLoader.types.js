export const propTypes = {
  status: {
    type: /** @type {'loading'|'idle'} */ (String),
    default: 'idle',
    required: false,
  },
}

/** @typedef {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} Props */
