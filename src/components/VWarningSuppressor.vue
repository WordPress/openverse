<template>
  <div v-on="$listeners">
    <slot />
  </div>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

/**
 * A `div` replacement component useful for suppressing warnings
 * about `.native` modifiers on non-components.
 */
export default defineComponent({
  name: 'VWarningSuppressor',
})
</script>
