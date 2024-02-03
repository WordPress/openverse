<template>
  <div :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]">
    <VSkipToContentButton />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <VGlobalAudioSection />
  </div>
  <div id="modal"></div>
</template>

<script setup lang="ts">
import { computed, onMounted, useRoute, useCookie } from "#imports"

import { useUiStore } from "~/stores/ui"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useLayout } from "~/composables/use-layout"
import type { OpenverseCookieState } from "~/types/cookies"

import VSkipToContentButton from "~/components/VSkipToContentButton.vue"

/**
 * Lifecycle hooks in async setup should be called before the first await.
 */
const { updateBreakpoint } = useLayout()

const route = useRoute()
const uiStore = useUiStore()

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
const featureCookies = useCookie<OpenverseCookieState["features"]>("features")
featureFlagStore.initFromCookies(featureCookies.value ?? {})
const sessionFeatures =
  useCookie<OpenverseCookieState["sessionFeatures"]>("sessionFeatures")
featureFlagStore.initFromCookies(sessionFeatures.value ?? {})
featureFlagStore.initFromQuery(route.query)

/* UI store */
const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
uiStore.initFromCookies(uiCookies.value ?? {})

const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
const breakpoint = computed(() => uiStore.breakpoint)
</script>
