import { getElements } from "#imports"

import { computed, onMounted, ref, watch } from "vue"

import type { License } from "~/constants/license"
import { useDarkMode } from "~/composables/use-dark-mode"

/**
 * Generate the names for `VIcon` components based on the license and color mode.
 * The value is updated on mounted and when the color mode changes.
 *
 * This is necessary to prevent client-server mismatch: the server does not have access
 * to media queries, so the `system` color mode always defaults to "light".
 * @param license - the license to generate icons for
 * @param filterOutCc - whether to filter out the `cc` from the list of icons
 */
export const useIconNames = ({
  license,
  filterOutCc,
}: {
  license: License
  filterOutCc: boolean
}) => {
  const getIconNames = (elements: string[], colorMode: "dark" | "light") => {
    return elements.map((element) => `licenses/${element}-${colorMode}`)
  }
  const { effectiveColorMode, serverColorMode } = useDarkMode()

  const icons = computed(() => {
    const elements = getElements(license)
    return filterOutCc
      ? elements.filter((element) => element !== "cc")
      : elements
  })

  const iconNames = ref(getIconNames(icons.value, serverColorMode.value))

  onMounted(() => {
    watch(
      effectiveColorMode,
      () => {
        iconNames.value = getIconNames(icons.value, effectiveColorMode.value)
      },
      { immediate: true }
    )
  })

  return { iconNames }
}
