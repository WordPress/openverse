<template>
  <div>
    <table
      :aria-label="$t('sources.aria.table')"
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
            <VLink :href="providerViewUrl(provider)">{{
              provider.display_name
            }}</VLink>
          </td>
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

    <section role="region" class="mobile-source-table md:hidden">
      <article
        v-for="provider in sortedProviders"
        :key="provider.display_name"
        :title="provider.display_name"
      >
        <p>{{ $t("sources.providers.source") }}</p>

        <VLink :href="providerViewUrl(provider)">{{
          provider.display_name
        }}</VLink>

        <p>{{ $t("sources.providers.domain") }}</p>

        <VLink :href="provider.source_url">
          {{ cleanSourceUrlForPresentation(provider.source_url) }}
        </VLink>

        <p>{{ $t("sources.providers.item") }}</p>

        <span>
          {{ getLocaleFormattedNumber(provider.media_count || 0) }}
        </span>
      </article>
    </section>
  </div>
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

@layer components {
  .source-table {
    @apply hidden rounded-sm border-0 border-dark-charcoal-20 md:table;
  }

  .source-table th,
  .source-table td {
    @apply border-dark-charcoal-20;
  }

  .source-table a {
    @apply text-pink hover:underline;
  }

  .source-table th {
    @apply cursor-pointer border-t bg-dark-charcoal-10;
  }

  .source-table th,
  .source-table td {
    @apply border-r p-4 first:border-l;
  }

  .source-table td {
    @apply break-normal border-y-0;
  }

  .source-table tr {
    @apply even:bg-dark-charcoal-06;
  }

  .source-table th {
    @apply first:rounded-ss-sm last:rounded-se-sm;
  }

  .source-table tr:last-child td {
    @apply border-b first:rounded-es-sm last:rounded-ee-sm;
  }

  .mobile-source-table article {
    @apply grid border-l border-r border-dark-charcoal-20 p-4 sm:grid-cols-4;
  }

  .mobile-source-table article:first-child {
    @apply border-t;
  }

  .mobile-source-table article:last-child {
    @apply border-b;
  }

  .mobile-source-table article:nth-child(odd) {
    @apply bg-dark-charcoal-10;
  }

  .mobile-source-table article p {
    @apply col-span-1 pt-2 font-bold;
  }

  .mobile-source-table article p:first-child {
    @apply pt-0;
  }

  .mobile-source-table article a,
  .mobile-source-table article span {
    @apply col-span-3;
  }

  .mobile-source-table article a {
    @apply font-bold text-pink hover:underline;
  }
}
</style>
