<script setup lang="ts">
import { computed, onMounted, useLocaleHead } from "#imports"

import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useLayout } from "~/composables/use-layout"

import VSkipToContentButton from "~/components/VSkipToContentButton.vue"

const { updateBreakpoint } = useLayout()

const featureFlagStore = useFeatureFlagStore()
const uiStore = useUiStore()

/* UI store */
const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
const breakpoint = computed(() => uiStore.breakpoint)

const head = useLocaleHead({
  addDirAttribute: true,
  identifierAttribute: "id",
  addSeoAttributes: true,
})

/**
 * Update the breakpoint value in the cookie on mounted.
 * The Pinia state might become different from the cookie state if, for example, the cookies were saved when the screen was `sm`,
 * and then a page is opened on SSR on a `lg` screen.
 */
onMounted(() => {
  updateBreakpoint()
  featureFlagStore.syncAnalyticsWithLocalStorage()
})
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
        <div :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]">
          <VSkipToContentButton />
          <NuxtLayout>
            <NuxtPage />
          </NuxtLayout>
          <VGlobalAudioSection />
        </div>
      </Body>
    </Html>
  </div>
</template>
