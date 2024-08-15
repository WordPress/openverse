<script lang="ts">
import { computed, defineComponent } from "vue"

import { defineEvent } from "~/types/emits"

import VButton from "~/components/VButton.vue"

/**
 * This button dismisses the open modal for changing content types or applying
 * filters and takes the user back to the results.
 */
export default defineComponent({
  name: "VShowResultsButton",
  components: { VButton },
  props: {
    /**
     * whether the results are being updated behind the open modal
     */
    isFetching: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    click: defineEvent(),
  },
  setup() {
    const diameter = 8 // px
    const spacing = 8 // px

    const radius = computed(() => diameter / 2)
    const width = computed(() => diameter * 3 + spacing * 2)

    return {
      diameter,
      spacing,
      radius,
      width,
    }
  },
})
</script>

<template>
  <VButton
    variant="filled-pink-8"
    size="large"
    class="label-bold relative ms-auto"
    @click="$emit('click')"
  >
    <!-- Loading animation -->
    <span
      v-if="isFetching"
      class="absolute inset-0 flex items-center justify-center"
    >
      <svg
        :viewBox="`0 0 ${width} ${diameter}`"
        :width="width"
        :height="diameter"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        fill="currentColor"
        class="loading motion-reduce:animate-pulse"
        :style="{ '--spacing': `${spacing}px`, '--diameter': `${diameter}px` }"
      >
        <circle
          v-for="idx in 3"
          :id="`dot-${idx}`"
          :key="idx"
          :r="radius"
          :cx="(idx - 1) * (spacing + diameter) + radius"
          cy="4"
        />
      </svg>
      <span class="sr-only">
        {{ $t("header.loading") }}
      </span>
    </span>

    <!-- To preserve the button width when state changes, this element is not
    removed from the DOM, only hidden and muted. -->
    <span :class="{ 'opacity-0': isFetching }" :aria-hidden="isFetching">
      {{ $t("header.seeResults") }}
    </span>
  </VButton>
</template>

<style>
/*
  Dot #2 becomes visible as soon as dot #3 as passed over it. This avoids the
  need to translate 2 dots and ensure that their movements are perfectly
  synchronised.
 */
@keyframes dot-2 {
  0%,
  49% {
    @apply opacity-0;
  }
  50%,
  100% {
    @apply opacity-100;
  }
}

/*
  Dot #3 is animated between 10% and 90% to simulate the pause in both the start
  and end state, before the animation loops itself.
 */
@keyframes dot-3 {
  0%,
  10% {
    transform: translateX(calc(-2 * (var(--spacing) + var(--diameter))));
  }
  90%,
  100% {
    @apply translate-x-0;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .loading #dot-2 {
    animation: dot-2 1s infinite ease-in-out alternate;
  }

  .loading #dot-3 {
    animation: dot-3 1s infinite ease-in-out alternate;
  }
}
</style>
