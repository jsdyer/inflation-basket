import {el} from './ui.mjs';

const monthFormat = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric', month: 'long', timeZone: 'UTC',
});
const monthName = month => monthFormat.format(new Date(month + '-01T00:00:00Z'));
const percent = new Intl.NumberFormat('en-CA', {
  style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1, signDisplay: 'exceptZero',
});

export function startRent(series) {
  const start = el('rent-from');
  const end = el('rent-to');
  const results = el('rent-results');
  function update() {
    const from = start.value, to = end.value;
    const valid = start.validity.valid && end.validity.valid && from <= to;
    results.hidden = !valid;
    el('rent-status').textContent = valid ? '' : 'Choose two months within the coverage dates, with the ending month on or after the start.';
    if (!valid) return;
    for (const card of results.querySelectorAll('[data-vector]')) {
      const values = series[card.dataset.vector];
      const a = values[from], b = values[to];
      const available = Number.isFinite(a) && Number.isFinite(b);
      card.querySelector('.big').textContent = available ? percent.format(b / a - 1) : 'Unavailable';
      card.querySelector('.rent-indexes').textContent = available
        ? 'Index ' + a.toFixed(1) + ' in ' + monthName(from) + ' and ' + b.toFixed(1) + ' in ' + monthName(to) + '.'
        : 'No published index for ' + [from, to].filter((m, i, all) => values[m] == null && all.indexOf(m) === i).map(monthName).join(' or ') + '.';
      const link = card.querySelector('a');
      const url = new URL(link.href);
      url.searchParams.set('refPeriods', [from, to].map(m => m.replace('-', '') + '01').join(','));
      link.href = url.href;
    }
  }
  el('rent-controls').hidden = false;
  start.addEventListener('input', update);
  end.addEventListener('input', update);
}
