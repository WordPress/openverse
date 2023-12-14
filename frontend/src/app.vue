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
        <div :class="[isDesktopLayout ? 'desktop' : 'mobile', breakpoint]">
          <VSkipToContentButton />
          <NuxtLayout>
            <NuxtPage />
          </NuxtLayout>
          <div id="modal" />
        </div>
      </Body>
    </Html>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  useRoute,
  useCookie,
  useLocaleHead,
  useNuxtApp,
} from "#imports"

import { useUiStore } from "~/stores/ui"
import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useLayout } from "~/composables/use-layout"
import type { OpenverseCookieState } from "~/types/cookies"

import VSkipToContentButton from "~/components/VSkipToContentButton.vue"

export default defineComponent({
  name: "App",
  components: {
    VSkipToContentButton,
  },
  async setup() {
    /**
     * Lifecycle hooks in async setup should be called before the first await.
     */
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
    const featureCookies =
      useCookie<OpenverseCookieState["features"]>("features")
    featureFlagStore.initFromCookies(featureCookies.value ?? {})
    const sessionFeatures =
      useCookie<OpenverseCookieState["sessionFeatures"]>("sessionFeatures")
    featureFlagStore.initFromCookies(sessionFeatures.value ?? {})
    featureFlagStore.initFromQuery(route.query)

    /* UI store */
    const { $ua } = useNuxtApp()
    const isMobileUa = $ua ? $ua.isMobile : false

    const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
    const uiCookiesValue = { ...(uiCookies.value ?? {}), isMobileUa }
    uiStore.initFromCookies(uiCookiesValue)

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const breakpoint = computed(() => uiStore.breakpoint)

    /* Provider store */
    const providerStore = useProviderStore()
    await providerStore.fetchMediaProviders()

    return {
      isDesktopLayout,
      breakpoint,
      head,
    }
  },
})
</script>
