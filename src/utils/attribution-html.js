function getAttributionHtml(media, licenseUrl, fullLicenseName) {
  if (!media) {
    return ''
  }
  const baseAssetsPath = 'https://search.creativecommons.org/static/img'
  const imgLink = `<a href="${media.foreign_landing_url}">"${media.title}"</a>`
  let creator = ''
  let mediaTag = ''
  if (media.url && media.title) {
    mediaTag = `<img style="display: block;" src="${media.url}" alt="${media.title}">`
  }
  if (media.creator && media.creator_url) {
    creator = `<span> by <a href="${media.creator_url}">${media.creator}</a></span>`
  } else if (media.creator && !media.creator_url) {
    creator = `<span> by <span>${media.creator}</span></span>`
  }
  const licenseLink = ` is licensed under <a href="${licenseUrl}" style="margin-right: 5px;">${fullLicenseName.toUpperCase()}</a>`

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

  const licenseImgLink = `<a href="${licenseUrl}" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;">${licenseIcons}</a>`
  return `<p style="font-size: 0.9rem;font-style: italic;">${mediaTag}${imgLink}${creator}${licenseLink}${licenseImgLink}</p>`
}

export default getAttributionHtml
