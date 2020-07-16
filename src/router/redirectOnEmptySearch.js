/**
 * redirects the user to home page if the search query params are empty
 * @param router
 */
const redirectOnEmptySearch = (router) => {
  router.beforeEach((to, from, next) => {
    if (to.matched.some((record) => record.meta.requiresQuery)) {
      // this route requires query, check if any
      // if not, redirect to home page.
      if (!to.query.q) {
        next('/')
      } else {
        next()
      }
    } else {
      next()
    }
  })
}

export default redirectOnEmptySearch
