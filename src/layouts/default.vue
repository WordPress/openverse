<template>
  <div class="app grid h-screen overflow-hidden">
    <MigrationNotice v-show="isReferredFromCc" />
    <TranslationStatusBanner />
    <VHeader v-if="!isHomeRoute" />
    <main
      class="main embedded overflow-x-hidden"
      :class="{
        'has-sidebar': isSidebarVisible,
      }"
    >
      <Nuxt ref="mainContentRef" class="min-w-0 main-page" />
      <VSidebarTarget class="sidebar" />
    </main>
    <VModalTarget class="modal" />
    <VGlobalAudioSection />
  </div>
</template>
<script>
import iframeHeight from '~/mixins/iframe-height'

import { NAV } from '~/constants/store-modules'
import {
  computed,
  provide,
  ref,
  useContext,
  watch,
} from '@nuxtjs/composition-api'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { isMinScreen } from '~/composables/use-media-query'
import {
  useMatchHomeRoute,
  useMatchSearchRoutes,
} from '~/composables/use-match-routes'
import { useScroll } from '~/composables/use-scroll'

import MigrationNotice from '~/components/MigrationNotice.vue'
import TranslationStatusBanner from '~/components/TranslationStatusBanner.vue'
import VHeader from '~/components/VHeader/VHeader.vue'
import VModalTarget from '~/components/VModal/VModalTarget.vue'
import VSidebarTarget from '~/components/VModal/VSidebarTarget.vue'
import VGlobalAudioSection from '~/components/VGlobalAudioSection/VGlobalAudioSection.vue'

const embeddedPage = {
  name: 'embedded',
  components: {
    MigrationNotice,
    TranslationStatusBanner,
    VHeader,
    VModalTarget,
    VSidebarTarget,
    VGlobalAudioSection,
  },
  layout: 'embedded',
  mixins: [iframeHeight],
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  setup() {
    const mainContentRef = ref(null)
    const mainRef = ref(null)
    const { store } = useContext()
    const isReferredFromCc = store.state[NAV].isReferredFromCc

    const { isVisible: isFilterVisible } = useFilterSidebarVisibility()
    const isMinScreenMd = isMinScreen('md')
    const { matches: isSearchRoute } = useMatchSearchRoutes()
    const { matches: isHomeRoute } = useMatchHomeRoute()

    const isSidebarVisible = computed(
      () => isSearchRoute.value && isMinScreenMd.value && isFilterVisible.value
    )

    const isHeaderScrolled = ref(false)
    const scrollY = ref(0)
    const { isScrolled: isMainContentScrolled, y: mainContentY } =
      useScroll(mainContentRef)
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
    })
    watch([mainContentY], ([mainContentY]) => {
      scrollY.value = mainContentY
    })
    const showScrollButton = computed(() => scrollY.value > 70)

    provide('isHeaderScrolled', isHeaderScrolled)
    provide('showScrollButton', showScrollButton)

    return {
      isHeaderScrolled,
      isMinScreenMd,
      isReferredFromCc,
      isSidebarVisible,
      isSearchRoute,
      isHomeRoute,
      mainContentRef,
      mainRef,
    }
  },
}
export default embeddedPage
</script>
<style lang="scss" scoped>
.app {
  grid-template-rows: auto 1fr;
}

.main {
  display: grid;
  grid-template-columns: 1fr 316px;
  height: 100%;
  overflow: hidden;
}

.main > * {
  overflow-y: scroll;
  min-height: 100%;
}

.main > *:first-child {
  grid-column: span 2;
}

.main.has-sidebar > *:first-child {
  grid-column: 1;
}
</style>
