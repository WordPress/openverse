<template>
  <div class="app relative grid">
    <div class="sticky top-0 z-40 block">
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VMigrationNotice />
      <VTranslationStatusBanner />
      <VHeader />
    </div>
    <main
      class="main embedded w-screen md:w-full"
      :class="{ 'has-sidebar': isSidebarVisible }"
    >
      <Nuxt class="main-page min-w-0" />
      <VSidebarTarget
        class="sidebar fixed overflow-y-auto bg-dark-charcoal-06 end-0"
        :class="{ 'border-dark-charcoal-20 border-s': isSidebarVisible }"
      />
    </main>
    <VModalTarget class="modal" />
    <VGlobalAudioSection />
  </div>
</template>
<script>
import { computed, provide, ref, watch } from '@nuxtjs/composition-api'

import { useWindowScroll } from '~/composables/use-window-scroll'
import { useMatchSearchRoutes } from '~/composables/use-match-routes'
import { isMinScreen } from '~/composables/use-media-query'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

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
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  setup() {
    const { isVisible: isFilterVisible } = useFilterSidebarVisibility()
    const isMinScreenMd = isMinScreen('md')
    const { matches: isSearchRoute } = useMatchSearchRoutes()

    const isSidebarVisible = computed(
      () => isSearchRoute.value && isMinScreenMd.value && isFilterVisible.value
    )

    const isHeaderScrolled = ref(false)
    const { isScrolled: isMainContentScrolled, y: scrollY } = useWindowScroll()
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
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
      isSidebarVisible,
      isSearchRoute,
      headerHasTwoRows,
    }
  },
}
export default embeddedPage
</script>

<style scoped>
.sidebar {
  /* Header height above md is 80px plus 1px for bottom border */
  height: calc(100vh - 81px);
}
.has-sidebar .sidebar {
  width: var(--filter-sidebar-width);
}

.app {
  grid-template-rows: auto 1fr;
}

@screen md {
  /** Display the search filter sidebar and results as independently-scrolling. **/
  .main {
    height: 100%;
    display: grid;
    grid-template-columns: 1fr var(--filter-sidebar-width);
  }
  /** Make the main content area span both grid columns when the sidebar is closed... **/
  .main > *:first-child {
    grid-column: span 2;
  }
  /** ...and only one column when it is visible. **/
  .main.has-sidebar > *:first-child {
    grid-column: 1;
  }
}
</style>
