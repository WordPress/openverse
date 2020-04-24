import smoothscroll from 'smoothscroll-polyfill';
import Vue from 'vue';
import createApp from './main';
import abTests from './abTests';
import sentryInit from './sentry/browser';
import router from './router/client';

sentryInit();
smoothscroll.polyfill();

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

const { app, store } = createApp(router, window.__INITIAL_STATE__);

abTests(store);

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
