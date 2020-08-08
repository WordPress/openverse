<template>
  <div class="safe-browsing">
    <button
      class="button is-text tiny is-paddingless rating is-shadowless"
      @click="toggleShowForm"
      v-on:keyup.enter="toggleShowForm"
    >
      <span class="has-color-dark-turquoise"
        >{{ $t('browse-page.safe-browsing.title')
        }}<i class="icon flag margin-left-small"></i>
      </span>
    </button>

    <div
      v-show="showForm"
      class="padding-normal is-clearfix arrow-popup arrow-popup--anchor-right"
    >
      <button
        class="button close-button is-text tiny is-pulled-right is-block has-text-grey-light"
        @click="toggleShowForm"
        v-on:keyup.enter="toggleShowForm"
      >
        <i class="icon cross"></i>
      </button>
      <p class="caption has-text-weight-semibold padding-right-big">
        {{ $t('browse-page.safe-browsing.caption') }}
      </p>

      <label class="checkbox margin-top-small" for="mature">
        <input
          id="mature"
          class="filter-checkbox"
          type="checkbox"
          :checked="mature"
          @change="toggleMature"
        />
        {{ $t('browse-page.safe-browsing.label') }}
      </label>
    </div>
  </div>
</template>

<script>
import { TOGGLE_FILTER } from '@/store/action-types'

/**
 * This component displays the mature content filter in a pop-up dialog.
 */
export default {
  name: 'safe-browsing',
  data() {
    return {
      showForm: false,
    }
  },
  computed: {
    mature() {
      return this.$store.state.filters.mature
    },
  },
  methods: {
    toggleShowForm() {
      this.showForm = !this.showForm
    },
    toggleMature() {
      this.$store.dispatch(TOGGLE_FILTER, {
        filterType: 'mature',
        shouldNavigate: true,
      })
    },
  },
}
</script>

<style>
.safe-browsing {
  position: relative;
}

.safe-browsing > .button.tiny {
  font-size: 0.8rem;
}
</style>
