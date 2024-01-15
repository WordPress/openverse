import { nextTick, onMounted, ref } from "vue"

/**
 * Composable used to set interactive elements disabled until the hydration is done.
 * @see https://playwright.dev/docs/navigations#hydration
 */
export const useHydrating = () => {
  const doneHydrating = ref(false)
  onMounted(() => {
    nextTick().then(() => {
      doneHydrating.value = true
    })
  })

  return {
    doneHydrating,
  }
}
