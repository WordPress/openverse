<template>
<form role="search"
      method="post"
      @submit.prevent="onSubmit"
      class="search-form">
  <div class="search-form_ctr grid-x global-nav show-for-smedium">
      <div class="search-form_inner-ctr medium-12 large-10">
        <input required="required"
               autofocus=""
               class="search-form_input"
               type="search"
               placeholder="Search the commons..."
               autocapitalize="none"
               id="searchInput"
               v-model="query">
        <ul class="search-form_toolbar menu icons icon-top" role="menubar">
          <li class="menu-button search-form_search-button" role="menuitem">
            <a href="#" @click.prevent="onSubmit">
              <i class="fi-list">
                  <svg width="24" height="24" version="1.1"
                       viewBox="0 0 50.000001 50.000001" xmlns="http://www.w3.org/2000/svg">
                   <rect width="24" height="24" fill-opacity="0"/>
                   <path d="m18.623 4.2559c-7.9132 0-14.367 6.454-14.367 14.367 0
                   7.9132 6.454 14.367 14.367 14.367 3.2414 0 6.2283-1.0954
                   8.6367-2.918a2.0002 2.0002 0 0 0 0.15039 0.16602l14.898
                   14.898a2.0002 2.0002 0 1 0 2.8281 -2.8281l-14.898-14.898a2.0002
                   2.0002 0 0 0 -0.16602 -0.15039c1.8225-2.4084 2.918-5.3953
                   2.918-8.6367 0-7.9132-6.454-14.367-14.367-14.367zm0 3.5898c5.9732
                   0 10.777 4.8042 10.777 10.777 0 5.9732-4.8042 10.777-10.777
                   10.777s-10.777-4.8042-10.777-10.777c2e-7 -5.9732 4.8042-10.777
                   10.777-10.777z" color="#000000" color-rendering="auto" fill="#fff" />
                  </svg>
              </i>
              <span class="menu-button_text">Search</span>
            </a>
          </li>
          <li class="menu-button search-form_filter-button" role="menuitem">
            <a href="#" @click.prevent="onToggleSearchGridFilter()">
              <i class="fi-list">
                  <svg xmlns="http://www.w3.org/2000/svg"
                  xmlns:xlink="http://www.w3.org/1999/xlink"
                  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" version="1.1"
                  id="DESIGNS" x="0px" y="0px" width="24px" height="24px" fill="color: #2c3e50"
                  viewBox="0 0 32 32" style="enable-background:new 0 0 32 32;" xml:space="preserve">
                  <title property="dc:title">to filter</title><desc property="dc:description">
                  An icon for "filter" from the Lines and Angles series on to [icon].
                  Downloaded from http://www.toicon.com/icons/lines-and-angles_filter
                  by 127.0.0.1 on 2017-07-10. Licensed CC-BY,
                  see http://toicon.com/license/ for details.</desc>
                  <path class="linesandangles_een" d="M26,6v0.233l-8.487,9.43L17,
                  16.233V17v7.764l-2-1V17v-0.767l-0.513-0.57L6,6.233V6H26 M28,4H4v3
                  l9,10v8l6,3V17l9-10V4L28,4z" style="fill: #d6d6d6"/>
                  <metadata><work rdf:about=""><format>image/svg+xml</format>
                  <type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
                  <license rdf:resource="http://creativecommons.org/licenses/by/4.0/"/>
                  <attributionname>Shannon E Thomas</attributionname><attributionurl>
                  http://www.toicon.com/icons/lines-and-angles_filter</attributionurl>
                  </work></metadata></svg>
              </i>
              <span class="menu-button_text">Filter</span>
            </a>
          </li>
        </ul>
      </div>
      <div class="medium-12 large-12 search-grid-filter-ctr">
          <search-grid-filter :isVisible="isFilterVisible"></search-grid-filter>
      </div>
  </div>
</form>
</template>

<script>
import { FETCH_IMAGES } from '@/store/action-types';
import SearchGridFilter from '@/components/SearchGridFilter';

export default {
  name: 'search-grid-form',
  data: () => ({ query: null, isFilterVisible: false }),
  components: {
    SearchGridFilter,
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();
      if (this.query) {
        this.$store.dispatch(FETCH_IMAGES, { q: this.query });
      }
    },
    onToggleSearchGridFilter() {
      this.isFilterVisible = !this.isFilterVisible;
    },
  },
  mounted() {
    this.query = this.$store.state.query.q;
  },
};
</script>

<style lang="scss" scoped>
  .search-form {
    width: 100%;
    border-bottom: 1px solid #d6d6d6;
  }

  .search-form_search-button a {
    color: #fff;
    background: #4DA5EF;

    span {
      color: #fff;
    }
  }

  .search-form_ctr {
    position: relative;
  }

  .search-grid-filter-ctr {
    overflow: hidden;
  }

  .search-form_filter-button {

    .menu-button_text {
      color: #d6d6d6;
    }
  }

  .search-form_inner-ctr {
    height: inherit;
    display: flex;
  }

  .search-form_input {
    font-size: 24px;
    padding-left: 30px;
    margin-bottom: 0;
    width: 100%;
    height: 100%;
    outline: 0;
    border: none;
    box-shadow: none;

    &:focus {
      border: none;
    }
  }

  .search-form_toolbar {
    width: 400px;

    li {
      border-left: 1px solid #d6d6d6;
      border-right: 1px solid #d6d6d6;

      &:last-of-type {
        border-left: none;
      }
    }
  }

  @media screen and (max-width: 600px) {
    .search-form_input {
      font-size: 18px;
    }
  }
</style>
