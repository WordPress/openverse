const redirectTo = (router) => (location, replace = false) => {
  if (replace) {
    router.replace(location)
  } else {
    router.push(location)
  }
}

export default redirectTo
