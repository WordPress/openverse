<template>
  <table
    :aria-label="$t('sources.aria.source-table').toString()"
    role="region"
    class="not-prose source-table w-full table-fixed text-base"
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
        <td>
          <span>{{ $t("sources.providers.source") }}</span>
          <VLink :href="providerViewUrl(provider)">{{
            provider.display_name
          }}</VLink>
        </td>
        <td class="truncate font-semibold">
          <span>{{ $t("sources.providers.domain") }}</span>
          <VLink :href="provider.source_url">
            {{ cleanSourceUrlForPresentation(provider.source_url) }}
          </VLink>
        </td>
        <td class="md:text-right">
          <span>{{ $t("sources.providers.item") }}</span>
          {{ getLocaleFormattedNumber(provider.media_count || 0) }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType, reactive } from "vue"

import { useProviderStore } from "~/stores/provider"
import { useGetLocaleFormattedNumber } from "~/composables/use-get-locale-formatted-number"

import type { SupportedMediaType } from "~/constants/media"
import type { MediaProvider } from "~/types/media-provider"

import { useSearchStore } from "~/stores/search"

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

    const searchStore = useSearchStore()
    const providerViewUrl = (provider: MediaProvider) => {
      return searchStore.getCollectionPath({
        type: props.media,
        collectionParams: {
          collection: "source",
          source: provider.source_name,
        },
      })
    }
    return {
      getLocaleFormattedNumber,
      sortedProviders,
      sorting,
      sortTable,
      cleanSourceUrlForPresentation,
      providerViewUrl,
    }
  },
})
</script>

<style scoped>
@tailwind base;
@tailwind components;
@tailwind utilities;

.display-initial {
  display: initial;
}

@layer components {
  .source-table {
    @apply block md:table rounded-sm border-0 border-dark-charcoal-20;
  }
  .source-table thead {
    @apply hidden md:table-header-group;
  }
  .source-table tbody {
    @apply block md:table-row-group;
  }
  .source-table th,
  .source-table td {
    @apply md:border-dark-charcoal-20;
  }
  .source-table a {
    @apply text-pink hover:underline;
  }
  .source-table th {
    @apply cursor-pointer border-t bg-dark-charcoal-10;
  }
  .source-table th,
  .source-table td {
    @apply md:border-r p-4 md:first:border-l;
  }

  .source-table td {
    @apply flex md:table-cell break-normal border-y-0;
  }

  .source-table td span {
    @apply block md:hidden font-bold;
    width: 10ch;
    min-width: 10ch;
  }

  .source-table tr {
    @apply flex flex-col md:table-row border-r border-l first:border-t last:border-b md:border-none even:bg-dark-charcoal-06 border-dark-charcoal-20;
  }

  .source-table th {
    @apply first:rounded-ss-sm last:rounded-se-sm;
  }

  .source-table tr:last-child td {
    @apply md:border-b first:rounded-es-sm last:rounded-ee-sm;
  }
}
</style>
