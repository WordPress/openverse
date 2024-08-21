<script setup lang="ts">
import { useElementSize } from "@vueuse/core"
import { computed, ref, watch } from "vue"

import { useUiStore } from "~/stores/ui"

import VBanners from "~/components/VBanner/VBanners.vue"
import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"
import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"
import VHeaderMobile from "~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"

const props = withDefaults(
  defineProps<{
    showBottomBorder?: boolean
    kind: "internal" | "search-desktop" | "search-mobile"
    color?: "default" | "complementary"
  }>(),
  {
    showBottomBorder: false,
    color: "default",
  }
)

const headerRef = ref<HTMLElement | null>(null)
const uiStore = useUiStore()
const { height } = useElementSize(headerRef)
watch(height, (height) => {
  uiStore.setHeaderHeight(height)
})

const headerComponent = computed(() => {
  return {
    internal: VHeaderInternal,
    "search-desktop": VHeaderDesktop,
    "search-mobile": VHeaderMobile,
  }[props.kind]
})

const bg = computed(() => `bg-${props.color}`)
</script>

<template>
  <div ref="headerRef" class="header-el" :class="bg">
    <VBanners />
    <component
      :is="headerComponent"
      class="h-20 border-b"
      :class="[showBottomBorder ? 'border-b-default' : 'border-b-tx', bg]"
    />
  </div>
</template>
