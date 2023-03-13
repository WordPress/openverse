<template>
  <VIcon v-if="showIcon" :icon-path="filterIcon" />
  <p
    v-else
    class="flex h-6 w-6 items-center justify-center rounded-sm"
    :class="pressed ? 'bg-tx' : 'bg-dark-charcoal-10'"
  >
    {{ appliedFilterCount }}
  </p>
</template>
<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api"

import VIcon from "~/components/VIcon/VIcon.vue"

import filterIcon from "~/assets/icons/filter.svg"

export default defineComponent({
  name: "VFilterIconOrCounter",
  components: { VIcon },
  props: {
    appliedFilterCount: {
      type: Number,
      default: 0,
    },
    pressed: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const showIcon = computed(() => props.appliedFilterCount === 0)

    return {
      showIcon,
      filterIcon,
    }
  },
})
</script>
