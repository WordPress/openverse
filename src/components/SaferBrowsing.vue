<template>
  <div class="safer-browsing" @keyup.esc="closeShowForm">
    <button
      class="button is-text tiny p-0 rating"
      @keypress.enter="toggleShowForm"
      @click="toggleShowForm"
    >
      <span class="text-trans-blue" style="white-space: nowrap">
        {{ $t('browse-page.safer-browsing.title') }}
        <i class="icon flag ml-2" />
      </span>
    </button>
    <FocusTrap :active="true">
      <div v-show="showForm" class="p-4 arrow-popup arrow-popup--anchor-right">
        <button
          class="button close-button is-text tiny float-right block text-light-gray"
          @keypress.enter="toggleShowForm"
          @click="toggleShowForm"
        >
          <i class="icon cross" />
        </button>
        <p class="caption font-semibold pr-6">
          {{ $t('browse-page.safer-browsing.caption') }}
        </p>

        <label class="checkbox mt-2" for="mature">
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
    </FocusTrap>
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
