<template>
  <div v-if="license">
    <ul class="my-2">
      <li
        v-for="(li, index) in splitLicenses"
        :key="index"
        class="license-element"
      >
        <i
          aria-hidden="true"
          :class="`icon cc-${getLicenseIcon(li)}`"
          :title="`${li.toUpperCase()}`"
        />
        <span class="sr-only">{{ li.toUpperCase() }}</span>
        <p>{{ $t(`browse-page.license-description.${li}`) }}</p>
      </li>
    </ul>
  </div>
</template>

<script>
const APItoIconNameMap = {
  by: 'by',
  nc: 'nc',
  nd: 'nd',
  sa: 'sa',
  cc0: 'zero',
  pdm: 'pd',
}

const LicenseElements = {
  name: 'license-elements',
  props: {
    license: {
      type: String,
      default: '',
    },
  },
  computed: {
    splitLicenses() {
      return this.$props.license.split('-')
    },
  },
  methods: {
    getLicenseIcon(licenseTerm) {
      return APItoIconNameMap[licenseTerm]
    },
  },
}

export default LicenseElements
</script>
<style lang="scss" scoped>
li {
  display: flex;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: flex-start;
}
li p {
  line-height: 22px;
}
i {
  color: black;
  background-color: white;
  font-size: 1.43rem;
  margin-right: 0.5rem;
}
.tooltip li {
  align-items: flex-start;
  line-height: 1.5;
}
</style>
