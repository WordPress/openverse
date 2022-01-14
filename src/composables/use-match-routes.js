import { ref, useRoute, useRouter } from '@nuxtjs/composition-api'

/**
 * Reactive property that returns true only on the matching routes.
 * Note that routes are matched by name, not the url path.
 *
 * @returns {{matches: import('@nuxtjs/composition-api').Ref<boolean>}}
 */
export const useMatchRoute = (routes = []) => {
  const route = useRoute()
  const router = useRouter()
  const matches = ref(routes.includes(route.value.name))
  router.beforeEach((to, from, next) => {
    matches.value = routes.includes(to.name)
    next()
  })
  return { matches }
}

/**
 * Reactive property that returns true only on the `search` routes.
 * Homepage, single image result and other content pages return `false`
 */
export const useMatchSearchRoutes = () =>
  useMatchRoute(['search', 'search-image', 'search-audio', 'search-video'])

export const useMatchHomeRoute = () => useMatchRoute(['index'])
