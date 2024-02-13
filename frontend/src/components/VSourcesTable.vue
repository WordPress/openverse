<template>
  <table
    :aria-label="$t('sources.aria.table').toString()"
    role="region"
    class="not-prose table w-full table-fixed text-base"
  >
    <thead>
      <tr>
        <th
          tabindex="0"
          @click="sortTable('display_name')"
          @keypress.enter="sortTable('display_name')"
        >
          <span class="flex w-full flex-row items-center justify-between">
            {{ $t("sources.providers.source") }}
            <TableSortIcon :active="sorting.field === 'display_name'" />
          </span>
        </th>
        <th
          tabindex="0"
          @click="sortTable('source_url')"
          @keypress.enter="sortTable('source_url')"
        >
          <span class="flex w-full flex-row items-center justify-between">
            {{ $t("sources.providers.domain") }}
            <TableSortIcon :active="sorting.field === 'source_url'" />
          </span>
        </th>
        <th
          tabindex="0"
          @click="sortTable('media_count')"
          @keypress.enter="sortTable('media_count')"
        >
          <span class="flex w-full flex-row items-center justify-between">
            {{ $t("sources.providers.item") }}
            <TableSortIcon :active="sorting.field === 'media_count'" />
          </span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="provider in sortedProviders" :key="provider.display_name">
        <td v-if="additionalSearchViews">
          <VLink :href="providerViewUrl(provider)">{{
            provider.display_name
          }}</VLink>
        </td>
        <td v-else>{{ provider.display_name }}</td>
        <td class="truncate font-semibold">
          <VLink :href="provider.source_url">
            {{ cleanSourceUrlForPresentation(provider.source_url) }}
          </VLink>
        </td>
        <td class="text-right">
          {{ getLocaleFormattedNumber(provider.media_count || 0) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, reactive } from "vue"

import { useContext } from "@nuxtjs/composition-api"

import { useProviderStore } from "~/stores/provider"
import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"

import type { SupportedMediaType } from "~/constants/media"
import type { MediaProvider } from "~/types/media-provider"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import TableSortIcon from "~/components/TableSortIcon.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VSourcesTable",
  components: {
    TableSortIcon,
    VLink,
  },
  props: {
    media: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const { app } = useContext()

    const sorting = reactive({
      direction: "asc",
      field: "display_name" as keyof Omit<MediaProvider, "logo_url">,
    })

    function sortTable(field: keyof Omit<MediaProvider, "logo_url">) {
      let direction = "asc"
      if (field === sorting.field) {
        direction = sorting.direction === "asc" ? "desc" : "asc"
      }

      sorting.direction = direction
      sorting.field = field
    }

    function cleanSourceUrlForPresentation(url: string) {
      const stripProtocol = (s: string) => s.replace(/https?:\/\//, "")
      const stripLeadingWww = (s: string) =>
        s.startsWith("www.") ? s.replace("www.", "") : s
      const removeAfterSlash = (s: string) => s.split("/")[0]

      return removeAfterSlash(stripLeadingWww(stripProtocol(url)))
    }

    const getLocaleFormattedNumber = useGetLocaleFormattedNumber()
    const providerStore = useProviderStore()

    function compareProviders(prov1: MediaProvider, prov2: MediaProvider) {
      let field1 = prov1[sorting.field]
      let field2 = prov2[sorting.field]
      if (sorting.field === "display_name") {
        field1 = prov1[sorting.field].toLowerCase()
        field2 = prov2[sorting.field].toLowerCase()
      }

      if (sorting.field === "source_url") {
        field1 = cleanSourceUrlForPresentation(field1 as string)
        field2 = cleanSourceUrlForPresentation(field2 as string)
      }
      if (field1 > field2) {
        return 1
      }
      if (field1 < field2) {
        return -1
      }
      return 0
    }

    const sortedProviders = computed<MediaProvider[]>(() => {
      const providers = providerStore.providers[props.media]
      providers.sort(compareProviders)
      return sorting.direction === "asc" ? providers : providers.reverse()
    })

    const featureFlagStore = useFeatureFlagStore()
    const additionalSearchViews = computed(() => {
      return featureFlagStore.isOn("additional_search_views")
    })
    const providerViewUrl = (provider: MediaProvider) => {
      return app.localePath(`/${props.media}/source/${provider.source_name}`)
    }
    return {
      getLocaleFormattedNumber,
      sortedProviders,
      sorting,
      sortTable,
      cleanSourceUrlForPresentation,
      providerViewUrl,
      additionalSearchViews,
    }
  },
})
</script>

<style scoped>
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .table {
    @apply rounded-sm border-0 border-dark-charcoal-20;
  }
  .table th,
  .table td {
    @apply border-dark-charcoal-20;
  }
  .table a {
    @apply text-pink hover:underline;
  }
  .table th {
    @apply cursor-pointer border-t bg-dark-charcoal-10;
  }
  .table th,
  .table td {
    @apply border-r p-4 first:border-l;
  }
  .table td {
    @apply break-normal border-y-0;
  }

  .table tr {
    @apply even:bg-dark-charcoal-06;
  }

  .table th {
    @apply first:rounded-ss-sm last:rounded-se-sm;
  }

  .table tr:last-child td {
    @apply border-b first:rounded-es-sm last:rounded-ee-sm;
  }
}
</style>
