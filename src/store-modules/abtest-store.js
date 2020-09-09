import { JOINED_AB_TEST_EXPERIMENT } from './mutation-types'
import { CONVERT_AB_TEST_EXPERIMENT } from './action-types'

const state = {
  experiments: [],
}

const actions = {
  [CONVERT_AB_TEST_EXPERIMENT](context, params) {
    const abTestData = context.state.experiments.filter(
      (experiment) => experiment.name === params.experimentName
    )

    if (abTestData.length > 0) {
      const session = abTestData[0].session
      session.convert(params.experimentName)
    }
  },
}

const mutations = {
  [JOINED_AB_TEST_EXPERIMENT](_state, params) {
    _state.experiments = [{ ...params }, ..._state.experiments]
  },
}

export default {
  state,
  mutations,
  actions,
}
