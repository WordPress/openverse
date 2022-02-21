<template>
  <div class="reuse-survey caption mt-1">
    {{ $t('photo-details.survey.content') }}
    <VLink
      :href="formLink"
      @click="onReuseSurveyClick"
      @keyup.enter="onReuseSurveyClick"
    >
      {{ $t('photo-details.survey.link') }}
    </VLink>
    {{ $t('photo-details.survey.answer') }}
  </div>
</template>

<script>
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/constants/usage-data-analytics-types'
import { USAGE_DATA } from '~/constants/store-modules'
import VLink from '~/components/VLink.vue'

const reuseForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSegPUDIUj_odzclJhhWRfPumSfbHtXDVDCHqRfFl7ZS8cMn2g/viewform'
const imageLinkEntry = '2039681354'

export default {
  name: 'ReuseSurvey',
  components: { VLink },
  props: ['image'],
  data: () => ({
    location: '',
  }),
  computed: {
    formLink() {
      const location = this.location
      return `${reuseForm}?entry.${imageLinkEntry}=${location}`
    },
  },
  mounted() {
    this.location = window.location.href
  },
  methods: {
    onReuseSurveyClick() {
      this.$store.dispatch(`${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`, {
        eventType: DETAIL_PAGE_EVENTS.REUSE_SURVEY,
        resultUuid: this.$props.image.id,
      })
    },
  },
}
</script>
