import { RouteLocationNormalized } from "vue-router"

/**
 * Get the route name as a string. If the name is undefined, return an empty string.
 * This function is necessary because the route name can be a symbol, or undefined in some cases.
 * @param route - the route to get the name from
 */
export const getRouteNameString = (route: RouteLocationNormalized): string => {
  if (typeof route?.name === "string") {
    return route.name
  }
  return route?.name?.toString() ?? ""
}
