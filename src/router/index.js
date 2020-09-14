import Vue from 'vue'
import VueMeta from 'vue-meta'
import VueRouter from 'vue-router'
import AboutPage from '@/pages/AboutPage'
import SourcePage from '@/pages/SourcePage'
import HomePage from '@/pages/HomePage'
import BrowsePage from '@/pages/BrowsePage'
import MetaSearchPage from '@/pages/MetaSearchPage'
import SupportPage from '@/pages/SupportPage'
import PhotoDetailPage from '@/pages/PhotoDetailPage'
import FeedbackPage from '@/pages/FeedbackPage'
import SearchHelpPage from '@/pages/SearchHelpPage'
import NotFoundPage from '@/pages/NotFoundPage'
import SearchGrid from '@/components/SearchGrid'
import MetaSearchForm from '@/components/MetaSearch/MetaSearchForm'

Vue.use(VueRouter)
Vue.use(VueMeta)

/**
 * These are the nested routes for each tab (image, audio, etc.) on the results pages.
 */
const resultSubviews = [
  { path: '', component: SearchGrid },
  { path: 'image', component: SearchGrid },
  {
    path: 'audio',
    component: MetaSearchForm,
    key: 'audio',
    props: { type: 'audio' },
  },
  {
    path: 'video',
    component: MetaSearchForm,
    key: 'video',
    props: { type: 'video' },
  },
]

const router = new VueRouter({
  mode: 'history',
  routes: [
    // This route is a redirect only
    {
      path: '/collections/:collection',
      redirect: (to) => ({
        path: '/search',
        props: (route) => ({ query: route.query.q }),
        query: { q: '', source: to.params.collection },
      }),
    },
    {
      path: '/search',
      component: BrowsePage,
      props: (route) => ({ query: route.query.q }),
      children: resultSubviews,
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
      path: '/meta-search',
      name: 'meta-search-page',
      component: MetaSearchPage,
    },
    {
      path: '/sources',
      name: 'source-page',
      component: SourcePage,
    },
    // redirect only
    {
      path: '/collections',
      redirect: '/sources',
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
      path: '/support',
      name: 'support-page',
      component: SupportPage,
    },
    {
      path: '/',
      name: 'home-page',
      component: HomePage,
    },
    {
      path: '*',
      name: 'not-found',
      component: NotFoundPage,
    },
  ],
  scrollBehavior(to) {
    if (
      (to.path === '/search' || to.path === '/search/image') &&
      to.params.location
    ) {
      // the setTimeout is for the time it takes it get the images
      // Else the page scrolls up after the images are fetched
      // Disabling linting for the reject argument that isn't used
      // eslint-disable-next-line
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          resolve({ x: 0, y: to.params.location })
        }, 600)
      })
    }
    return { x: 0, y: 0 }
  },
})

router.afterEach((to) => {
  if (typeof ga !== 'undefined') {
    ga('set', 'page', to.fullPath)
    ga('send', 'pageview')
  }
})

export default router
