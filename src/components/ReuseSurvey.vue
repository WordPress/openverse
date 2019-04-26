<template>
  <div class="reuse-survey">
    <span>How are you using this image?</span>
    <span>If you intend to use this image, you can answer</span>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeSApxNMup8Ujt-8Vjv53ngltzhJeaHspMykHCD8VKQ39yXAA/viewform">
      this quick survey here
    </a>
    <span>to let us know how you are using it.</span>
  </div>
</template>

<script>
export default {
  name: 'reuse-survey',
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
