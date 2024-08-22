import { type SupportedSearchType, IMAGE, AUDIO } from "~/constants/media"
import type { AudioDetail, ImageDetail } from "~/types/media"
import type { ResultKind, Results } from "~/types/result"

export type SingleResultProps = {
  kind: ResultKind
  searchTerm: string
  relatedTo?: string
}
export type CommonCollectionProps = SingleResultProps & {
  collectionLabel: string
}

export type MediaCollectionComponentProps = CommonCollectionProps & {
  results: Results
  /**
   * Overrides the value from the media store.
   * Used for the related media which uses a different store.
   */
  isFetching: boolean
}

export type CollectionComponentProps<T extends SupportedSearchType> =
  CommonCollectionProps & {
    results: T extends typeof IMAGE
      ? ImageDetail[]
      : T extends typeof AUDIO
        ? AudioDetail[]
        : (ImageDetail | AudioDetail)[]
  }
