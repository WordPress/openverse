import Vue from 'vue';
import VueRouter from 'vue-router';
import AboutPage from '@/pages/AboutPage';
import HomePage from '@/pages/HomePage';
import BrowsePage from '@/pages/BrowsePage';
import PhotoDetailPage from '@/pages/PhotoDetailPage';
import ShareListPage from '@/pages/ShareListPage';
import ShareListsPage from '@/pages/ShareListsPage';

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
      path: '/lists/:id',
      name: 'share-list-page',
      component: ShareListPage,
      props: true,
    },
    {
      path: '/lists',
      name: 'share-list-page',
      component: ShareListsPage,
    },
    {
      path: '/photos/:id',
      name: 'photo-detail-page',
      component: PhotoDetailPage,
      props: true,
    },
    {
      path: '/about',
      name: 'about-page',
      component: AboutPage,
    },
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
  ga('set', 'page', to.fullPath);
  ga('send', 'pageview');
});

export const routePush = location => router.push(location);

export default router;
