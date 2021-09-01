// The default fallback for the flags is used for running ests regarding the PhotoDetailPage
const flags = {
  socialSharing: process.env.SOCIAL_SHARING === 'ENABLED',
}

export default flags
