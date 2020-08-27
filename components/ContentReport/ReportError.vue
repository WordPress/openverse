<template>
  <div>
    <span
      class="is-block padding-horizontal-big margin-top-large has-text-centered"
    >
      {{ $t('photo-details.content-report.dmca.error') }}
    </span>
    <button
      class="button is-text tiny margin-top-normal is-shadowless"
      @click="onBackClick()"
      v-on:keyup.enter="onBackClick()"
    >
      <span>
        <i class="icon chevron-left margin-right-small"></i>
        {{ $t('photo-details.content-report.back') }}
      </span>
    </button>
  </div>
</template>

<script>
import { BACK_TO_REPORT_START } from '../../src/store/mutation-types'

export default {
  name: 'report-error',
  methods: {
    onBackClick() {
      this.$store.commit(BACK_TO_REPORT_START)
    },
  },
}
</script>
