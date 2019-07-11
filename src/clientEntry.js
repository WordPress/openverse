import Vue from 'vue';
import router from './router/client';
import createApp from './main';

// a global mixin that calls `asyncData` when a route component's params change
Vue.mixin({
  beforeRouteUpdate(to, from, next) {
    const { asyncData } = this.$options;
    if (asyncData) {
      asyncData({
        store: this.$store,
        route: to,
      }).then(next).catch(next);
    }
    else {
      next();
    }
  },
});

const { app, store } = createApp(router);

// prime the store with server-initialized state.
// the state is determined during SSR and inlined in the page markup.
// doesn't replace query values from __INITIAL_STATE__
// query values are initialized from URL inside store (see search store state definition)
if (window.__INITIAL_STATE__) {
  const { query, ...initialState } = window.__INITIAL_STATE__;
  initialState.query = store.state.query;
  store.replaceState(initialState);
}

// wait until router has resolved all async before hooks
// and async components...
router.onReady(() => {
  // Add router hook for handling asyncData.
  // Doing it after initial route is resolved so that we don't double-fetch
  // the data that we already have. Using router.beforeResolve() so that all
  // async components are resolved.
  router.beforeResolve((to, from, next) => {
    const matched = router.getMatchedComponents(to);
    const prevMatched = router.getMatchedComponents(from);
    let diffed = false;
    // eslint-disable-next-line no-return-assign
    const activated = matched.filter((c, i) => diffed || (diffed = (prevMatched[i] !== c)));
    const asyncDataHooks = activated.map(c => c.asyncData).filter(_ => _);
    if (!asyncDataHooks.length) {
      return next();
    }
    return 0;
  });

  // actually mount to DOM
  app.$mount('#app');
});
