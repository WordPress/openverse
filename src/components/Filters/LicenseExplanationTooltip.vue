<template>
  <div class="license-explanation-tooltip padding-small margin-top-small">
    <h5 class="b-header">License CC {{ license.toUpperCase() }}</h5>

    <license-explanations :license="license" />
  </div>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations';

export default {
  name: 'license-explanation-tooltip',
  props: ['license'],
  components: {
    LicenseExplanations,
  },
};
</script>

<style lang="scss" scoped>
// from http://www.cssarrowplease.com/
.license-explanation-tooltip {
  position: absolute;
  background: #ffffff;
  border: 2px solid #D8D8D8;
  z-index: 10;
  width: 20rem;
  box-shadow: 10px 10px 10px -10px rgba(0,0,0,0.25);
}
.license-explanation-tooltip:after, .license-explanation-tooltip:before {
  bottom: 100%;
  left: 10%;
  border: solid transparent;
  content: " ";
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}

.license-explanation-tooltip:after {
  border-color: rgba(255, 255, 255, 0);
  border-bottom-color: #ffffff;
  border-width: 10px;
  margin-left: 258px;
}
.license-explanation-tooltip:before {
  border-color: rgba(120, 120, 120, 0);
  border-bottom-color: #D8D8D8;
  border-width: 13px;
  margin-left: 255px;
}
</style>
