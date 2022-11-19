import { computed, useContext, useRoute } from '@nuxtjs/composition-api'

export default function usePages(isNew = false) {
  const { app } = useContext()

  const pages = isNew
    ? [
        {
          id: 'about',
          name: 'navigation.about',
          link: app.localePath('/about'),
        },
        {
          id: 'licenses',
          name: 'navigation.licenses',
          link: 'https://creativecommons.org/about/cclicenses/',
        },
        {
          id: 'get-involved',
          name: 'navigation.get-involved',
          link: 'https://make.wordpress.org/openverse/handbook/',
        },
        {
          id: 'api',
          name: 'navigation.api',
          link: 'https://api.openverse.engineering/v1/',
        },
        {
          id: 'privacy',
          name: 'navigation.privacy',
          link: 'https://wordpress.org/privacy',
        },
        {
          id: 'feedback',
          name: 'navigation.feedback',
          link: app.localePath('/feedback'),
        },
      ]
    : [
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
          id: 'external-sources',
          name: 'header.external-sources-nav-item',
          link: app.localePath('/external-sources'),
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
  /**
   * The route name of the current page is localized, so it looks like `index__en`.
   * We need to remove the locale suffix to match the page id.
   */
  const currentPageId = computed(() => route.value?.name?.split('__')[0])

  return { all: pages, current: currentPageId }
}
