<script setup lang="ts">
import { useHead, useLocaleHead, useRuntimeConfig } from "#imports"
import { computed, onMounted } from "vue"

import { meta as commonMeta } from "#shared/constants/meta"
import { favicons } from "#shared/constants/favicons"
import { useUiStore } from "~/stores/ui"
import { useDarkMode } from "~/composables/use-dark-mode"
import { useLayout } from "~/composables/use-layout"

import VFourOhFour from "~/components/VFourOhFour.vue"

defineProps(["error"])

const config = useRuntimeConfig()
const uiStore = useUiStore()

const headerHeight = computed(() => {
  return `--header-height: ${uiStore.headerHeight}px`
})

/**
 * Update the breakpoint value in the cookie on mounted.
 * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
 * and then a page is opened on SSR on a `lg` screen.
 */
onMounted(() => {
  const { updateBreakpoint } = useLayout()
  updateBreakpoint()
})

const darkMode = useDarkMode()

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
</script>

<template>
  <div>
    <VSkipToContentButton />
    <NuxtLayout name="default">
      <VFourOhFour class="flex-grow" :error="error" />
    </NuxtLayout>
  </div>
</template>

<style>
body {
  /* This is used by some elements. */
  --color-bg-curr-page: var(--color-bg-complementary);
}
</style>
