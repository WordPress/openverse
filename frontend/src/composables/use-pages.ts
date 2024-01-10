import { useNuxtApp, useRoute } from "#imports"

import { computed } from "vue"

export default function usePages() {
  const localePath = useNuxtApp().$localePath

  const pages = [
    {
      id: "about",
      name: "navigation.about",
      link: localePath("/about"),
    },
    {
      id: "licenses",
      name: "navigation.licenses",
      link: "https://creativecommons.org/about/cclicenses/",
    },
    {
      id: "sources",
      name: "navigation.sources",
      link: localePath("/sources"),
    },
    {
      id: "search-help",
      name: "navigation.searchHelp",
      link: localePath("/search-help"),
    },
    {
      id: "get-involved",
      name: "navigation.getInvolved",
      link: "https://make.wordpress.org/openverse/handbook/",
    },
    {
      id: "api",
      name: "navigation.api",
      link: "https://api.openverse.engineering/v1/",
    },
    {
      id: "privacy",
      name: "navigation.privacy",
      link: localePath("/privacy"),
    },
    {
      id: "feedback",
      name: "navigation.feedback",
      link: localePath("/feedback"),
    },
  ]

  const route = useRoute()
  /**
   * The route name of the current page is localized, so it looks like `index__en`.
   * We need to remove the locale suffix to match the page id.
   */
  const currentPageId = computed<string>(
    () => String(route.name)?.split("__")[0] ?? ""
  )

  return { all: pages, current: currentPageId }
}
