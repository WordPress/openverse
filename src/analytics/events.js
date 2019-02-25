import { Event } from './GoogleAnalytics';

export function CopyTextAttribution(text) {
  return new Event('Attribution', 'Copy Text', text);
}

export function CopyHtmlAttribution(text) {
  return new Event('Attribution', 'Copy HTML', text);
}
