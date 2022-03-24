<template>
  <VContentPage>
    <h1>
      {{ $t('sources.title') }}
    </h1>

    <h3>
      {{ $t('sources.cc-content.where', { openverse: 'Openverse' }) }}
    </h3>
    <p>
      {{ $t('sources.cc-content.content', { openverse: 'Openverse' }) }}
    </p>
    <i18n path="sources.cc-content.provider" tag="p">
      <template #flickr>
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        <VLink href="https://www.flickr.com/">Flickr</VLink>
      </template>
      <template #smithsonian>
        <VLink href="https://www.si.edu/">{{
          $t('sources.cc-content.smithsonian')
        }}</VLink>
      </template>
    </i18n>
    <i18n path="sources.cc-content.europeana" tag="p">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <template #openverse>Openverse</template>
      <template #link>
        <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
        <VLink href="https://www.europeana.eu/en">Europeana</VLink>
      </template>
      <template #link-api>
        <VLink href="https://pro.europeana.eu/page/apis">{{
          $t('sources.cc-content.europeana-api')
        }}</VLink>
      </template>
    </i18n>

    <h3>
      {{ $t('sources.new-content.next') }}
    </h3>
    <p>
      {{ $t('sources.new-content.integrate') }}
    </p>
    <ul>
      <li>
        {{ $t('sources.new-content.impact') }}
      </li>
      <li>
        {{ $t('sources.new-content.reuse') }}
      </li>
      <li>
        {{ $t('sources.new-content.total-items') }}
      </li>
    </ul>

    <h3>
      {{ $t('sources.suggestions') }}
    </h3>

    <p class="inline-block">
      <VButton
        as="VLink"
        variant="primary"
        size="disabled"
        class="not-prose font-semibold mt-5 px-6 py-4"
        href="https://github.com/WordPress/openverse-catalog/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C+%F0%9F%A7%B9+status%3A+ticket+work+required%2C+%E2%98%81%EF%B8%8F+provider%3A+any&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
      >
        {{ $t('sources.issue-button') }}
        <VIcon :icon-path="externalLinkIcon" :rtl-flip="true" class="mx-2" />
      </VButton>
    </p>

    <i18n path="sources.detail" tag="p">
      <template #single-name>
        <strong>
          {{ $t('sources.single-name') }}
        </strong>
      </template>
    </i18n>

    <table
      :aria-label="$t('sources.aria.table')"
      role="region"
      class="table is-striped mt-4 mb-10 border border-dark-charcoal-06 not-prose text-base"
    >
      <thead>
        <tr>
          <th
            tabindex="0"
            @click="sortTable('display_name')"
            @keypress.enter="sortTable('display_name')"
          >
            <span class="w-full flex flex-row items-center justify-between">
              {{ $t('sources.providers.source') }}
              <TableSortIcon :active="sort.field === 'display_name'" />
            </span>
          </th>
          <th
            tabindex="0"
            @click="sortTable('source_url')"
            @keypress.enter="sortTable('source_url')"
          >
            <span class="w-full flex flex-row items-center justify-between">
              {{ $t('sources.providers.domain') }}
              <TableSortIcon :active="sort.field === 'source_url'" />
            </span>
          </th>
          <th
            tabindex="0"
            @click="sortTable('media_count')"
            @keypress.enter="sortTable('media_count')"
          >
            <span class="w-full flex flex-row items-center justify-between">
              {{ $t('sources.providers.item') }}
              <TableSortIcon :active="sort.field === 'media_count'" />
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(imageProvider, index) in sortedProviders" :key="index">
          <td>
            {{ imageProvider.display_name }}
          </td>
          <td class="font-semibold">
            <VLink :href="imageProvider.source_url">
              {{ imageProvider.source_url }}
            </VLink>
          </td>
          <td class="number-cell">
            {{ getLocaleFormattedNumber(imageProvider.media_count || 0) }}
          </td>
        </tr>
      </tbody>
    </table>
  </VContentPage>
</template>

<script>
import sortBy from 'lodash.sortby'
import { mapState } from 'vuex'

import { PROVIDER } from '~/constants/store-modules'
import { useGetLocaleFormattedNumber } from '~/composables/use-get-locale-formatted-number'

import VButton from '~/components/VButton.vue'
import VLink from '~/components/VLink.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import TableSortIcon from '~/components/TableSortIcon.vue'
import VContentPage from '~/components/VContentPage.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'

const SourcePage = {
  name: 'source-page',
  components: { VButton, VContentPage, VIcon, VLink, TableSortIcon },
  data() {
    return {
      sort: {
        direction: 'asc',
        field: 'display_name',
      },
    }
  },
  setup() {
    const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

    return { getLocaleFormattedNumber, externalLinkIcon }
  },
  computed: {
    ...mapState(PROVIDER, ['imageProviders']),
    sortedProviders() {
      const sorted = sortBy(this.imageProviders, [this.sort.field])
      return this.sort.direction === 'asc' ? sorted : sorted.reverse()
    },
  },
  methods: {
    sortTable(field) {
      let direction = 'asc'
      if (field === this.sort.field) {
        direction = this.sort.direction === 'asc' ? 'desc' : 'asc'
      }

      this.sort = { direction, field }
    },
  },
  head() {
    return {
      title: `${this.$t('sources.title')} | Openverse`,
    }
  },
}

export default SourcePage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.table {
  table-layout: fixed;
  width: 100%;
}

.table.is-bordered td {
  word-break: break-all;
}

.button.is-primary {
  font-size: 1.1875rem;
  font-weight: 700;
}
.table.is-striped th {
  cursor: pointer;
}
.table.is-striped svg {
  margin-top: -4px;
}

.table.is-striped th:not(:first-child),
.table.is-striped td:not(:first-child) {
  @apply border border-dark-charcoal-06;
}
.table.is-striped td,
.table.is-striped th {
  word-break: initial;
  border-bottom: none;
  border-top: none;
}
.table.is-striped {
  --table-border-radius: 2px;
  /* The following are styles for rounding the table's corners */
  border-collapse: separate;
  border-radius: var(table-border-radius);
}

.table.is-striped th:first-child {
  border-top-left-radius: var(--table-border-radius);
}
.table.is-striped th:last-child {
  border-top-right-radius: var(--table-border-radius);
}
.table.is-striped tr:last-child td:first-child,
.table.is-striped tr:last-child td:last-child {
  border-bottom-left-radius: var(--table-border-radius);
}
</style>
