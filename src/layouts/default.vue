<template>
  <div class="app grid h-screen overflow-hidden relative">
    <div>
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VMigrationNotice v-show="isReferredFromCc" />
      <VTranslationStatusBanner />
      <VHeader />
    </div>
    <main
      class="main embedded overflow-x-hidden"
      :class="{ 'has-sidebar': isSidebarVisible }"
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
import { useMatchSearchRoutes } from '~/composables/use-match-routes'
import { useScroll } from '~/composables/use-scroll'

import VMigrationNotice from '~/components/VMigrationNotice.vue'
import VTranslationStatusBanner from '~/components/VTranslationStatusBanner.vue'
import VHeader from '~/components/VHeader/VHeader.vue'
import VModalTarget from '~/components/VModal/VModalTarget.vue'
import VSidebarTarget from '~/components/VModal/VSidebarTarget.vue'
import VGlobalAudioSection from '~/components/VGlobalAudioSection/VGlobalAudioSection.vue'
import VTeleportTarget from '~/components/VTeleport/VTeleportTarget.vue'

const embeddedPage = {
  name: 'embedded',
  components: {
    VMigrationNotice,
    VTranslationStatusBanner,
    VHeader,
    VModalTarget,
    VTeleportTarget,
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

    const headerHasTwoRows = computed(
      () =>
        isSearchRoute.value && !isHeaderScrolled.value && !isMinScreenMd.value
    )
    provide('headerHasTwoRows', headerHasTwoRows)
    return {
      isHeaderScrolled,
      isMinScreenMd,
      isReferredFromCc,
      isSidebarVisible,
      isSearchRoute,
      headerHasTwoRows,
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

@screen md {
  // Logic for displaying the filter sidebar and search results
  // as independently-scrolling sections.
  .main {
    height: 100%;
    display: grid;
    grid-template-columns: 1fr 316px;
  }
  // Make the main content area span both grid columns
  // when the sidebar is closed...
  .main > *:first-child {
    grid-column: span 2;
  }
  // ...and only one column when it is visible.
  .main.has-sidebar > *:first-child {
    grid-column: 1;
  }
}

.main {
  overflow: hidden;
}
.main > *:not(:empty) {
  overflow-y: scroll;
  height: 100%;
}
</style>
