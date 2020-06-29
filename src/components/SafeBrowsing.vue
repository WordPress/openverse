<template>
  <div class="safe-browsing">
    <button
      class="button is-text tiny is-paddingless rating is-shadowless"
      @click="toggleShowForm"
    >
      <span class="has-color-dark-turquoise"
        >Safe Browsing<i class="icon flag margin-left-small"></i>
      </span>
    </button>

    <div
      v-show="showForm"
      class="padding-normal is-clearfix arrow-popup arrow-popup--anchor-right"
    >
      <button
        class="button close-button is-text tiny is-pulled-right is-block has-text-grey-light"
        @click="toggleShowForm"
      >
        <i class="icon cross"></i>
      </button>
      <p class="caption has-text-weight-semibold padding-right-big">
        By default, search results will not include results that have been
        reported as mature by users and sources.
      </p>

      <label class="checkbox margin-top-small" for="mature">
        <input
          id="mature"
          class="filter-checkbox"
          type="checkbox"
          :value="mature"
          @change="toggleMature"
        />
        Show Mature Content
      </label>
    </div>
  </div>
</template>

<script>
import { TOGGLE_FILTER } from '@/store/action-types';

/**
 * This component displays the mature content filter in a pop-up dialog.
 */
export default {
  name: 'safe-browsing',
  data() {
    return {
      showForm: false,
    };
  },
  computed: {
    mature() {
      return this.$store.state.filters.mature;
    },
  },
  methods: {
    toggleShowForm() {
      this.showForm = !this.showForm;
    },
    toggleMature() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'mature',
        shouldNavigate: true,
      });
    },
  },
};
</script>

<style>
.safe-browsing {
  position: relative;
}

.safe-browsing > .button.tiny {
  font-size: 0.8rem;
}
</style>
