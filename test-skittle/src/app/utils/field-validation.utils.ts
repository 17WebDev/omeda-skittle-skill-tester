import {computed, Signal} from '@angular/core';

export function requiredString(value: Signal<string>, touched: Signal<boolean>, label: string) {
  return computed(() =>
    touched() && value().trim() === '' ? `${label} is required` : null
  );
}

export function requiredNumber(value: Signal<number | null>, touched: Signal<boolean>, label: string) {
  return computed(() =>
    touched() && value() === null ? `${label} is required` : null
  );
}
