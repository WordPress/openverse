<template>
  <div class="section">
    <div class="container is-fluid columns">
      <header class="column is-full margin-bottom-small">
        <h1 class="title is-2" role="article">
          {{ $t('sources.title') }}
        </h1>
      </header>
    </div>
    <div class="container is-fluid columns is-variable is-4">
      <div class="column">
        <i18n path="sources.detail" tag="p">
          <template v-slot:single-name>
            <strong>
              {{ $t('sources.single-name') }}
            </strong>
          </template>
        </i18n>
        <table
          :aria-label="$t('about.aria.sources')"
          role="region"
          class="table is-bordered is-striped margin-bottom-large margin-top-normal"
        >
          <thead>
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
          </thead>
          <tbody>
            <tr
              v-for="(imageProvider, index) in sortedProviders"
              :key="index"
              role="row"
            >
              <td>
                <a
                  :aria-label="imageProvider.display_name"
                  :href="`/search?source=${imageProvider.source_name}`"
                >
                  {{ imageProvider.display_name }}
                </a>
              </td>
              <td class="number-cell">
                {{ getProviderImageCount(imageProvider.image_count) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="column">
        <h3 class="title subtitle is-normal is-4">
          {{ $t('sources.cc-content.where') }}
        </h3>
        <p class="body-big margin-vertical-normal">
          {{ $t('sources.cc-content.content') }}
        </p>
        <i18n
          path="sources.cc-content.provider"
          tag="p"
          class="body-big margin-vertical-normal"
        >
          <template v-slot:flickr>
            <a aria-label="flickr" href="https://www.flickr.com/">Flickr</a>
          </template>
          <template v-slot:smithsonian>
            <a aria-label="smithsonian" href="https://www.si.edu/"
              >Smithsonian Institute</a
            >
          </template>
        </i18n>
        <i18n
          path="sources.cc-content.europeana"
          tag="p"
          class="body-big margin-vertical-normal"
        >
          <template v-slot:link>
            <a aria-label="europeana" href="https://www.europeana.eu/en"
              >Europeana</a
            >
          </template>
          <template v-slot:link-api>
            <a
              aria-label="europeana-api"
              href="https://pro.europeana.eu/page/apis"
              >Europeana API</a
            >
          </template>
        </i18n>
        <h3 class="title subtitle is-normal is-4">
          {{ $t('sources.new-content.next') }}
        </h3>
        <p class="body-big margin-vertical-normal">
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
        <h5 class="title subtitle is-5 margin-vertical-normal">
          {{ $t('sources.suggestions') }}
        </h5>
        <a
          href="https://github.com/creativecommons/cccatalog/issues/new?assignees=&labels=awaiting+triage%2C+ticket+work+required%2C+providers&template=new-source-suggestion.md&title=%5BSource+Suggestion%5D+Insert+source+name+here"
          class="button is-primary is-uppercase"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ $t('sources.issue-button') }}
          <i class="margin-left-small icon external-link" />
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import sortBy from 'lodash.sortby'

const SourcePage = {
  name: 'source-page',
  layout: 'with-nav-search',
  data() {
    return {
      sort: {
        direction: 'asc',
        field: 'display_name',
      },
    }
  },
  computed: {
    imageProviders() {
      return this.$store.state.imageProviders
    },
    sortedProviders() {
      const sorted = sortBy(this.imageProviders, [this.sort.field])
      return this.sort.direction === 'asc' ? sorted : sorted.reverse()
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return imageCount.toLocaleString('en')
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

.table.is-bordered {
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
  }
}
</style>
