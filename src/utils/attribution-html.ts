import type { Media } from '~/models/media'

const linkProperties = 'target="_blank" rel="noopener noreferrer"'

function getAttributionHtml(
  media: Media,
  licenseUrl: string,
  fullLicenseName: string
) {
  if (!media) {
    return ''
  }
  const baseAssetsPath = 'https://search.openverse.engineering/static/img'
  const imgLink = `<a href="${media.foreign_landing_url}" ${linkProperties}>"${media.title}"</a>`
  let creator = ''
  let mediaTag = ''
  if (media.url && media.title) {
    mediaTag = `<img style="display: block;" src="${media.url}" alt="${media.title}">`
  }
  if (media.creator && media.creator_url) {
    creator = `<span> by <a href="${media.creator_url}" ${linkProperties}>${media.creator}</a></span>`
  } else if (media.creator && !media.creator_url) {
    creator = `<span> by <span>${media.creator}</span></span>`
  }
  const licenseLink = ` is licensed under <a href="${licenseUrl}" style="margin-right: 5px;" ${linkProperties}>${fullLicenseName.toUpperCase()}</a>`

  let licenseIcons = `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc_icon.svg?media_id=${media.id}" />`
  if (media.license) {
    licenseIcons += media.license
      .split('-')
      .map(
        (license) =>
          `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc-${license.toLowerCase()}_icon.svg" />`
      )
      .join('')
  }

  const licenseImgLink = `<a href="${licenseUrl}" ${linkProperties} style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;">${licenseIcons}</a>`
  return `<p style="font-size: 0.9rem;font-style: italic;">${mediaTag}${imgLink}${creator}${licenseLink}${licenseImgLink}</p>`
}

/**
 * Get the HTML markup for attributing the given media item.
 *
 * @param mediaItem - the media item, image or audio from the API, to attribute
 * @returns the HTML markup of the attribution
 */
export const getAttributionMarkup = (mediaItem: Media) => {
  if (!mediaItem) return ''

  const extLink = (href: string, text: string) =>
    `<a rel="noopener noreferrer" target="_blank" href="${href}">${text}</a>`

  let title = `"${mediaItem.title}"`
  if (mediaItem.foreign_landing_url) {
    title = extLink(mediaItem.foreign_landing_url, title)
  }

  let creator = mediaItem.creator
  if (mediaItem.creator_url) {
    creator = extLink(mediaItem.creator_url, creator)
  }

  let license = `${mediaItem.license} ${mediaItem.license_version}`
  license = extLink(mediaItem.license_url, license.toUpperCase())

  return `${title} by ${creator} is licensed under ${license}.`
}

export default getAttributionHtml
