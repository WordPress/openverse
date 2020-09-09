/**
 * Ignore duplicate route errors
 * @see https://router.vuejs.org/guide/advanced/navigation-failures.html#detecting-navigation-failures
 */
const handleRouteErrors = (failure) => {
  // Until vue-router@3.4.0 comes out, this is how to detect a 'duplicate navigation' error
  if (failure.type !== 4) throw Error
}

// @todo Fix Router
const redirectTo = (router = () => {}) => (location, replace = false) => {
  if (replace) {
    router.replace(location).catch(handleRouteErrors)
  } else {
    router.push(location).catch(handleRouteErrors)
  }
}

export default redirectTo
