<template>
  <div>
    <search-grid-infinite-load v-if="renderInfiniteLoad()" />
    <search-grid-manual-load v-else-if="renderManualLoad()" />
  </div>
</template>

<script>
import SearchGridInfiniteLoad from '@/components/SearchGridInfiniteLoad';
import SearchGridManualLoad from '@/components/SearchGridManualLoad';
import { ExperimentData as InfiniteLoadingExperiment } from '@/abTests/infiniteLoadingExperiment';

export default {
  name: 'search-grid',
  components: {
    SearchGridInfiniteLoad,
    SearchGridManualLoad,
  },
  methods: {
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
};
</script>

