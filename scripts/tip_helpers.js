// TIP CGSpace form helpers. Paste with the javascript tool ~3 s after each page load.
// Never use them to click "Send to review". Tested 2026-11-26 except where marked.
window.sleep = ms => new Promise(r => setTimeout(r, ms));
window._t = e => e.innerText.replace(/\s+/g, ' ').trim();

// Server-search select2 (authors, affiliations, project, sponsors, AGROVOC): type q, pick the first
// result where test(text). Returns "OK: text" or "NOTFOUND [q]: first results" (nothing picked).
window.s2pick = async (sel, q, test) => {
  const $s = jQuery(sel); $s.select2('open');
  const inp = document.querySelector('.select2-container--open .select2-search__field');
  inp.value = q; inp.dispatchEvent(new Event('input', {bubbles: true})); jQuery(inp).trigger('keyup');
  let opts = [];
  for (let i = 0; i < 40 && !opts.length; i++) {
    await sleep(300);
    opts = [...document.querySelectorAll('.select2-container--open .select2-results__option')].filter(o => !/Searching|Please enter|Loading/i.test(o.innerText));
  }
  const o = opts.find(o => test(_t(o)));
  if (!o) { $s.select2('close'); return 'NOTFOUND [' + q + ']: ' + opts.slice(0, 6).map(o => _t(o).slice(0, 70)).join(' || '); }
  const txt = _t(o); jQuery(o).trigger('mouseup'); await sleep(1500);
  return 'OK: ' + txt.slice(0, 90);
};

// Plain select by exact option texts; returns the texts not found.
window.setSel = (id, texts) => {
  const s = jQuery('#' + id), vals = [], miss = [];
  texts.forEach(t => { const o = [...s[0].options].find(o => o.text.trim() === t); o ? vals.push(o.value) : miss.push(t); });
  s.val(vals).trigger('change'); return miss;
};
window.setText = (id, v) => { const e = document.getElementById(id); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); jQuery(e).trigger('change'); };

window.addExt = async (name, institution) => {
  document.getElementById('addExternal').click(); await sleep(1200);
  const idx = Math.max(...[...document.querySelectorAll('[name^="authors["][name$="[name]"]')].map(e => +e.name.match(/authors\[(\d+)\]/)[1]));
  const f = k => document.querySelector('[name="authors[' + idx + '][' + k + ']"]');
  for (const [k, v] of [['name', name], ['institution', institution]]) { const e = f(k); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); jQuery(e).trigger('change').trigger('keyup').trigger('blur'); }
  await sleep(600); return idx + ': ' + f('name').value;
};
// Reuse a staff or External record named exactly "Surname, Firstname"; otherwise add an external author.
window.findOrAdd = async (name, institution) => {
  const r = await s2pick('#find_author', name.split(',')[0], t => t.startsWith(name + ' '));
  return r.startsWith('OK') ? r : await addExt(name, institution);
};

window.orgSelect = () => { const s = [...document.querySelectorAll('#section-A-container select')].find(s => !s.id || s.id === 'tmp_org_select'); s.id = 'tmp_org_select'; return '#tmp_org_select'; };
window.sponsorSelect = () => { const s = [...document.querySelectorAll('#section-B-container select[multiple]')].find(x => !x.id || x.id === 'tmp_sponsor_select'); s.id = 'tmp_sponsor_select'; return '#tmp_sponsor_select'; };

// Contributes to a Science Program = No, no program tagged. Run before every Save Draft or Send.
window.noScienceProgram = () => {
  document.querySelector('input[name="toc_science_program_contribution"][value="no"]').click();
  jQuery('#portfolio_programs_accelerators').val([]).trigger('change');
  const cb = document.getElementById('portfolio-has-programs-accelerators'); if (cb.checked) cb.click();
};

// Files served by scripts/serve_file.py: files = [[port, fileName], ...].
window.attachServed = async (files, type = 'application/pdf') => {
  const dt = new DataTransfer();
  for (const [port, name] of files) dt.items.add(new File([await fetch('http://127.0.0.1:' + port + '/file').then(r => r.blob())], name, {type}));
  document.getElementById('fileupload').files = dt.files;
  return [...dt.files].map(x => x.name + ' ' + x.size);
};

// The javascript tool stops waiting after 45 s; the page keeps running. Read window.__job later.
window.runInBackground = fn => { window.__job = 'running'; fn().then(r => window.__job = r).catch(e => window.__job = 'ERROR ' + e.message); return 'started'; };

window.storedFileSizes = async () => {
  const out = [];
  for (const a of document.querySelectorAll('a[href*="/CgspaceSubmission/file"]')) out.push(+(await fetch(a.href, {method: 'HEAD', credentials: 'include'})).headers.get('content-length'));
  return out;
};

