// Helpers to fill the TIP CGSpace form (https://tip.alliance.cgiar.org/CgspaceSubmission/create).
// Paste this into the page with the Claude in Chrome javascript tool after the page has fully
// loaded (wait ~3 s; select2 is not ready right after navigation). Re-run after every navigation.
// Tested 2026-11-26 on five real submissions. Never use these to click "Send to review".

window.sleep = ms => new Promise(r => setTimeout(r, ms));

// Search a select2 list that loads results from the server (authors, affiliations, project,
// sponsors, AGROVOC), and pick the first result for which test(text) is true.
// Returns "OK: <picked text>" or "NOTFOUND [query]: <first results>" (nothing is picked then).
// Use test = t => false to only look at the results.
window.s2pick = async (sel, q, test) => {
  const $s = jQuery(sel); $s.select2('open');
  const inp = document.querySelector('.select2-container--open .select2-search__field');
  inp.value = q; inp.dispatchEvent(new Event('input', {bubbles: true})); jQuery(inp).trigger('keyup');
  let opts = [];
  for (let i = 0; i < 40; i++) {
    await sleep(300);
    opts = Array.from(document.querySelectorAll('.select2-container--open .select2-results__option'))
      .filter(o => !/Searching|Please enter|Loading/i.test(o.innerText));
    if (opts.length) break;
  }
  const o = opts.find(o => test(o.innerText.replace(/\s+/g, ' ')));
  if (!o) { $s.select2('close'); return 'NOTFOUND [' + q + ']: ' + opts.map(o => o.innerText.replace(/\s+/g, ' ').slice(0, 70)).slice(0, 6).join(' || '); }
  const txt = o.innerText.replace(/\s+/g, ' ');
  jQuery(o).trigger('mouseup');
  await sleep(1500);
  return 'OK: ' + txt.slice(0, 90);
};

// Set a plain select by exact option texts. Returns the texts that were not found.
window.setSel = (id, texts) => {
  const s = jQuery('#' + id); const vals = []; const miss = [];
  texts.forEach(t => { const o = Array.from(s[0].options).find(o => o.text.trim() === t); if (o) vals.push(o.value); else miss.push(t); });
  s.val(vals).trigger('change'); return miss;
};

window.setText = (id, v) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); jQuery(e).trigger('change'); };

// Add an external author (not in the staff directory). Search first with s2pick: some
// partners already exist as "External" records; reuse those instead of creating duplicates.
window.addExt = async (name, institution) => {
  document.getElementById('addExternal').click(); await sleep(1200);
  const idx = Math.max(...Array.from(document.querySelectorAll('[name^="authors["][name$="[name]"]')).map(e => +e.name.match(/authors\[(\d+)\]/)[1]));
  const f = k => document.querySelector('[name="authors[' + idx + '][' + k + ']"]');
  for (const [k, v] of [['name', name], ['institution', institution]]) { const e = f(k); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); jQuery(e).trigger('change').trigger('keyup').trigger('blur'); }
  await sleep(600); return idx + ': ' + f('name').value;
};

// Unnamed selects get a temporary id so s2pick can address them.
window.orgSelect = () => { const s = Array.from(document.querySelectorAll('#section-A-container select')).find(s => !s.id || s.id === 'tmp_org_select'); s.id = 'tmp_org_select'; return '#tmp_org_select'; };
window.sponsorSelect = () => { const s = Array.from(document.querySelectorAll('#section-B-container select[multiple]')).find(x => !x.id || x.id === 'tmp_sponsor_select'); s.id = 'tmp_sponsor_select'; return '#tmp_sponsor_select'; };

// "Does this result contribute to a Science Program or Accelerator?" = No, and no program tagged.
// Call again right before every Save Draft: TIP resets it from the project on reload.
window.noScienceProgram = () => {
  document.querySelector('input[name="toc_science_program_contribution"][value="no"]').click();
  jQuery('#portfolio_programs_accelerators').val([]).trigger('change');
  const cb = document.getElementById('portfolio-has-programs-accelerators'); if (cb.checked) cb.click();
};

// Put a file served by scripts/serve_file.py into the file input (any size).
window.attachServed = async (fileName, type = 'application/pdf') => {
  const b = await fetch('http://127.0.0.1:8765/file').then(r => r.blob());
  const dt = new DataTransfer(); dt.items.add(new File([b], fileName, {type}));
  document.getElementById('fileupload').files = dt.files;
  return Array.from(document.getElementById('fileupload').files).map(x => x.name + ' ' + x.size);
};

// After Save Draft, open /CgspaceSubmission/update/<id> and run this to check what was stored.
window.verifyDraft = async expectedBytes => {
  const a = document.querySelector('a[href*="/CgspaceSubmission/file"]');
  const size = a ? (await fetch(a.href, {credentials: 'include'}).then(r => r.blob())).size : null;
  const sel = id => Array.from(document.getElementById(id).selectedOptions).map(o => o.text.trim());
  return {
    title: document.getElementById('first_name01').value,
    authors: Array.from(document.getElementById('c_author').options).slice(1).map(o => o.text),
    corresponding: jQuery('#c_author option:selected').text(),
    authorship: sel('authorship_field'), date: document.getElementById('date_publication').value,
    countries: sel('countries'), regions: sel('regions'),
    affiliations: Array.from(document.querySelectorAll('#affiliations-div input')).filter(i => /\[name\]/.test(i.name)).map(i => i.value),
    sponsors: Array.from(document.querySelectorAll('#sponsors-div input')).filter(i => /\[name\]/.test(i.name)).map(i => i.value),
    sciencePrograms: sel('portfolio_programs_accelerators'), lever: sel('lever_field'), agrovoc: sel('selectAgrovoc'),
    ip: (document.querySelector('input[name=i_property]:checked') || {}).value,
    fileBytes: size, sameFile: expectedBytes ? size === expectedBytes : undefined
  };
};

'tip helpers loaded';
