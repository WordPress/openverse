import { INCLUDE_SENSITIVE_QUERY_PARAM } from "~/constants/content-safety"

export type Collection = "tag" | "creator" | "source"
export type SearchStrategy = "default" | Collection

/**
 * The filter query parameters.
 */
export interface SearchFilterQuery {
  license?: string
  license_type?: string
  extension?: string
  size?: string
  aspect_ratio?: string
  category?: string
  source?: string
  length?: string
  [INCLUDE_SENSITIVE_QUERY_PARAM]?: string
  /**
   * A conditional to show audio waveform data.
   * TODO:  We'll need new types that accept a media type to allow media-specific params
   */
  peaks?: string
}

export type SearchFilterKeys = keyof SearchFilterQuery
export type SearchRequestQuery = { q: string }

interface PaginatedParams {
  page?: string
}

/**
 * Query parameters for the search request, includes filters and `q` param.
 */
export type SearchQuery = SearchFilterQuery & SearchRequestQuery
/**
 * Query parameters for the search request, includes filters, `q` and `page` params.
 */
export type PaginatedSearchQuery = SearchRequestQuery &
  PaginatedParams &
  SearchFilterQuery

export type PaginatedCollectionQuery = PaginatedParams & {
  [key: string]: string
}

export type TagCollection = { collection: "tag"; tag: string }
export type CreatorCollection = {
    collection: "creator"
    source: string
    creator: string
}
export type SourceCollection = { collection: "source"; source: string }

export type CollectionParams =
    | TagCollection
    | CreatorCollection
    | SourceCollection
