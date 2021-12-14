<template>
  <div class="relative" @keyup.esc="closeShowForm">
    <button
      type="button"
      class="appearance-none px-0 leading-10 text-xs text-trans-blue font-semibold"
      style="white-space: nowrap"
      @click="toggleShowForm"
    >
      {{ $t('browse-page.safer-browsing.title') }}
    </button>
    <FocusTrap :active="showForm">
      <div v-show="showForm" class="p-4 arrow-popup arrow-popup--anchor-right">
        <button
          class="button close-button is-text tiny float-right block text-light-gray"
          type="button"
          @click="toggleShowForm"
        >
          <i class="icon cross" />
        </button>
        <p class="caption font-semibold pe-6">
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
import { TOGGLE_FILTER } from '~/constants/action-types'
import { mapActions } from 'vuex'
import { SEARCH } from '~/constants/store-modules'

export default {
  name: 'VSaferBrowsing',
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
      return this.$store.state.search.filters.mature
    },
  },
  methods: {
    ...mapActions(SEARCH, { toggleFilter: TOGGLE_FILTER }),
    toggleShowForm() {
      this.showForm = !this.showForm
    },
    closeShowForm() {
      this.showForm = false
    },
    toggleMature() {
      this.toggleFilter({ filterType: 'mature' })
    },
  },
}
</script>
