import { JOINED_AB_TEST_EXPERIMENT } from '~/constants/mutation-types'
import { CONVERT_AB_TEST_EXPERIMENT } from '~/constants/action-types'
import { convert } from '~/utils/sixpack'

export const state = () => ({
  experiments: [],
})

export const actions = {
  [CONVERT_AB_TEST_EXPERIMENT](context, params) {
    const experiment = context.state.experiments.find(
      ({ name }) => name === params.name
    )
    const sessionId = context.state.abSessionId

    if (!experiment) {
      return
    }

    convert(experiment.name, { sessionId }).catch(() =>
      console.error(
        `A/B test ${experiment.name} failed to convert with case ${experiment.case}.`
      )
    )
  },
}

export const mutations = {
  [JOINED_AB_TEST_EXPERIMENT](_state, params) {
    _state.experiments = [{ ...params }, ..._state.experiments]
  },
}

export default {
  state,
  mutations,
  actions,
}
