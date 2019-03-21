import { Event } from './GoogleAnalytics';

export function CopyTextAttribution(text) {
  return new Event('Attribution', 'Copy Text', text);
}

export function CopyHtmlAttribution(text) {
  return new Event('Attribution', 'Copy HTML', text);
}

export function DownloadWatermark(params) {
  let label = 'Download watermark';

  if (params.shouldWatermark) {
    label = `${label} | In Attribution Frame`;
  }
  if (params.shouldEmbedMetadata) {
    label = `${label} | With Attribution Metadata`;
  }

  return new Event('Download', label, params.imageId);
}
