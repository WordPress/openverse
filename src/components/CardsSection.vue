<template class="cards">
  <div class="cards row">
    <div class="grid-container">
      <div class="grid-x grid-padding-x small-up-1 medium-up-2 large-up-4">
        <div class="cell"
             v-for="(tag, index) in tags"
             @click="gotoBrowsePage(tag.tagName)"
             :key="index">
          <div class="card">
            <div class="card-text">
              {{ tag.tagName }}
            </div>
            <div class="card-image">
              <img :src="tag.tagImageSrc">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'cards-section',
  data: () => ({
    tags: [
      {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'Sunset',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      },
    ],
  }),
  methods: {
    gotoBrowsePage: (tagName) => {
      // eslint-disable-next-line no-console
      console.log(tagName);
    },
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  .cards {
    margin-top: 50px;
  }

  .card {
    position: relative;
    border-radius: 5px;
    cursor: pointer;
  }

  .card:after {
    background: linear-gradient(to top, rgba(0, 0, 0, 0.1) 0%, rgba(17, 17, 17, 0.7) 100%);
    content: '';
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 0;
  }

  .card-text {
    color: #fff;
    position: absolute;
    padding: 5px 15px;
    border: 1px solid #fff;
    position: absolute;
    left: 50%;
    transform: translateX(-50%) translateY(-50%);
    top: 50%;
    border-radius: 3px;
    z-index: 1;
  }
</style>
