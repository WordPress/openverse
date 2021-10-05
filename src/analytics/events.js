import { Event } from './google-analytics'

export function CopyAttribution(type, text) {
  return new Event('Attribution Copy', type, text)
}

export function DonateLinkClick(location) {
  return new Event('Donation', 'Click', location)
}

export function DonateBannerClose() {
  return new Event('Donation', 'Close')
}
