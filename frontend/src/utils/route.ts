import { RouteLocationNormalizedLoaded } from "vue-router"

const routeName = (route: RouteLocationNormalizedLoaded) =>
  (route.name?.toString() ?? "").split("__")[0]

export const isSearchRoute = (route: RouteLocationNormalizedLoaded) => {
  const name = routeName(route)
  return ["search", "search-audio", "search-image"].includes(name)
}

export const isResultsRoute = (route: RouteLocationNormalizedLoaded) => {
  const name = routeName(route)
  return (
    isSearchRoute(route) ||
    [
      "audio-tag-tag",
      "audio-source-source",
      "image-tag-tag",
      "image-source-source",
    ].includes(name)
  )
}
