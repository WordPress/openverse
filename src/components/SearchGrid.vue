<template>
  <div>
    <search-grid-infinite-load v-if="renderInfiniteLoad"
                               :query="query"
                               :searchTerm="searchTerm"
                               @onLoadMoreImages="onLoadMoreImages" />
    <search-grid-manual-load v-else-if="renderManualLoad"
                             :query="query"
                             :searchTerm="searchTerm"
                             @onLoadMoreImages="onLoadMoreImages" />
  </div>
</template>

<script>
import SearchGridInfiniteLoad from '@/components/SearchGridInfiniteLoad';
import SearchGridManualLoad from '@/components/SearchGridManualLoad';
import { ExperimentData as InfiniteLoadingExperiment } from '@/abTests/infiniteLoadingExperiment';
import { CONVERT_AB_TEST_EXPERIMENT } from '@/store/action-types';

export default {
  name: 'search-grid',
  components: {
    SearchGridInfiniteLoad,
    SearchGridManualLoad,
  },
  props: ['query', 'searchTerm'],
  computed: {
    renderInfiniteLoad() {
      return this.$store.state.experiments.some(experiment =>
        experiment.name === InfiniteLoadingExperiment.EXPERIMENT_NAME &&
        experiment.case === InfiniteLoadingExperiment.INFINITE_LOADING_EXPERIMENT,
      );
    },
    renderManualLoad() {
      return this.$store.state.experiments.some(experiment =>
        experiment.name === InfiniteLoadingExperiment.EXPERIMENT_NAME &&
        experiment.case === InfiniteLoadingExperiment.MANUAL_LOADING_EXPERIMENT,
      );
    },
  },
  methods: {
    onLoadMoreImages(searchParams) {
      this.$store.dispatch(
        CONVERT_AB_TEST_EXPERIMENT,
        { experimentName: InfiniteLoadingExperiment.EXPERIMENT_NAME },
      );
      this.$emit('onLoadMoreImages', searchParams);
    },
  },
};
</script>

