<script setup lang="ts">
import {
  onMounted,
  useHead,
  useLocaleHead,
  useRoute,
  useRuntimeConfig,
} from "#imports"

import { meta as commonMeta } from "#shared/constants/meta"
import { favicons } from "#shared/constants/favicons"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useDarkMode } from "~/composables/use-dark-mode"
import { useLayout } from "~/composables/use-layout"

import VFourOhFour from "~/components/VFourOhFour.vue"

defineProps(["error"])

const route = useRoute()
const { updateBreakpoint } = useLayout()
const config = useRuntimeConfig()

/**
 * Update the breakpoint value in the cookie on mounted.
 * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
 * and then a page is opened on SSR on a `lg` screen.
 */
onMounted(() => {
  updateBreakpoint()
  featureFlagStore.syncAnalyticsWithLocalStorage()
})

/* Feature flag store */

const featureFlagStore = useFeatureFlagStore()
featureFlagStore.initFromQuery(route.query)

const darkMode = useDarkMode()
const head = useLocaleHead({ dir: true, key: "id", seo: true })

useHead({
  bodyAttrs: { class: darkMode.cssClass },
  title: "Openly Licensed Images, Audio and More | Openverse",
  meta: commonMeta,
  link: [
    ...favicons,
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
  ],
})
</script>

<template>
  <div>
    <Html :lang="head.htmlAttrs?.lang" :dir="head.htmlAttrs?.dir">
      <Head>
        <template v-for="link in head.link" :key="link.id">
          <Link
            :id="link.id"
            :rel="link.rel"
            :href="link.href"
            :hreflang="link.hreflang"
          />
        </template>
        <template v-for="meta in head.meta" :key="meta.id">
          <Meta
            :id="meta.id"
            :property="meta.property"
            :content="meta.content"
          />
        </template>
      </Head>
      <Body>
        <VSkipToContentButton />
        <NuxtLayout name="default">
          <VFourOhFour class="flex-grow" :error="error" />
        </NuxtLayout>
      </Body>
    </Html>
  </div>
</template>

<style>
body {
  /* This is used by some elements. */
  --color-bg-curr-page: var(--color-bg-complementary);
}
</style>
