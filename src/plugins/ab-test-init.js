import abTests from '~/abTests'

/**
 * Initialize our ab tests on the client-side
 * @param {import('@nuxt/types').Context} context
 */
export default function abTestInit(context) {
  abTests(context.store)
}
