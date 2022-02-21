<template>
  <VNoticeBar>
    {{ $t('migration-notice.intro') }}
    <i18n tag="span" path="migration-notice.more">
      <template #read-more>
        <VLink
          class="text-dark-blue hover:text-dark-blue underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
          >{{ $t('migration-notice.read') }}</VLink
        >
      </template>
    </i18n>
  </VNoticeBar>
</template>

<script>
import VNoticeBar from '~/components/VNoticeBar/VNoticeBar.vue'
import VLink from '~/components/VLink.vue'

export default {
  name: 'VMigrationNotice',
  components: { VLink, VNoticeBar },
}
</script>
