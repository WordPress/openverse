import { useRoute, useRouter } from "#imports"

import { ref, Ref } from "vue"

import { ALL_MEDIA, searchTypes, supportedSearchTypes } from "~/constants/media"
import usePages from "~/composables/use-pages"

/**
 * Reactive property that returns true only on the matching routes.
 * Note that routes are matched by their non-localized name.
 *
 */
export const useMatchRoute = (
  routes: string[] = []
): { matches: Ref<boolean> } => {
  const route = useRoute()
  const router = useRouter()

  /**
   * The route name is localized, so it includes the locale code after `__`.
   * We remove the locale from the route name to match it with the
   * non-localized routes array.
   *
   * @param route - the localized route name (e.g. `search__en`)
   */
  const routeNameMatches = (route: string | null | undefined) => {
    if (!route) {
      return false
    }
    return routes.includes(route.split("__")[0])
  }

  const matches = ref(routeNameMatches(String(route?.name)))

  router.beforeEach((to, _from, next) => {
    matches.value = routeNameMatches(String(to.name))
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
 * Reactive property that returns true only on the `single result` and `full-page report` routes.
 * Homepage, search results and other content pages return `false`
 */
export const useMatchSingleResultRoutes = () => {
  const routes = [
    ...supportedSearchTypes
      .filter((name) => name !== ALL_MEDIA)
      .map((name) => `${name}-id`),
  ]
  // @TODO Switch to more generic implementation once
  // an Audio reporting page is designed.
  //
  // routes = routes.concat(routes.map((name) => `${name}-report`))
  routes.push("image-id-report")

  return useMatchRoute(routes)
}

/**
 * Reactive property that returns true only on the 'content' routes:
 * about, search help, etc. and the preferences page.
 */
export const useMatchContentPageRoutes = () => {
  const routes = usePages()
    .all.filter((page) => page.link.startsWith("/"))
    .map((page) => page.id)
  routes.push("preferences")
  return useMatchRoute(routes)
}
export const useMatchHomeRoute = () => useMatchRoute(["index"])
