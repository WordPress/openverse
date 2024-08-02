<script setup lang="ts">
import {
  onMounted,
  useFeatureFlagStore,
  useLocaleHead,
  useRoute,
} from "#imports"

import { useLayout } from "~/composables/use-layout"

import VFourOhFour from "~/components/VFourOhFour.vue"

defineProps(["error"])

const head = useLocaleHead({
  addDirAttribute: true,
  identifierAttribute: "id",
  addSeoAttributes: true,
})

const { updateBreakpoint } = useLayout()

const route = useRoute()

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
</script>

<template>
  <div>
    <Html :lang="head.htmlAttrs.lang" :dir="head.htmlAttrs.dir">
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
        <div id="modal"></div>
      </Body>
    </Html>
  </div>
</template>
