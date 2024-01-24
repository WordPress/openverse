<template>
  <div>
    <Html :lang="head.htmlAttrs?.lang" :dir="head.htmlAttrs?.dir">
      <VSkipToContentButton />
      <NuxtLayout name="default">
        <VFourOhFour class="flex-grow" :error="error" />
      </NuxtLayout>
      <div id="modal"></div>
    </Html>
  </div>
</template>

<script setup lang="ts">
import {
  onMounted,
  useCookie,
  useFeatureFlagStore,
  useLocaleHead,
  useRoute,
  useUiStore,
} from "#imports"

import { useLayout } from "~/composables/use-layout"
import type { OpenverseCookieState } from "~/types/cookies"

import VFourOhFour from "~/components/VFourOhFour.vue"

defineProps(["error"])

const { updateBreakpoint } = useLayout()

const route = useRoute()
const uiStore = useUiStore()

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
</script>
