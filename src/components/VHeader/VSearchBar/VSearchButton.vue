<template>
  <div>
    <VButton
      v-if="isHomeRoute && isMinScreenMd"
      v-bind="$attrs"
      :aria-label="$t('search.search')"
      class="inline-block cta-search-button font-semibold h-full text-2xl"
      v-on="$listeners"
      >{{ $t('search.search') }}</VButton
    >
    <VIconButton
      v-else
      v-bind="$attrs"
      :size="`search-${size}`"
      class="search-button hover:text-white group-hover:text-white hover:bg-pink group-hover:bg-pink p-0.5px ps-1.5px focus:p-0 border hover:border-pink group-hover:border-pink rounded-e-sm active:shadow-ring"
      :class="[
        isHomeRoute
          ? 'bg-pink text-white border-tx'
          : 'border-dark-charcoal-20',
      ]"
      :icon-props="{ iconPath: searchIcon }"
      :aria-label="$t('search.search')"
      v-on="$listeners"
    />
  </div>
</template>

<script>
import { isMinScreen } from '~/composables/use-media-query'

import VIconButton from '~/components/VIconButton/VIconButton.vue'

import searchIcon from '~/assets/icons/search.svg'

export default {
  name: 'VSearchButton',
  components: { VIconButton },
  inheritAttrs: false,
  props: {
    size: {
      type: String,
      required: true,
      validator: (v) => ['small', 'medium', 'large', 'standalone'].includes(v),
    },
    isHomeRoute: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    return { isMinScreenMd, searchIcon }
  },
}
</script>

<style scoped>
.cta-search-button {
  @apply py-6 px-10 rounded-s-none border-b border-b-pink;
}

/* @todo: Find a better way to override the VIconButton border styles */
.search-button {
  /* Negative margin removes a tiny gap between the button and the input borders */
  margin-inline-start: -1px;
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:not(:hover):not(:focus):not(:focus-within) {
  border-inline-start-color: transparent;
  border-width: 1px;
}
.search-button.search-button:hover {
  border-inline-start-color: rgba(214, 212, 213, 1);
  border-width: 1px;
}
</style>
