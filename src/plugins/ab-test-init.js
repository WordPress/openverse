import abTests, { activeExperiments } from '~/ab-tests'

/**
 * Initialize our ab tests on the client-side
 * @param {import('@nuxt/types').Context} context
 */
export default function abTestInit(context) {
  if (activeExperiments.length > 0) {
    abTests(context.store, activeExperiments)
  }
}
