<template>
  <div class="reuse-survey caption has-text-weight-semibold">
    {{ $t('photo-details.survey.content') }}
    <a
      :href="formLink"
      target="_blank"
      rel="noopener"
      @click="onReuseSurveyClick"
      @keyup.enter="onReuseSurveyClick"
    >
      {{ $t('photo-details.survey.link') }}
    </a>
    {{ $t('photo-details.survey.answer') }}
  </div>
</template>

<script>
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'

const reuseForm =
  'https://docs.google.com/forms/d/e/1FAIpQLSegPUDIUj_odzclJhhWRfPumSfbHtXDVDCHqRfFl7ZS8cMn2g/viewform'
const imageLinkEntry = '2039681354'

export default {
  name: 'ReuseSurvey',
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
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.REUSE_SURVEY,
        resultUuid: this.$props.image.id,
      })
    },
  },
}
</script>
