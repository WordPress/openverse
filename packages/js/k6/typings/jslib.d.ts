declare module "https://jslib.k6.io/k6-summary/0.1.0/index.js" {
  export type MetricSummary = Record<string, number> & {
    thresholds?: Record<string, boolean>
  }
  export interface Check {
    name: string
    path: string
    id: string
    passes: number
    fails: number
  }

  export interface Group {
    groups: Record<string, Group>
    checks: Record<string, Check>
    name: string
    path: string
    id: string
  }

  export interface SummaryData {
    metrics: Record<string, MetricSummary>
    root_group: Group
  }

  export interface TextOptions {
    enableColors: boolean
  }

  export interface JUnitOptions {
    name: string
    classname: string
  }

  export function textSummary(
    data: SummaryData,
    options?: Partial<TextOptions>
  ): string
  export function jUnit(
    data: SummaryData,
    options?: Partial<JUnitOptions>
  ): string
}

declare module "https://jslib.k6.io/k6-utils/1.2.0/index.js" {
  export function check<T>(
    val: T,
    checks: Record<string, (val: T) => Promise<boolean> | boolean>,
    tags?: Record<string, string>
  ): Promise<boolean>
  export function randomIntBetween(min: number, max: number): number
  export function randomItem<T>(array: T[]): T
  export function randomString(length: number, charset?: string): string
  export function uuidv4(): string
  export function findBetween(
    content: string,
    left: string,
    right: string,
    repeat: boolean
  ): string
  export function normalDistributionStages(
    maxVus: number,
    durationSeconds: number,
    numberOfStages?: number
  ): { duration: string; target: number }[]
  export function getCurrentStageIndex(): number
  export function tagWithCurrentStageIndex(): void
  export function tagWithCurrentStageProfile(): void
}
