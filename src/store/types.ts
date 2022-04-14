export interface ApiQueryParams {
  q?: string
  license?: string
  license_type?: string
  extension?: string
  size?: string
  aspect_ratio?: string
  searchBy?: string
  categories?: string
  source?: string
  duration?: string
  mature?: string
  page?: string
}
export type ApiQueryFilters = Omit<ApiQueryParams, 'q'>
export type ApiQueryKeys = keyof ApiQueryFilters
