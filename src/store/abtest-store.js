import { JOINED_AB_TEST_EXPERIMENT } from './mutation-types';

const state = {
  experiments: [],
};

const mutations = () => ({
  [JOINED_AB_TEST_EXPERIMENT](_state, params) {
    // eslint-disable-next-line no-param-reassign
    _state.experiments = [
      { ...params },
      ..._state.experiments,
    ];
  },
});

export default {
  state,
  mutations,
};
