import { computed, watch } from '@nuxtjs/composition-api'

import { useUiStore } from '~/stores/ui'
import { useFeatureFlagStore } from '~/stores/feature-flag'
import { isMinScreen } from '~/composables/use-media-query'

/**
 * This composable updates the UI store when the screen width changes or
 * when the SSR layout settings are different from the cookie settings.
 *
 * The threshold for switching between mobile and desktop layout is
 * `lg` for the `new_header` and `md` for the `old_header`.
 */
export function useLayout() {
  const uiStore = useUiStore()
  const featureFlagStore = useFeatureFlagStore()

  const isNewHeaderEnabled = computed(() => featureFlagStore.isOn('new_header'))

  // `isMobile` is set in the middleware for each server request.
  const shouldPassInSSR = uiStore.isDesktopLayout
  const desktopBreakpoint = computed(() =>
    isNewHeaderEnabled.value ? 'lg' : 'md'
  )

  const isDesktopLayout = isMinScreen(desktopBreakpoint, { shouldPassInSSR })

  watch(isDesktopLayout, (isDesktop) => {
    updateLayout(isDesktop)
  })

  const updateLayout = (isDesktop: boolean) => {
    if (isDesktop !== uiStore.isDesktopLayout) {
      uiStore.updateBreakpoint(isDesktop)
    }
  }

  return {
    isDesktopLayout,
    updateLayout,
  }
}
