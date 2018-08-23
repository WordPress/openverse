<template>
  <div class="share-list-page grid-x">
      <div class="cell">
        <header-section showNavSearch="true" fixedNav="true"></header-section>
      </div>
      <div class="cell small-11 medium-11 large-11 grid-padding-x  share-list">
        <header class="share-list_header">
          <h1 class="header-title">
            {{ id }} list
          </h1>
        </header>
        <div class="share-list_items">
          <div v-for="(image, index) in shareListImages"
            :class="{ 'search-list_item': true, 'search-grid_ctr__active': image.isActive }"
            :key="index">
          <router-link :to="{ name: 'photo-detail-page', params: { id: image.id }}">
            <article class="article-row">
              <div class="article-row-img">
                <img class="share-list_image" :src="image.thumbnail || image.url">
              </div>
              <div class="article-row-content">
                <h2 class="article-row-content-header">{{ image.title }}</h2>
                <p class="article-row-content-author">By {{ image.creator }}</p>
                <p class="article-row-content-license">
                  License CC {{ image.license}} {{ image.license_version }}
                </p>
                <p class="article-row-content-author">Provider {{ image.provider }}</p>
              </div>
            </article>
          </router-link>
        </div>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import SearchGridForm from '@/components/SearchGridForm';
import { FETCH_LIST } from '@/store/action-types';

const ShareListPage = {
  name: 'share-list-page',
  components: {
    HeaderSection,
    SearchGridForm,
    FooterSection,
  },
  props: {
    id: null,
  },
  computed: {
    shareListImages() {
      return this.$store.state.shareListImages;
    },
  },
  created() {
    this.$store.dispatch(FETCH_LIST, { id: this.id });
  },
};

export default ShareListPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">

@import '../styles/app';

.share-list_header {
  border-top: 1px solid #e7e8e9;
}

.search-list_item:first-of-type .article-row {
  border-top: none;
}

.header-title {
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
}

.share-list {
  min-height: 450px;
  margin: 45px auto;
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
