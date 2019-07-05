import Vue from 'vue';
import VueRouter from 'vue-router';
import AboutPage from '@/pages/AboutPage';
import HomePage from '@/pages/HomePage';
// import BrowsePage from '@/pages/BrowsePage';
// import PhotoDetailPage from '@/pages/PhotoDetailPage';
import FeedbackPage from '@/pages/FeedbackPage';
import CollectionsPage from '@/pages/CollectionsPage';
// import CollectionBrowsePage from '@/pages/CollectionBrowsePage';
import SearchHelpPage from '@/pages/SearchHelpPage';

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  routes: [
    // {
    //   path: '/search',
    //   name: 'browse-page',
    //   component: BrowsePage,
    //   props: route => ({ query: route.query.q }),
    // },
    // {
    //   path: '/photos/:id',
    //   name: 'photo-detail-page',
    //   component: PhotoDetailPage,
    //   props: true,
    // },
    {
      path: '/about',
      name: 'about-page',
      component: AboutPage,
    },
    {
      path: '/search-help',
      name: 'search-help-page',
      component: SearchHelpPage,
    },
    {
      path: '/feedback',
      name: 'feedback-page',
      component: FeedbackPage,
    },
    {
      path: '/collections',
      name: 'collections-page',
      component: CollectionsPage,
    },
    // {
    //   path: '/collections/:provider',
    //   name: 'collections-browse-page',
    //   component: CollectionBrowsePage,
    //   props: true,
    // },
    {
      path: '/',
      name: 'home-page',
      component: HomePage,
    },
  ],
  scrollBehavior() {
    return { x: 0, y: 0 };
  },
});

router.afterEach((to) => {
  if (typeof ga !== 'undefined') {
    ga('set', 'page', to.fullPath);
    ga('send', 'pageview');
  }
});

export const routePush = location => router.push(location);

export default router;
