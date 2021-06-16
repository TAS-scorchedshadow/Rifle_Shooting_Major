import { quantilesType7 } from './quantiles';

export interface IBoxPlot {
  /**
   * minimum value in the given data
   */
  readonly min: number;
  /**
   * maximum value in the given data
   */
  readonly max: number;
  /**
   * median value in the given data
   */
  readonly median: number;
  /**
   * 25% quantile
   */
  readonly q1: number;
  /**
   * 75% quantile
   */
  readonly q3: number;

  /**
   * inter quantile range (q3 - q1)
   */
  readonly iqr: number;
  /**
   * whisker / fence below the 25% quantile (lower one)
   * by default is computed as the smallest element that satisfies (e >= q1 - 1.5IQR && e <= q1)
   */
  readonly whiskerLow: number;
  /**
   * whisker / fence above the 75% quantile (upper one)
   * by default is computed as the largest element that satisfies (e <= q3 + 1.5IQR && e >= q1)
   */
  readonly whiskerHigh: number;
  /**
   * outliers that are outside of the whiskers on both ends
   */
  readonly outlier: readonly number[];

  /**
   * arithmetic mean
   */
  readonly mean: number;

  /**
   * number of missing values (NaN, null, undefined) in the data
   */
  readonly missing: number;
  /**
   * number of values (valid + missing)
   */
  readonly count: number;
  /**
   * array like (array or typed array) of all valid items
   */
  readonly items: ArrayLike<number>;
}

export declare interface QuantileMethod {
  (arr: ArrayLike<number>, length: number): { q1: number; median: number; q3: number };
}

export declare type BoxplotStatsOptions = {
  /**
   * specify the coefficient for the whiskers, use <=0 for getting min/max instead
   * the coefficient will be multiplied by the IQR
   * @default 1.5
   */
  coef?: number;

  /**
   * specify the quantile method to use
   * @default quantilesType7
   */
  quantiles?: QuantileMethod;

  /**
   * defines that it can be assumed that the array is sorted and just contains valid numbers
   * (which will avoid unnecessary checks and sorting)
   * @default false
   */
  validAndSorted?: boolean;

  /**
   * whiskers mode whether to compute the nearest element which is bigger/smaller than low/high whisker or
   * the exact value
   * @default 'nearest'
   */
  whiskersMode?: 'nearest' | 'exact';

  /**
   * delta epsilon to compare
   * @default 10e-3
   */
  eps?: number;
};

function createSortedData(data: readonly number[] | Float32Array | Float64Array) {
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  let sum = 0;
  let valid = 0;
  const length = data.length;

  const vs = data instanceof Float64Array ? new Float64Array(length) : new Float32Array(length);

  for (let i = 0; i < length; ++i) {
    const v = data[i];
    if (v == null || Number.isNaN(v)) {
      continue;
    }
    vs[valid] = v;
    valid++;

    if (v < min) {
      min = v;
    }
    if (v > max) {
      max = v;
    }
    sum += v;
  }

  const missing = length - valid;

  if (valid === 0) {
    return {
      sum,
      min,
      max,
      missing,
      s: [],
    };
  }

  // add comparator since the polyfill doesn't to a real sorting
  const s = valid === length ? vs : vs.subarray(0, valid);
  // sort in place
  s.sort((a, b) => (a === b ? 0 : a < b ? -1 : 1));

  // use real number for better precision
  return {
    sum,
    min: s[0],
    max: s[s.length - 1],
    missing,
    s,
  };
}

function withSortedData(data: readonly number[] | Float32Array | Float64Array) {
  if (data.length === 0) {
    return {
      sum: Number.NaN,
      min: Number.NaN,
      max: Number.NaN,
      missing: 0,
      s: [],
    };
  }
  const min = data[0];
  const max = data[data.length - 1];
  const red = (acc: number, v: number) => acc + v;
  const sum =
    data instanceof Float32Array
      ? data.reduce(red, 0)
      : data instanceof Float64Array
      ? data.reduce(red, 0)
      : data.reduce(red, 0);

  return {
    sum,
    min,
    max,
    missing: 0,
    s: data,
  };
}

export default function boxplot(
  data: readonly number[] | Float32Array | Float64Array,
  options: BoxplotStatsOptions = {}
): IBoxPlot {
  const { quantiles, validAndSorted, coef, whiskersMode, eps }: Required<BoxplotStatsOptions> = Object.assign(
    {
      coef: 1.5,
      eps: 10e-3,
      quantiles: quantilesType7,
      validAndSorted: false,
      whiskersMode: 'nearest',
    },
    options
  );

  const { missing, s, min, max, sum } = validAndSorted ? withSortedData(data) : createSortedData(data);

  const invalid = {
    min: Number.NaN,
    max: Number.NaN,
    mean: Number.NaN,
    missing,
    iqr: Number.NaN,
    count: data.length,
    whiskerHigh: Number.NaN,
    whiskerLow: Number.NaN,
    outlier: [],
    median: Number.NaN,
    q1: Number.NaN,
    q3: Number.NaN,
    items: [],
  };

  const same = (a: number, b: number) => Math.abs(a - b) < eps;

  const valid = data.length - missing;

  if (valid === 0) {
    return invalid;
  }

  const { median, q1, q3 } = quantiles(s, valid);
  const iqr = q3 - q1;
  const isCoefValid = typeof coef === 'number' && coef > 0;
  let whiskerLow = isCoefValid ? Math.max(min, q1 - coef * iqr) : min;
  let whiskerHigh = isCoefValid ? Math.min(max, q3 + coef * iqr) : max;

  const outlier: number[] = [];
  // look for the closest value which is bigger than the computed left
  for (let i = 0; i < valid; ++i) {
    const v = s[i];
    if (v >= whiskerLow || same(v, whiskerLow)) {
      if (whiskersMode === 'nearest') {
        whiskerLow = v;
      }
      break;
    }
    // outlier
    if (outlier.length === 0 || !same(outlier[outlier.length - 1], v)) {
      outlier.push(v);
    }
  }
  // look for the closest value which is smaller than the computed right
  const reversedOutliers: number[] = [];
  for (let i = valid - 1; i >= 0; --i) {
    const v = s[i];
    if (v <= whiskerHigh || same(v, whiskerHigh)) {
      if (whiskersMode === 'nearest') {
        whiskerHigh = v;
      }
      break;
    }
    // outlier
    if (
      (reversedOutliers.length === 0 || !same(reversedOutliers[reversedOutliers.length - 1], v)) &&
      (outlier.length === 0 || !same(outlier[outlier.length - 1], v))
    ) {
      reversedOutliers.push(v);
    }
  }

  return {
    min,
    max,
    count: data.length,
    missing,
    mean: sum / valid,
    whiskerHigh,
    whiskerLow,
    outlier: outlier.concat(reversedOutliers.reverse()),
    median,
    q1,
    q3,
    iqr,
    items: s,
  };
}
