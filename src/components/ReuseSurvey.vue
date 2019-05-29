<template>
  <div class="reuse-survey">
    <span>How are you using this image?</span>
    <span>Let us know how you use this image in</span>
    <a :href="formLink">
      this quick survey
    </a>
  </div>
</template>

<script>
export default {
  name: 'reuse-survey',
  computed: {
    formLink() {
      const location = window.location.href;
      return `https://docs.google.com/forms/d/e/1FAIpQLSeSApxNMup8Ujt-8Vjv53ngltzhJeaHspMykHCD8VKQ39yXAA/viewform?usp=pp_url&entry.1690035721=${location}`;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';

  .reuse-survey {
    margin: 2rem 0 2rem;

    span:first-child {
      font-size: 1.1rem;
      font-weight: 600;
      display: block;
    }
  }
</style>
