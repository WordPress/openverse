import type { Media } from '~/models/media'
import {
  getElements,
  getFullLicenseName,
  isPublicDomain,
} from '~/utils/license'
import type { LicenseElement } from '~/constants/license'

import type VueI18n from 'vue-i18n'

/* Helper functions */

/**
 * Create an HTML tag with the given name, attributes and children.
 *
 * @param name - the tag name
 * @param attrs - the attributes associated with the tag
 * @param children - the tags children
 * @returns the HTML markup of the tag
 */
const h = (
  name: string,
  attrs: Record<string, string>,
  children: string[] | null = null
): string => {
  const map = Object.entries(attrs)
    .map(([key, value]) => `${key}="${value}"`)
    .join(' ')
  const opening = map ? `<${name} ${map}>` : `<${name}>`
  const closing = `</${name}>`
  return `${opening}${(children ?? []).join('\n')}${closing}`
}

/**
 * Get an `<img>` tag corresponding to a license element.
 *
 * @param licenseElement - the license element for which to get the `<img>` tag
 * @returns the HTML markup of the `<img>` tag
 */
const licenseElementImg = (licenseElement: LicenseElement): string => {
  const filename = licenseElement.replace('-', '.')
  const src = `https://mirrors.creativecommons.org/presskit/icons/${filename}.svg`
  return h('img', {
    src,
    style: 'height: 1em; margin-right: 0.125em; display: inline;',
  })
}

/**
 * Get an HTML `<a>` tag set up with the `target` and `rel` attributes.
 *
 * @param href - the link that the anchor tag should point to
 * @param text - the textual content of the anchor tag
 * @returns the HTML markup of the `<a>` tag
 */
const extLink = (href: string, text: string) =>
  h('a', { target: '_blank', rel: 'noopener noreferrer', href }, [text])

/* Interfaces */

/**
 * This interface describes a subset of media that contains fields necessary
 * for generating a proper attribution.
 */
export type AttributableMedia = Pick<
  Media,
  | 'title'
  | 'foreign_landing_url'
  | 'creator'
  | 'creator_url'
  | 'license'
  | 'license_version'
  | 'license_url'
>

/**
 * This interface describes the options that the `getAttribution` function can
 * take to customise its output.
 */
export interface AttributionOptions {
  includeIcons?: boolean
  isPlaintext?: boolean
}

/* Actual util */

/**
 * Get the HTML markup for properly attributing the given media item.
 *
 * @param mediaItem - the media item being attributed
 * @param i18n - the i18n instance to access translations
 * @param includePreview - whether to include the preview markup in the HTML
 * @returns the HTML markup of the attribution
 */
export const getAttribution = (
  mediaItem: AttributableMedia,
  i18n: VueI18n | null = null,
  { includeIcons, isPlaintext }: AttributionOptions = {
    isPlaintext: false,
    includeIcons: true,
  }
): string => {
  if (!mediaItem) return ''

  /* Title */

  let titleLink = mediaItem.title || ''
  if (!isPlaintext && mediaItem.foreign_landing_url && titleLink)
    titleLink = extLink(mediaItem.foreign_landing_url, titleLink)

  /* Creator */

  let creatorLink = mediaItem.creator || ''
  if (!isPlaintext && mediaItem.creator_url && creatorLink)
    creatorLink = extLink(mediaItem.creator_url, creatorLink)

  /* License */

  const fullLicenseName = getFullLicenseName(
    mediaItem.license,
    mediaItem.license_version,
    i18n
  )
  let licenseIcons = ''
  if (includeIcons && mediaItem.license) {
    const elements = getElements(mediaItem.license)
    const icons = elements.map((element) => licenseElementImg(element))
    // Icons are only rendered if present for every element
    if (!icons.includes('')) {
      licenseIcons = icons.join('')
    }
  }

  let licenseLink = `${fullLicenseName} ${licenseIcons}`.trim()
  if (!isPlaintext && mediaItem.license_url) {
    licenseLink = extLink(`${mediaItem.license_url}?ref=openverse`, licenseLink)
  }

  /* Attribution */

  const i18nBase = 'media-details.reuse.credit'
  const isPd = isPublicDomain(mediaItem.license)

  let attribution: string
  if (i18n) {
    let fillers: Record<string, string> = {
      title: titleLink
        ? i18n.t(`${i18nBase}.actual-title`, { title: titleLink }).toString()
        : i18n.t(`${i18nBase}.generic-title`).toString(),
      creator: creatorLink
        ? i18n
            .t(`${i18nBase}.creator-text`, {
              'creator-name': creatorLink,
            })
            .toString()
        : '',
      'marked-licensed': i18n
        .t(`${i18nBase}.${isPd ? 'marked' : 'licensed'}`)
        .toString(),
      license: licenseLink,
    }
    if (isPlaintext) {
      fillers = {
        ...fillers,
        'view-legal': i18n
          .t(`${i18nBase}.view-legal-text`, {
            'terms-copy': i18n.t(
              `${i18nBase}.${isPd ? 'terms-text' : 'copy-text'}`
            ),
            URL: `${mediaItem.license_url}?ref=openverse`,
          })
          .toString(),
      }
    }
    attribution = i18n.t(`${i18nBase}.text`, fillers).toString()
  } else {
    const attributionParts = []
    attributionParts.push(titleLink ? `"${titleLink}"` : 'This work')
    if (creatorLink) attributionParts.push(' by ', creatorLink)
    attributionParts.push(
      isPd ? ' is marked with ' : ' is licensed under ',
      licenseLink,
      '.'
    )
    if (isPlaintext)
      attributionParts.push(
        ' To view ',
        isPd ? 'the terms,' : 'a copy of this license,',
        ' visit',
        mediaItem.license_url,
        '.'
      )

    attribution = attributionParts.join('')
  }
  return isPlaintext
    ? attribution
    : h('p', { class: 'attribution' }, [attribution])
}
