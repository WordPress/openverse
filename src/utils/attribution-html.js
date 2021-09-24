function attributionHtml(image, openverseLicenseUrl, fullLicenseName) {
  if (!image) {
    return ''
  }
  const baseAssetsPath = 'https://search.creativecommons.org/static/img'
  const imgLink = `<a href="${image.foreign_landing_url}">"${image.title}"</a>`
  let creator = ''
  let imageTag = ''
  if (image.url && image.title) {
    imageTag = `<img style="display: block;" src="${image.url}" alt="${image.title}">`
  }
  if (image.creator && image.creator_url) {
    creator = `<span> by <a href="${image.creator_url}">${image.creator}</a></span>`
  } else if (image.creator && !image.creator_url) {
    creator = `<span> by <span>${image.creator}</span></span>`
  }
  const licenseLink = ` is licensed under <a href="${ccLicenseUrl}" style="margin-right: 5px;">${fullLicenseName.toUpperCase()}</a>`

  let licenseIcons = `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc_icon.svg?image_id=${image.id}" />`
  if (image.license) {
    licenseIcons += image.license
      .split('-')
      .map(
        (license) =>
          `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc-${license.toLowerCase()}_icon.svg" />`
      )
      .join('')
  }

  const licenseImgLink = `<a href="${ccLicenseUrl}" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;">${licenseIcons}</a>`
  return `<p style="font-size: 0.9rem;font-style: italic;">${imageTag}${imgLink}${creator}${licenseLink}${licenseImgLink}</p>`
}

export default attributionHtml
