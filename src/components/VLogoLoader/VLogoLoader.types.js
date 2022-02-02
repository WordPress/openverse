export const propTypes = {
  status: {
    type: /** @type {'loading'|'idle'} */ (String),
    default: 'idle',
    required: false,
  },
  autoResize: {
    type: Boolean,
    default: true,
  },
}

/** @typedef {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} Props */
