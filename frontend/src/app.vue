<script setup lang="ts">
import {
  computed,
  onMounted,
  useHead,
  useLocaleHead,
  useRuntimeConfig,
} from "#imports"

import { meta as commonMeta } from "#shared/constants/meta"
import { favicons } from "#shared/constants/favicons"
import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useLayout } from "~/composables/use-layout"
import { useDarkMode } from "~/composables/use-dark-mode"

import VSkipToContentButton from "~/components/VSkipToContentButton.vue"

const config = useRuntimeConfig()

const featureFlagStore = useFeatureFlagStore()
const uiStore = useUiStore()

const darkMode = useDarkMode()

/* UI store */
const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
const breakpoint = computed(() => uiStore.breakpoint)
const headerHeight = computed(() => {
  return `--header-height: ${uiStore.headerHeight}px`
})

const head = useLocaleHead({ dir: true, key: "id", seo: true })
const htmlI18nProps = computed(() => ({
  lang: head.value?.htmlAttrs?.lang ?? "en",
  dir: head.value?.htmlAttrs?.dir ?? "ltr",
}))
const link = computed(() => {
  return [
    ...favicons,
    ...(head.value.link ?? []),
    {
      rel: "search",
      type: "application/opensearchdescription+xml",
      title: "Openverse",
      href: "/opensearch.xml",
    },
    {
      rel: "dns-prefetch",
      href: config.public.apiUrl,
    },
    {
      rel: "preconnect",
      href: config.public.apiUrl,
      crossorigin: "",
    },
  ]
})

const meta = computed(() => {
  return [...commonMeta, ...(head.value.meta ?? [])]
})

useHead({
  htmlAttrs: htmlI18nProps,
  bodyAttrs: { class: darkMode.cssClass, style: headerHeight },
  title: "Openly Licensed Images, Audio and More | Openverse",
  meta,
  link,
})

/**
 * Update the breakpoint value in the cookie on mounted.
 * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
 * and then a page is opened on SSR on a `lg` screen.
 */
onMounted(() => {
  const { updateBreakpoint } = useLayout()
  updateBreakpoint()
  featureFlagStore.syncAnalyticsWithLocalStorage()
})
</script>

<template>
  <div :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]">
    <VSkipToContentButton />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <VGlobalAudioSection />
  </div>
</template>
