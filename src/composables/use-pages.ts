import { computed, useContext, useRoute } from '@nuxtjs/composition-api'

export default function usePages() {
  const { app } = useContext()

  const pages = [
    {
      id: 'about',
      name: 'header.about-nav-item',
      link: app.localePath('/about'),
    },
    {
      id: 'sources',
      name: 'header.source-nav-item',
      link: app.localePath('/sources'),
    },
    {
      id: 'licenses',
      name: 'header.licenses-nav-item',
      link: 'https://creativecommons.org/about/cclicenses/',
    },
    {
      id: 'search-help',
      name: 'header.search-guide-nav-item',
      link: app.localePath('/search-help'),
    },
    {
      id: 'meta-search',
      name: 'header.meta-search-nav-item',
      link: app.localePath('/meta-search'),
    },
    {
      id: 'feedback',
      name: 'header.feedback-nav-item',
      link: app.localePath('/feedback'),
    },
    {
      id: 'api',
      name: 'header.api-nav-item',
      link: 'https://api.openverse.engineering/v1/',
    },
    {
      id: 'privacy',
      name: 'header.privacy-nav-item',
      link: 'https://wordpress.org/privacy',
    },
  ]

  const route = useRoute()
  const currentPageId = computed(() => route.value.name)

  return { all: pages, current: currentPageId }
}
