<template>
  <div>
    <search-grid-form-original v-if="renderOriginalFilter"
                               v-bind="$attrs"
                               @onSearchFormSubmit="onSearchFormSubmit" />

    <search-grid-form-new-filter v-if="renderNewFilter"
                                 v-bind="$attrs"
                                 @onSearchFormSubmit="onSearchFormSubmit" />
  </div>
</template>

<script>
import SearchGridFormNewFilter from '@/components/SearchGridFormNewFilter';
import SearchGridFormOriginal from '@/components/SearchGridFormOriginal';
import { ExperimentData as FilterButtonExperiment } from '@/abTests/filterButtonExperiment';

export default {
  name: 'search-grid-form',
  components: {
    SearchGridFormOriginal,
    SearchGridFormNewFilter,
  },
  props: {
    showProvidersFilter: {
      default: false,
    },
    searchBoxPlaceholder: {
      default: 'Search all images',
    },
  },
  computed: {
    renderOriginalFilter() {
      return this.$store.state.experiments.some(experiment =>
        experiment.name === FilterButtonExperiment.EXPERIMENT_NAME &&
        experiment.case === FilterButtonExperiment.ORIGINAL_FILTER_BUTTON_EXPERIMENT,
      );
    },
    renderNewFilter() {
      return this.$store.state.experiments.some(experiment =>
        experiment.name === FilterButtonExperiment.EXPERIMENT_NAME &&
        experiment.case === FilterButtonExperiment.FILTER_BUTTON_NEW_POSITION_EXPERIMENT,
      );
    },
  },
  methods: {
    onSearchFormSubmit(query) {
      this.$emit('onSearchFormSubmit', query);
    },
  },
};
</script>

<style lang="scss" scoped>
  .search-filter {
    position: absolute;
    top: 82px !important;
    left: auto !important;
    right: 0 !important;
    border: 1px solid #e8e8e8;
  }

  .search-form {
    width: 100%;
    background: #fff;
    border-bottom: 1px solid #E6EAEA;
  }

  .search-filter:after,
  .search-filter:before {
    bottom: 100%;
    right: 30px;
    border: solid transparent;
    content: " ";
    height: 0;
    width: 0;
    position: absolute;
    pointer-events: none;
  }

  .search-filter:after {
    border-color: rgba(255, 255, 255, 0);
    border-bottom-color: #fff;
    border-width: 8px;
    margin-left: -8px;
    z-index: 100;
  }

  .search-filter:before {
    border-color: rgba(232, 232, 232, 0);
    border-bottom-color: #e8e8e8;
    border-width: 10px;
    margin-left: 0px;
    right: 28px;
  }

  .search-form_search-button {

    .menu-button_text {
      color: #35495e;
    }
  }

  .search-form_filter-button {
    position: relative;

    .menu-button_text {
      color: #35495e;
    }
  }
  .search-form_ctr {
    position: relative;
  }

  .search-form_inner-ctr {
    height: inherit;
    display: flex;
  }

  .search-form_input {
    font-size: 24px;
    padding-left: 30px;
    margin-bottom: 0;
    width: 100%;
    height: 100%;
    outline: 0;
    border: none;
    box-shadow: none;

    &:focus {
      border: none;
    }
  }

  .search-form_toolbar {
    flex-wrap: nowrap;

    li {
      border-left: 1px solid #E6EAEA;
      border-right: 1px solid #E6EAEA;

      &:last-of-type {
        border-left: none;
      }
    }
  }

  @media screen and (max-width: 600px) {
    .search-form_input {
      font-size: 18px;
    }
  }
</style>
