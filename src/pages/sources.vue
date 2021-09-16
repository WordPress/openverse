<template>
  <div class="section">
    <div :class="['container', isEmbedded ? '' : 'is-fluid']">
      <div class="mb-10">
        <h1 class="text-5xl mb-10">
          {{ $t('sources.title') }}
        </h1>
        <div class="mb-10">
          <h3 class="text-2xl">
            {{ $t('sources.cc-content.where') }}
          </h3>
          <p class="my-4">
            {{ $t('sources.cc-content.content') }}
          </p>
          <i18n path="sources.cc-content.provider" tag="p" class="my-4">
            <template #flickr>
              <a aria-label="flickr" href="https://www.flickr.com/">{{
                $t('sources.cc-content.flickr')
              }}</a>
            </template>
            <template #smithsonian>
              <a aria-label="smithsonian" href="https://www.si.edu/">{{
                $t('sources.cc-content.smithsonian')
              }}</a>
            </template>
          </i18n>
          <i18n path="sources.cc-content.europeana" tag="p" class="my-4">
            <template #link>
              <a aria-label="europeana" href="https://www.europeana.eu/en">{{
                $t('sources.cc-content.europeana-link')
              }}</a>
            </template>
            <template #link-api>
              <a
                aria-label="europeana-api"
                href="https://pro.europeana.eu/page/apis"
                >{{ $t('sources.cc-content.europeana-api') }}</a
              >
            </template>
          </i18n>
        </div>
        <div class="mb-10">
          <h3 class="text-2xl">
            {{ $t('sources.new-content.next') }}
          </h3>
          <p class="my-4">
            {{ $t('sources.new-content.integrate') }}
          </p>
          <div class="content">
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
          </div>
        </div>

        <h3 class="text-2xl my-4">
          {{ $t('sources.suggestions') }}
        </h3>
        <a
          href="https://github.com/WordPress/openverse-catalog/issues/new?assignees=&labels=%F0%9F%9A%A6+status%3A+awaiting+triage%2C+%F0%9F%A7%B9+status%3A+ticket+work+required%2C+%E2%98%81%EF%B8%8F+provider%3A+any&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
          class="button is-primary py-8"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ $t('sources.issue-button') }}
          <i class="icon external-link mx-2 mt-2" />
        </a>
      </div>
      <i18n path="sources.detail" tag="p">
        <template #single-name>
          <strong>
            {{ $t('sources.single-name') }}
          </strong>
        </template>
      </i18n>
      <table
        :aria-label="$t('about.aria.sources-table')"
        role="region"
        class="table is-striped mt-4 mb-10"
      >
        <thead>
          <tr>
            <th
              tabindex="0"
              @click="sortTable('display_name')"
              @keypress.enter="sortTable('display_name')"
            >
              <span class="table-header-inner">
                {{ $t('sources.providers.source') }}
                <span class="icon"><i class="icon sort" /></span>
              </span>
            </th>
            <th>{{ $t('sources.providers.domain') }}</th>
            <th
              tabindex="0"
              @click="sortTable('image_count')"
              @keypress.enter="sortTable('image_count')"
            >
              <span class="table-header-inner">
                {{ $t('sources.providers.item') }}
                <span class="icon"><i class="icon sort" /></span>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(imageProvider, index) in sortedProviders" :key="index">
            <td class="bold-cell">
              <a :href="`/search?source=${imageProvider.source_name}`">
                {{ imageProvider.display_name }}
              </a>
            </td>
            <td class="bold-cell">
              <a :href="imageProvider.source_url">
                {{ imageProvider.source_url }}
              </a>
            </td>
            <td class="number-cell">
              {{ getProviderImageCount(imageProvider.image_count) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import sortBy from 'lodash.sortby'
import { mapState } from 'vuex'

const SourcePage = {
  name: 'source-page',
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  data() {
    return {
      sort: {
        direction: 'asc',
        field: 'display_name',
      },
    }
  },
  computed: {
    ...mapState(['imageProviders', 'isEmbedded']),
    sortedProviders() {
      const sorted = sortBy(this.imageProviders, [this.sort.field])
      return this.sort.direction === 'asc' ? sorted : sorted.reverse()
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString(this.$i18n.locale)
    },
    sortTable(field) {
      let direction = 'asc'
      if (field === this.sort.field) {
        direction = this.sort.direction === 'asc' ? 'desc' : 'asc'
      }

      this.sort = { direction, field }
    },
  },
}

export default SourcePage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '~/styles/text-only-page.scss';

$table-border: 1px solid $color-light-gray;
$table-border-radius: 4px;

.button.is-primary {
  font-size: 1.1875rem;
  font-weight: 700;
}

.table.is-striped {
  th {
    cursor: pointer;
  }

  .table-header-inner {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    > .icon {
      margin-top: -4px;
    }
  }

  td,
  th {
    word-break: initial;
    border-bottom: none;
    border-top: none;
  }

  /* The following are styles for rounding the table's corners */
  border-collapse: separate;
  border-radius: $table-border-radius;

  th:first-child {
    border-top-left-radius: $table-border-radius;
  }
  th:last-child {
    border-top-right-radius: $table-border-radius;
  }

  tr:last-child {
    td {
      border-bottom: $table-border;
    }
    td:first-child {
      border-bottom-left-radius: $table-border-radius;
    }
    td:last-child {
      border-bottom-right-radius: $table-border-radius;
    }
  }

  td {
    border-left: $table-border;
  }

  tr td:last-child {
    border-right: $table-border;
  }
}

.bold-cell {
  font-weight: 600;
}

.number-cell {
  font-weight: 500;
}
</style>
