function attributionHtml(image, ccLicenseURL, fullLicenseName) {
  if (!image) {
    return '';
  }
  const baseAssetsPath = 'https://search.creativecommons.org/static/img';
  const imgLink = `<a href="${image.foreign_landing_url}">"${image.title}"</a>`;
  let creator = '';
  if (image.creator && image.creator_url) {
    creator = `<span> by <a href="${image.creator_url}">${image.creator}</a></span>`;
  }
  else if (image.creator && !image.creator_url) {
    creator = `<span> by <span>${image.creator}</span></span>`;
  }
  const licenseLink = ` is licensed under <a href="${ccLicenseURL}" style="margin-right: 5px;">${fullLicenseName.toUpperCase()}</a>`;

  let licenseIcons = `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc_icon.svg" />`; // eslint-disable-line global-require, import/no-dynamic-require
  if (image.license) {
    licenseIcons += image.license.split('-').map(license =>
      `<img style="height: inherit;margin-right: 3px;display: inline-block;" src="${baseAssetsPath}/cc-${license.toLowerCase()}_icon.svg" />`, // eslint-disable-line global-require, import/no-dynamic-require
    ).join('');
  }

  const licenseImgLink = `<a href="${ccLicenseURL}" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;opacity: 1.0;margin-top: 2px;margin-left: 3px;height: 22px !important;">${licenseIcons}</a>`;
  return `<p style="font-size: 0.9rem;font-style: italic;">${imgLink}${creator}${licenseLink}${licenseImgLink}</p>`;
}

export default attributionHtml;
