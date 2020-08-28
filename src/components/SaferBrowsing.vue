<template>
  <div class="safer-browsing" @keyup.esc="closeShowForm">
    <button
      class="button is-text tiny is-paddingless rating is-shadowless"
      @click="toggleShowForm"
    >
      <span class="has-color-dark-turquoise"
        >{{ $t('browse-page.safer-browsing.title')
        }}<i class="icon flag margin-left-small" />
      </span>
    </button>
    <focus-trap :active="true">
      <div
        v-show="showForm"
        class="padding-normal is-clearfix arrow-popup arrow-popup--anchor-right"
      >
        <button
          class="button close-button is-text tiny is-pulled-right is-block has-text-grey-light"
          @click="toggleShowForm"
        >
          <i class="icon cross" />
        </button>
        <p class="caption has-text-weight-semibold padding-right-big">
          {{ $t('browse-page.safer-browsing.caption') }}
        </p>

        <label class="checkbox margin-top-small" for="mature">
          <input
            id="mature"
            class="filter-checkbox"
            type="checkbox"
            :checked="mature"
            @change="toggleMature"
            @keyup.enter="toggleMature"
          />
          {{ $t('browse-page.safer-browsing.label') }}
        </label>
      </div>
    </focus-trap>
  </div>
</template>

<script>
import { FocusTrap } from 'focus-trap-vue'
import { TOGGLE_FILTER } from '~/store-modules/action-types'

export default {
  name: 'SaferBrowsing',
  components: {
    FocusTrap,
  },
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
    closeShowForm() {
      this.showForm = false
    },
    toggleMature() {
      this.$store.dispatch(TOGGLE_FILTER, { filterType: 'mature' })
    },
  },
}
</script>

<style>
.safer-browsing {
  position: relative;
}

.safer-browsing > .button.tiny {
  font-size: 0.8rem;
}
</style>
