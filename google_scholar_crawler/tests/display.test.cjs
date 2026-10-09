const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');
const source = fs.readFileSync('_includes/fetch_google_scholar_stats.html', 'utf8')
  .split('<script>')[1].split('</script>')[0]
  .replace(/{%[\s\S]*?%}/g, '').replace(/{{[\s\S]*?}}/g, 'example/repo');

async function render(data, ok = true) {
  const nodes = Object.fromEntries(['total_cit', 'total_cit_wrap', 'gs-updated', 'gs-summary', 'paper']
    .map(id => [id, { textContent: '', hidden: true, removeAttribute() { this.hidden = false; }, getAttribute() { return 'test:paper'; } }]));
  vm.runInNewContext(source, {
    fetch: async () => ({ ok, status: 503, json: async () => data }),
    document: { getElementById: id => nodes[id], getElementsByClassName: () => [nodes.paper] }
  });
  await new Promise(resolve => setImmediate(resolve));
  return nodes;
}

test('old snapshot keeps its UTC date on totals, summary and publication tooltip', async () => {
  const nodes = await render({ citedby: 86, hindex: 6, updated: '2026-09-30 14:23:15.124241', publications: { 'test:paper': { num_citations: 2 } } });
  assert.equal(nodes.total_cit.textContent, 86);
  assert.equal(nodes['gs-summary'].textContent, ' (86 citations, h-index 6; as of 2026-09-30 UTC)');
  assert.equal(nodes['gs-updated'].textContent, ' (as of 2026-09-30 UTC)');
  assert.equal(nodes.paper.title, 'Google Scholar citations, as of 2026-09-30 UTC');
});
test('new timezone-aware timestamp and zero citations display correctly', async () => {
  const nodes = await render({ citedby: 0, hindex: 0, updated: '2026-10-09T01:02:03+00:00' });
  assert.equal(nodes.total_cit_wrap.hidden, false);
  assert.match(nodes['gs-summary'].textContent, /0 citations, h-index 0; as of 2026-10-09 UTC/);
  assert.equal(nodes.paper.hidden, true);
});
test('unknown dates are not represented as a fresh collection', async () => {
  for (const updated of [undefined, '', 'invalid']) {
    const nodes = await render({ citedby: 86, updated });
    assert.match(nodes['gs-summary'].textContent, /date unavailable/);
  }
});
test('network or malformed data stays hidden', async () => {
  for (const data of [null, {}, { citedby: '86' }, { citedby: -1 }]) {
    const nodes = await render(data);
    assert.equal(nodes.total_cit_wrap.hidden, true);
    assert.equal(nodes['gs-summary'].hidden, true);
  }
  assert.equal((await render({ citedby: 86 }, false)).total_cit_wrap.hidden, true);
});
