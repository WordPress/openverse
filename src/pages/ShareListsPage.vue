<template>
  <div class="share-lists-page grid-x">
    <div class="cell">
      <header-section showNavSearch="true" fixedNav="true"></header-section>
    </div>
    <div class="cell
                small-11
                medium-11
                large-11
                grid-padding-x
                share-lists">
      <header class="share-lists_header">
        <h1 class="share-lists_header-title">
          Lists
        </h1>
      </header>
      <div class="share-lists_items">
        <div v-for="(list, index) in lists" class="search-list_item" :key="index">
          <article class="article-row" @click.stop="onGotoListPage(list)">
            <div class="article-row-img">
              <img class="share-list_image" :src="list.thumbnail">
            </div>
            <div class="article-row-content">
              <h2 class="article-row-content-header">{{ list.listID }}</h2>
              <a @click.stop="onRemoveImage(list)"
                 class="share-list_remove-btn">Remove list</a>
            </div>
          </article>
        </div>
        <div class="callout warning" v-if="lists && lists.length === 0">
          <h5>You currently don't have any saved lists.</h5>
          <p>Start by creating a list on the <a href="/search?q=nature">Search page.</a></p>
        </div>
      </div>
    </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchGridForm from '@/components/SearchGridForm';
import { FETCH_LISTS, REMOVE_LIST } from '@/store/action-types';

const ShareListPage = {
  name: 'share-list-page',
  components: {
    HeaderSection,
    SearchGridForm,
    FooterSection,
  },
  data: () => ({
    authToken: null,
    imageURL: '',
  }),
  computed: {
    lists() {
      return this.$store.state.shareLists;
    },
    shareURL() {
      return window.location;
    },
    shareText() {
      return encodeURI(`I created an image list @creativecommons: ${this.shareURL}`);
    },
  },
  created() {
    this.$store.dispatch(FETCH_LISTS);
  },
  methods: {
    onGotoListPage(list) {
      this.$router.push(`/lists/${list.listID}`);
    },
    onRemoveImage(list) {
      this.$store.dispatch(REMOVE_LIST,
        { auth: list.auth,
          listID: list.listID,
        },
      );
    },
  },
};

export default ShareListPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped="true">

@import '../styles/app';

.share-lists {
  min-height: 450px;
  margin: 45px auto;
}

.share-lists_remove-btn {
  color: red;
  display: block;

  before: {
    content: '';
    background: url('../assets/remove-icon.svg') center center no-repeat;
  }
}

.share-lists_header {
  position: relative;
  border-top: 1px solid #e7e8e9;
}

.search-list_item {
  cursor: pointer;
}

.search-list_item:first-of-type .article-row {
  border-top: none;
}

.share-lists_header-title {
  position: relative;
  margin-bottom: 1.07142857em;
  font-size: 1em;
  font-weight: 600;
  letter-spacing: 1px;
  line-height: 1.25;
  text-transform: uppercase;
  display: inline-block;
  padding-top: .28571429em;
  border-top: 5px solid rgba(29, 31, 39, 0.8);
  margin-top: -3px;
  margin-right: 60px;
  vertical-align: text-bottom;
}

.share-lists .social-share {
  display: inline-block;
}

.share-list_remove-btn {
  color: red;
  display: block;

  before: {
    content: '';
    background: url('../assets/remove-icon.svg') center center no-repeat;
  }
}

.share-lists_social-items .social-button {
  width: 1.6rem;
  height: 1.6rem;
}

.article-row-section {
  @include flex-grid-row(null, $global-width, 12);
  justify-content: center;
}

.article-row-section-inner {
  @include flex-grid-column(12);

  @include breakpoint(medium) {
    @include flex-grid-column(10);
  }
}

.article-row-section-header {
  padding: 1.5rem 0;
  margin: 0;
  line-height: 1;
}

.article-row {
  display: flex;
  flex-direction: column;
  border-top: 1px solid $light-gray;
  padding: 1.5rem 0;

   @include breakpoint(medium) {
    flex-direction: row;
  }

  &:hover {
    .article-row-content-header {
      color: #1779ba;
    }
  }
}

.article-row-img img {
  width: 100%;

  @include breakpoint(medium) {
    max-width: 300px;
    width: auto;
  }
}

.article-row-content {
  padding: 1.5rem 0 0;
  color: $body-font-color;

  @include breakpoint(medium) {
    padding: 0 0 0 1.5rem;
  }
}

.article-row-content-header {
  font-size: 1.5rem;
}

.article-row-content-description {
  font-size: 1.25rem;
}

.article-row-content-author,
.article-row-content-time,
.article-row-content-license {
  font-size: 0.875rem;
  margin-bottom: 0;
  color: $dark-gray;
}

.article-row-content-license a:hover {
  text-decoration: underline;
}
</style>
