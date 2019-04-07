<template>
  <form role="search"
        method="post"
        @submit.prevent="onSubmit"
        class="search-form">
    <div class="search-form_ctr grid-container grid-x global-nav show-for-smedium">
        <div class="search-form_inner-ctr cell">
          <input required="required"
                 autofocus="true"
                 class="search-form_input"
                 type="search"
                 placeholder="Search the commons..."
                 autocapitalize="none"
                 id="searchInput"
                 v-model="searchTermsModel"
                 ref="search"
                 @keyup.enter="onSubmit">
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
                     10.777-10.777z" color="#35495e" color-rendering="auto" fill=" #35495e" />
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
                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                    xmlns:cc="http://creativecommons.org/ns#"
                    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" version="1.1"
                    id="DESIGNS" x="0px" y="0px" width="24px" height="24px" fill="color: #35495e"
                    viewBox="0 0 32 32" style="enable-background:new 0 0 32 32;"
                    xml:space="preserve" v-if="!isFilterApplied">
                    <title property="dc:title">to filter</title><desc property="dc:description">
                    An icon for "filter" from the Lines and Angles series on to [icon].
                    Downloaded from http://www.toicon.com/icons/lines-and-angles_filter
                    by 127.0.0.1 on 2017-07-10. Licensed CC-BY, see http://toicon.com/license/
                    for details.</desc>
                    <path class="linesandangles_een" d="M26,6v0.233l-8.487,9.43L17,
                    16.233V17v7.764l-2-1V17v-0.767l-0.513-0.57L6,6.233V6H26 M28,4H4v3
                    l9,10v8l6,3V17l9-10V4L28,4z" style="fill: #2c3e50"/>
                    <metadata><work rdf:about=""><format>image/svg+xml</format>
                    <type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
                    <license rdf:resource="http://creativecommons.org/licenses/by/4.0/"/>
                    <attributionname>Shannon E Thomas</attributionname><attributionurl>
                    http://www.toicon.com/icons/lines-and-angles_filter</attributionurl>
                    </work></metadata></svg>

                    <svg enable-background="new 0 0 24 24" version="1.1" width="24"
                    height="24" viewBox="0 0 1000 1000"
                    xml:space="preserve" xmlns="http://www.w3.org/2000/svg" v-if="isFilterApplied"
                    class="search-grid_filter-btn-icon"
                    fill="#4A69CA">
                    <g transform="matrix(1 0 0 -1 0 1920)"><path d="m783.6 1530.1c-25.7
                    0-50.3 5-73.7 15-23.5 10-43.7 23.5-60.7 40.5s-30.5 37.3-40.5 60.7c-10
                    23.5-15 48.1-15 73.7 0 20.6 3.2 40.6 9.5 59.9 6.4 19.3 15.4 36.8 27.2
                    52.3 11.7 15.6 25.4 29.2 41 41 15.6 11.7 33 20.8 52.3 27.2s39.3 9.5 59.9
                    9.5c25.7 0 50.3-5 73.7-15 23.5-10 43.7-23.5 60.7-40.5s30.5-37.3
                    40.5-60.7c10-23.5 15-48.1
15-73.7s-5-50.3-15-73.7c-10-23.5-23.5-43.7-40.5-60.7s-37.3-30.5-60.7-40.5-48-15-73.7-15zm-23.4
88.6c1.5-1.8 3.5-2.6 5.8-2.6s4.2 0.9 5.8 2.6l123.4 123.4c1.5 1.5 2.3 3.5 2.3
                    5.8s-0.8 4.3-2.3 6.1l-45.8 45.8c-1.5 1.5-3.5 2.3-5.8
                    2.3s-4.2-0.8-5.8-2.3l-72.1-72.1-27.7 28c-1.5 1.5-3.5 2.3-5.8
2.3s-4.3-0.8-6.1-2.3l-45.8-45.8c-1.5-1.8-2.3-3.7-2.3-5.9s0.8-4.2
                    2.3-5.9l79.9-79.4zm-700.8 23.7c-9 0-16.7 3.2-23.2 9.7s-9.7 14.2-9.7
                    23.2v44.8h483.9c0-26.1 3.8-52 11.5-77.7h-462.5zm230.4-712.4v329.2l-230.4
                    362.1h469.8c14-36.2 34.8-67.9 62.2-95.1l-169.9-267v-197.5l-131.7-131.7z"/>
                    </g>
                    </svg>
                </i>
                <span class="menu-button_text">Filter</span>
              </a>
              <search-grid-filter></search-grid-filter>
            </li>
          </ul>
        </div>
    </div>
  </form>
</template>

<script>
import SearchGridFilter from '@/components/SearchGridFilter';
import { SET_QUERY, SET_FILTER_IS_VISIBLE } from '@/store/mutation-types';

export default {
  name: 'search-grid-form',
  data: () => ({ searchTermsModel: null }),
  components: {
    SearchGridFilter,
  },
  computed: {
    searchTerms() {
      return this.$store.state.query.q;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
    isFilterApplied() {
      return this.$store.state.isFilterApplied;
    },
  },
  methods: {
    onSubmit(e) {
      e.preventDefault();
      if (this.searchTermsModel) {
        this.$store.commit(
          SET_QUERY,
          { query: { q: this.searchTermsModel }, shouldNavigate: true },
        );
      }
    },
    onToggleSearchGridFilter() {
      this.$store.commit(
        SET_FILTER_IS_VISIBLE,
        { isFilterVisible: !this.isFilterVisible },
      );
    },
    addScrollEvent() {
      this.removeScrollEvent = this.removeScrollEvent.bind(this);
      window.addEventListener('scroll', this.removeScrollEvent);
    },
    removeScrollEvent() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, { isFilterVisible: false });
      window.removeEventListener('scroll', this.removeScrollEvent);
    },
    setFormInput() {
      this.searchTermsModel = this.searchTerms;
    },
  },
  watch: {
    isFilterVisible: function handler(isFilterVisible) {
      if (isFilterVisible) this.addScrollEvent();
    },
    searchTerms: function handler() {
      this.setFormInput();
    },
  },
  mounted: function handler() {
    this.setFormInput();
  },
};
</script>

<style lang="scss" scoped>
  .search-filter {
    position: absolute;
    top: 82px !important;
    left: auto !important;
    right: 0 !important;
    border: 1px solid #e8e8e8;
  }

  .search-form {
    width: 100%;
    background: #fff;
    border-bottom: 1px solid #E6EAEA;
  }

  .search-filter:after,
  .search-filter:before {
    bottom: 100%;
    right: 30px;
    border: solid transparent;
    content: " ";
    height: 0;
    width: 0;
    position: absolute;
    pointer-events: none;
  }

  .search-filter:after {
    border-color: rgba(255, 255, 255, 0);
    border-bottom-color: #fff;
    border-width: 8px;
    margin-left: -8px;
    z-index: 100;
  }

  .search-filter:before {
    border-color: rgba(232, 232, 232, 0);
    border-bottom-color: #e8e8e8;
    border-width: 10px;
    margin-left: 0px;
    right: 28px;
  }

  .search-form_search-button {

    .menu-button_text {
      color: #35495e;
    }
  }

  .search-form_filter-button {
    position: relative;

    .menu-button_text {
      color: #35495e;
    }
  }
  .search-form_ctr {
    position: relative;
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
    flex-wrap: nowrap;
    flex-direction: row-reverse;

    li {
      border-left: 1px solid #E6EAEA;

      a {
        width: 80px;
        text-align: center;
      }
    }
  }

  @media screen and (max-width: 600px) {
    .search-form_input {
      font-size: 18px;
    }
  }
</style>
