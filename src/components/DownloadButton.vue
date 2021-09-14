<template>
  <DropdownButton v-if="filesizes">
    <template #default="{ buttonProps }">
      <a
        v-bind="buttonProps"
        class="whitespace-nowrap"
        :href="selectedFormat.download_url"
        download=""
      >
        <span>{{ $t('download-button.download') }}</span>
        <span class="ml-4 selected-format">
          {{ selectedFormat.extension_name }}
        </span>
        <span class="ml-1 font-thin">{{
          getFormatSize(selectedFormat.extension_name)
        }}</span>
      </a>
    </template>

    <template
      #items="{
        activeItemClass,
        itemClass,
        itemA11yProps,
        toggleOpen,
        onItemKeydown,
      }"
    >
      <ul>
        <li v-for="format in formats" :key="format.name">
          <button
            class="flex justify-between w-full"
            :class="[
              itemClass,
              selectedFormat.extension_name === format.extension_name
                ? activeItemClass
                : '',
            ]"
            type="button"
            v-bind="itemA11yProps"
            @click="
              setSelectedFormat(format)
              toggleOpen()
            "
            @keydown="onItemKeydown"
          >
            <span class="font-bold mr-2">{{ format.extension_name }}</span>
            <span>{{ getFormatSize(format.extension_name) }}</span>
          </button>
        </li>
      </ul>
    </template>
  </DropdownButton>
</template>

<script>
import filesize from 'filesize'
import axios from 'axios'

const LS_DOWNLOAD_FORMAT_EXTENSION_KEY = 'openverse:download-format-extension'

export default {
  name: 'DownloadButton',
  props: {
    formats: {
      type: Array,
      required: true,
      validator: (formats) => {
        const properties = ['extension_name', 'download_url', 'filesize']
        return formats.every((format) => properties.every((p) => p in format))
      },
    },
  },
  data() {
    const savedFormatExtension =
      localStorage.getItem(LS_DOWNLOAD_FORMAT_EXTENSION_KEY) ?? null
    let format = this.formats[0]
    if (savedFormatExtension) {
      const found = this.formats.find(
        (format) => format.extension_name === savedFormatExtension
      )
      if (found) {
        format = found
      }
    }

    return { selectedFormat: format, filesizes: null }
  },
  async fetch() {
    const extensionsToFilesizes = await Promise.all(
      this.formats.map(async (format) => {
        try {
          const response = await axios.head(format.download_url)
          return [format.extension_name, response.headers['content-length']]
        } catch (e) {
          return [format.extension_name, undefined]
        }
      })
    )

    this.filesizes = extensionsToFilesizes.reduce(
      (acc, [extensionName, filesize]) => ({
        ...acc,
        [extensionName]: filesize,
      }),
      {}
    )
  },
  methods: {
    getFormatSize(extensionName) {
      const size = this.filesizes?.[extensionName] ?? undefined
      if (typeof size === 'undefined') return ''

      return filesize(size, { locale: this.$i18n.locale })
    },
    setSelectedFormat(format) {
      localStorage.setItem(
        LS_DOWNLOAD_FORMAT_EXTENSION_KEY,
        format.extension_name
      )
      this.selectedFormat = format
    },
  },
}
</script>
