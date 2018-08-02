import Vue from 'vue';
import VueRouter from 'vue-router';
import HomePage from '@/pages/HomePage';
import BrowsePage from '@/pages/BrowsePage';
import PhotoDetailPage from '@/pages/PhotoDetailPage';
import store from '@/store';
import { SET_QUERY } from '@/store/mutation-types';


Vue.use(VueRouter);


const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/search',
      name: 'browse-page',
      component: BrowsePage,
      props: route => ({ query: route.query.q }),
    },
    {
      path: '/photo/:id',
      name: 'photo-detail-page',
      component: PhotoDetailPage,
    },
    {
      path: '/',
      name: 'home-page',
      component: HomePage,
    },
  ],
});

router.afterEach((to) => {
  if (to && to.query) {
    store.commit(SET_QUERY, to.query);
  }
});


export default router;
