// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack-base.conf with an alias.
import Vue from 'vue'
import App from './App'
import i18n from './i18n'
import store from '../store'
import GoogleAnalytics from './analytics/GoogleAnalytics'

function createApp(router, __INITIAL_STATE__) {
  Vue.config.productionTip = false

  const analytics = GoogleAnalytics()
  analytics.anonymizeIpAddress()
  analytics.setTransportBeacon()

  const appStore = store(analytics, router)

  // prime the store with server-initialized state.
  // the state is determined during SSR and inlined in the page markup.
  // doesn't replace query and isFilterVisible values from __INITIAL_STATE__
  // query values are initialized from URL inside store (see search store state definition)
  // isFilterVisible is always false on server, but can be true on the client (browser desktops)
  if (__INITIAL_STATE__) {
    const {
      query,
      filters,
      isFilterVisible,
      isFilterApplied,
      imageProviders,
      ...initialState
    } = __INITIAL_STATE__
    initialState.query = appStore.state.query
    initialState.isFilterVisible = appStore.state.isFilterVisible
    initialState.isFilterApplied = appStore.state.isFilterApplied
    initialState.filters = appStore.state.filters
    initialState.imageProviders = appStore.state.imageProviders
    appStore.replaceState(initialState)
  }

  const app = new Vue({
    el: '#app',
    store: appStore,
    router,
    i18n,
    render: (h) => h(App),
  })

  return { app, store: appStore, router }
}

export default createApp
