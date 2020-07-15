<template>
  <div>
    <search-grid-manual-load :query="query" @onLoadMoreImages="onLoadMoreImages" />
    <ScrollButton :showBtn="showScrollButton " />
  </div>
</template>

<script>
import SearchGridManualLoad from '@/components/SearchGridManualLoad';
import ScrollButton from '@/components/ScrollButton';

export default {
  name: 'search-grid',
  components: {
    SearchGridManualLoad,
    ScrollButton,
  },
  props: ['query'],
  data: () => ({
    showScrollButton: false,
  }),
  methods: {
    onLoadMoreImages(searchParams) {
      this.$emit('onLoadMoreImages', searchParams);
    },
    checkScrollLength() {
      if (window.scrollY > 70) this.showScrollButton = true;
      else this.showScrollButton = false;
    },
  },
  mounted() {
    document.addEventListener('scroll', this.checkScrollLength);
  },
  beforeDestroy() {
    document.removeEventListener('scroll', this.checkScrollLength);
  },
};
</script>
