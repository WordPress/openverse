// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack-base.conf with an alias.

import Vue from 'vue';
import ApiService from '@/api/ApiService';
import App from './App';
import router from './router';
import store from './store';
import GoogleAnalytics from './analytics/GoogleAnalytics';

Vue.config.productionTip = false;

ApiService.init();
const analytics = GoogleAnalytics();
analytics.anonymizeIpAddress();

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store: store(analytics),
  router,
  components: { App },
  template: '<App/>',
});
