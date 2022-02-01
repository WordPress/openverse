<template>
  <div v-if="license">
    <ul>
      <li
        v-for="(li, index) in splitLicenses"
        :key="index"
        class="flex items-start my-2"
      >
        <i
          aria-hidden="true"
          class="icon me-2 text-black text-3xl bg-white"
          :class="`cc-${getLicenseIcon(li)}`"
          :title="`${li.toUpperCase()}`"
        />
        <span class="sr-only">{{ li.toUpperCase() }}</span>
        <p class="text-sm">
          {{ $t(`browse-page.license-description.${li}`) }}
        </p>
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
