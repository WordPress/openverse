import { defineI18nConfig } from "#imports"

import localeFallback from "./locale-fallback.json"

import type { Locale } from "@intlify/core-base"

const custom5Rule = (n: number): number =>
  n == 0
    ? 0
    : n == 1
      ? 1
      : n == 2
        ? 2
        : n % 100 >= 3 && n % 100 <= 10
          ? 3
          : n % 100 >= 11 && n % 100 <= 99
            ? 4
            : 5

export default defineI18nConfig(() => ({
  legacy: false,
  globalInjection: true,
  fallbackLocale: localeFallback as { [x: string]: Locale[] },
  silentFallbackWarn: true,
  pluralizationRules: {
    ar: custom5Rule,
    arq: custom5Rule,
    ary: custom5Rule,
    bel: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    bs: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    cor: (n: number): number =>
      n == 0
        ? 0
        : n == 1
          ? 1
          : n % 100 == 2 ||
              n % 100 == 22 ||
              n % 100 == 42 ||
              n % 100 == 62 ||
              n % 100 == 82 ||
              (n % 1000 == 0 &&
                ((n % 100000 >= 1000 && n % 100000 <= 20000) ||
                  n % 100000 == 40000 ||
                  n % 100000 == 60000 ||
                  n % 100000 == 80000)) ||
              (n != 0 && n % 1000000 == 100000)
            ? 2
            : n % 100 == 3 ||
                n % 100 == 23 ||
                n % 100 == 43 ||
                n % 100 == 63 ||
                n % 100 == 83
              ? 3
              : n != 1 &&
                  (n % 100 == 1 ||
                    n % 100 == 21 ||
                    n % 100 == 41 ||
                    n % 100 == 61 ||
                    n % 100 == 81)
                ? 4
                : 5,
    cs: (n: number): number => (n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2),
    cy: (n: number): number =>
      n == 1 ? 0 : n == 2 ? 1 : n != 8 && n != 11 ? 2 : 3,
    dsb: (n: number): number =>
      n % 100 == 1
        ? 0
        : n % 100 == 2
          ? 1
          : n % 100 == 3 || n % 100 == 4
            ? 2
            : 3,
    ga: (n: number): number =>
      n == 1
        ? 0
        : n == 2
          ? 1
          : n >= 3 && n <= 6
            ? 2
            : n >= 7 && n <= 10
              ? 3
              : 4,
    gd: (n: number): number =>
      n == 1 || n == 11
        ? 0
        : n == 2 || n == 12
          ? 1
          : (n >= 3 && n <= 10) || (n >= 13 && n <= 19)
            ? 2
            : 3,
    hr: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    hsb: (n: number): number =>
      n % 100 == 1
        ? 0
        : n % 100 == 2
          ? 1
          : n % 100 == 3 || n % 100 == 4
            ? 2
            : 3,
    is: (n: number): number => (n % 10 != 1 || n % 100 == 11 ? 1 : 0),
    lt: (n: number): number =>
      n % 10 == 1 && (n % 100 < 11 || n % 100 > 19)
        ? 0
        : n % 10 >= 2 && n % 10 <= 9 && (n % 100 < 11 || n % 100 > 19)
          ? 1
          : 2,
    lv: (n: number): number =>
      n % 10 == 0 || (n % 100 >= 11 && n % 100 <= 19)
        ? 0
        : n % 10 == 1 && n % 100 != 11
          ? 1
          : 2,
    me: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)
          ? 1
          : 2,
    mk: (n: number): number => (n % 10 != 1 || n % 100 == 11 ? 1 : 0),
    pl: (n: number): number =>
      n == 1
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    ro: (n: number): number =>
      n == 1 ? 0 : n == 0 || (n % 100 >= 2 && n % 100 <= 19) ? 1 : 2,
    ru: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    sk: (n: number): number => (n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2),
    sl: (n: number): number =>
      n % 100 == 1
        ? 0
        : n % 100 == 2
          ? 1
          : n % 100 == 3 || n % 100 == 4
            ? 2
            : 3,
    sr: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
    szl: (n: number): number =>
      n == 1 ? 0 : n % 10 >= 2 && n % 10 <= 4 && n % 100 == 20 ? 1 : 2,
    uk: (n: number): number =>
      n % 10 == 1 && n % 100 != 11
        ? 0
        : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14)
          ? 1
          : 2,
  },
}))
