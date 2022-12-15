import {
  useContext,
  ref,
  useRoute,
  useRouter,
  Ref,
} from "@nuxtjs/composition-api"

import { ALL_MEDIA, searchTypes, supportedSearchTypes } from "~/constants/media"

/**
 * Reactive property that returns true only on the matching routes.
 * Note that routes are matched by name, not the url path.
 *
 * Routes are also localized before comparison, so 'search' becomes
 * 'search__en', for example.
 *
 */
export const useMatchRoute = (
  routes: string[] = []
): { matches: Ref<boolean> } => {
  const { app } = useContext()
  const route = useRoute()
  const router = useRouter()

  const localizedRoutes = routes.map(
    (route) => app.localeRoute({ name: route })?.name
  )
  const matches = ref(localizedRoutes.includes(route.value.name))

  router.beforeEach((to, _from, next) => {
    matches.value = localizedRoutes.includes(to.name)
    next()
  })

  return { matches }
}

/**
 * Reactive property that returns true only on the `search` routes.
 * Homepage, single image result and other content pages return `false`
 */
export const useMatchSearchRoutes = () => {
  const routes = [
    "search",
    ...searchTypes
      .filter((type) => type !== ALL_MEDIA)
      .map((type) => `search-${type}`),
  ]
  return useMatchRoute(routes)
}

/**
 * Reactive property that returns true only on the `search` routes.
 * Homepage, single image result and other content pages return `false`
 */
export const useMatchSingleResultRoutes = () => {
  const routes = [
    ...supportedSearchTypes
      .filter((name) => name !== ALL_MEDIA)
      .map((name) => `${name}-id`),
  ]
  return useMatchRoute(routes)
}

export const useMatchHomeRoute = () => useMatchRoute(["index"])
