<template>
  <div class="app flex min-h-screen flex-col">
    <div class="sticky top-0 z-40 block">
      <VTeleportTarget name="skip-to-content" :force-destroy="true" />
      <VMigrationNotice />
      <VTranslationStatusBanner />
      <VHeader v-if="isNewHeaderEnabled" />
      <VHeaderOld v-else />
    </div>

    <main
      class="main embedded w-screen flex-shrink-0 flex-grow md:w-full"
      :class="[
        { 'has-sidebar': isSidebarVisible },
        isNewHeaderEnabled ? 'new-layout' : 'old-layout',
      ]"
    >
      <div v-if="isNewHeaderEnabled">
        <Nuxt class="main-page min-w-0" />
        <VFooter class="border-t border-dark-charcoal-20" />
      </div>
      <Nuxt v-else class="main-page min-w-0" />

      <VSidebarTarget
        class="sidebar fixed z-10 overflow-y-auto bg-dark-charcoal-06 end-0"
        :class="{ 'border-dark-charcoal-20 border-s': isSidebarVisible }"
      />
    </main>

    <VModalTarget class="modal" />
    <VGlobalAudioSection />
  </div>
</template>
<script>
import { computed, provide, ref, watch } from '@nuxtjs/composition-api'
import { PortalTarget as VTeleportTarget } from 'portal-vue'

import { useWindowScroll } from '~/composables/use-window-scroll'
import { useMatchSearchRoutes } from '~/composables/use-match-routes'
import { isMinScreen } from '~/composables/use-media-query'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { useFeatureFlagStore } from '~/stores/feature-flag'

import { IsMinScreenLgKey, IsMinScreenMdKey } from '~/types/provides'

import VMigrationNotice from '~/components/VMigrationNotice.vue'
import VTranslationStatusBanner from '~/components/VTranslationStatusBanner.vue'
import VHeaderOld from '~/components/VHeaderOld/VHeaderOld.vue'
import VModalTarget from '~/components/VModal/VModalTarget.vue'
import VSidebarTarget from '~/components/VModal/VSidebarTarget.vue'
import VGlobalAudioSection from '~/components/VGlobalAudioSection/VGlobalAudioSection.vue'
import VFooter from '~/components/VFooter/VFooter.vue'

const embeddedPage = {
  name: 'embedded',
  components: {
    VMigrationNotice,
    VTranslationStatusBanner,
    VHeaderOld,
    VHeader: () => import('~/components/VHeader/VHeader.vue'),
    VFooter,
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
    const featureFlagStore = useFeatureFlagStore()
    const isNewHeaderEnabled = featureFlagStore.isOn('new_header')

    const { isVisible: isFilterVisible } = useFilterSidebarVisibility()
    const { matches: isSearchRoute } = useMatchSearchRoutes()

    const isMinScreenMd = isMinScreen('md')
    const isMinScreenLg = isMinScreen('lg')

    const isSidebarVisible = computed(() => {
      return isNewHeaderEnabled
        ? isSearchRoute.value && isMinScreenLg.value && isFilterVisible.value
        : isSearchRoute.value && isMinScreenMd.value && isFilterVisible.value
    })

    const isHeaderScrolled = ref(false)
    const { isScrolled: isMainContentScrolled, y: scrollY } = useWindowScroll()
    watch([isMainContentScrolled], ([isMainContentScrolled]) => {
      isHeaderScrolled.value = isMainContentScrolled
    })
    const showScrollButton = computed(() => scrollY.value > 70)

    provide('isHeaderScrolled', isHeaderScrolled)
    provide('showScrollButton', showScrollButton)
    // TODO: remove the untyped `isMinScreenMd` provide after the new header is enabled.
    provide('isMinScreenMd', isMinScreenMd)
    provide(IsMinScreenMdKey, isMinScreenMd)
    provide(IsMinScreenLgKey, isMinScreenLg)

    // TODO: remove `headerHasTwoRows` provide after the new header is enabled.
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
      isNewHeaderEnabled,
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

/* TODO: remove these styles when new header is enabled */
@screen md {
  /** Display the search filter sidebar and results as independently-scrolling. **/
  .main.old-layout {
    @apply grid h-full grid-cols-[1fr_var(--filter-sidebar-width)];
  }
  /** Make the main content area span both grid columns when the sidebar is closed... **/
  .main.old-layout > *:first-child {
    grid-column: span 2;
  }
  /** ...and only one column when it is visible. **/
  .main.old-layout.has-sidebar > *:first-child {
    grid-column: 1;
  }
}
/* TODO: remove the new-layout class when new header is enabled */
@screen lg {
  /** Display the search filter sidebar and results as independently-scrolling. **/
  .main.new-layout {
    @apply grid h-full grid-cols-[1fr_var(--filter-sidebar-width)];
  }
  /** Make the main content area span both grid columns when the sidebar is closed... **/
  .main.new-layout > *:first-child {
    grid-column: span 2;
  }
  /** ...and only one column when it is visible. **/
  .main.new-layout.has-sidebar > *:first-child {
    grid-column: 1;
  }
}
</style>
