<template>
  <VNoticeBar>
    {{ $t('migration-notice.intro') }}
    <i18n tag="span" path="migration-notice.more">
      <template #read-more>
        <a
          class="text-dark-blue hover:text-dark-blue underline"
          href="https://wordpress.org/news/2021/05/welcome-to-openverse/"
          target="_blank"
          >{{ $t('migration-notice.read') }}</a
        >
      </template>
    </i18n>
  </VNoticeBar>
</template>

<script>
import VNoticeBar from '~/components/VNoticeBar/VNoticeBar.vue'

export default {
  name: 'VMigrationNotice',
  components: { VNoticeBar },
}
</script>