// Filled values only, as compact JSON (empty fields are left out). Tested 2026-11-27.
window.formState = () => {
  const sel = id => { const e = document.getElementById(id); return e ? [...e.selectedOptions].filter(o => o.value !== '' && !/^select$/i.test(o.text.trim())).map(o => o.text.trim()) : []; };
  const val = id => (document.getElementById(id) || {}).value;
  const names = div => [...document.querySelectorAll(div + ' input')].filter(i => /\[name\]/.test(i.name)).map(i => i.value);
  const s = {
    title: val('first_name01'), authors: [...(document.getElementById('c_author') || {options: []}).options].slice(1).map(o => o.text),
    corresponding: jQuery('#c_author option:selected').text(), date: val('date_publication'),
    affiliations: names('#affiliations-div'), sponsors: names('#sponsors-div'),
    ip: (document.querySelector('input[name=i_property]:checked') || {}).value,
    scienceProgramContribution: (document.querySelector('input[name="toc_science_program_contribution"]:checked') || {}).value,
    abstractChars: (val('abstract_field') || '').length, files: [...(document.getElementById('fileupload') || {files: []}).files].map(f => f.name)
  };
  for (const id of ['authorship_field', 'p_collection', 'p_type', 'languages', 'countries', 'regions', 'open_access', 'usage_rigth',
                    'alliance_subject', 'impact_area_field', 'lever_field', 'portfolio_programs_accelerators', 'selectAgrovoc', 'selectAgrovocES']) s[id] = sel(id);
  for (const k in s) if (s[k] == null || s[k] === '' || (Array.isArray(s[k]) && !s[k].length)) delete s[k];
  return s;
};

// Required questions ("*") in tabs A to D whose answer is still empty. Questions hidden inside their
// tab (conditional branches) are skipped. missingRequired(true) shows the control found for each.
// Tested 2026-11-27 on /create (16 required on an empty form).
window.missingRequired = (debug) => {
  const CTRL = 'select, textarea, input:not([type=hidden]):not(.select2-search__field):not([type=button]):not([type=submit])';
  const isEmpty = (c, holder) => {
    if (c.type === 'checkbox') return !holder.querySelector('input[type=checkbox]:checked');
    if (c.type === 'radio') return !document.querySelector('input[name="' + c.name + '"]:checked');
    if (c.tagName === 'SELECT') return ![...c.selectedOptions].some(o => o.value !== '' && !/^select$/i.test(o.text.trim()));
    return !String(c.value || '').trim();
  };
  const hidden = (e, sec) => { for (let p = e; p && p !== sec; p = p.parentElement) if (getComputedStyle(p).display === 'none') return true; return false; };
  const out = [];
  for (const x of 'ABCD') {
    const sec = document.getElementById('section-' + x + '-container'); if (!sec) continue;
    const qs = [...sec.querySelectorAll('h6, label, p')].filter(q => { const t = _t(q); return t.length > 1 && t.length < 220 && /\*$/.test(t); });
    for (const q of qs) {
      if (qs.some(o => o !== q && q.contains(o)) || hidden(q, sec)) continue;
      const label = x + ': ' + _t(q).replace(/\s*\*\s*/g, ' ').trim().slice(0, 60);
      let c = null, holder = null, empty;
      if (/^Author\(s\)/.test(_t(q))) { empty = document.querySelectorAll('#c_author option').length < 2; c = 'authors'; }
      else {
        for (let n = q.nextElementSibling; !c && n && !qs.some(o => n === o || n.contains(o)); n = n.nextElementSibling) { c = n.matches(CTRL) ? n : n.querySelector(CTRL); holder = n; }
        for (let box = q.parentElement; !c && box && box !== sec; box = box.parentElement) { const others = qs.some(o => o !== q && box.contains(o)); c = others ? null : box.querySelector(CTRL); holder = box; if (others) break; }
        empty = !c || isEmpty(c, holder);
      }
      if (debug) out.push(label + ' -> ' + (c ? (c.id || c.name || c.tagName || c) : 'NO CONTROL') + (empty ? ' EMPTY' : ' ok'));
      else if (empty) out.push(label);
    }
  }
  return out;
};

// After Save Draft: open /CgspaceSubmission/update/<id>; expectedBytes = one number or an array.
window.verifyDraft = async expectedBytes => {
  const sizes = await storedFileSizes(), want = expectedBytes == null ? null : [].concat(expectedBytes);
  return {...formState(), fileBytes: sizes, sameFiles: want ? sizes.length === want.length && want.every(w => sizes.includes(w)) : undefined};
};
'tip helpers loaded';
