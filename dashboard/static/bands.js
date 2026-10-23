/* CardScout /bands — client-side sorts (P7) + localStorage favorites (Phase 1).
   Sorts operate ONLY on rows already in the DOM: zero network calls. */
(function () {
  'use strict';

  // ---------------- favorites (localStorage, no account) ----------------
  var FAV_KEY = 'cardscout.favorites.v1';

  function readFavs() {
    try {
      var raw = localStorage.getItem(FAV_KEY);
      var arr = raw ? JSON.parse(raw) : [];
      return Array.isArray(arr) ? arr : [];
    } catch (e) { return []; }
  }

  function writeFavs(arr) {
    try { localStorage.setItem(FAV_KEY, JSON.stringify(arr.slice(0, 200))); } catch (e) { /* private mode */ }
  }

  var favBtn = document.getElementById('fav-btn');
  if (favBtn) {
    var slug = favBtn.getAttribute('data-slug');
    var sync = function () {
      var favs = readFavs();
      var on = favs.indexOf(slug) !== -1;
      favBtn.classList.toggle('is-fav', on);
      favBtn.textContent = on ? '★ Favorited' : '☆ Favorite';
    };
    favBtn.addEventListener('click', function () {
      var favs = readFavs();
      var idx = favs.indexOf(slug);
      if (idx === -1) favs.push(slug); else favs.splice(idx, 1);
      writeFavs(favs);
      sync();
    });
    sync();
  }

  // ---------------- client-side sorts (zero API cost) ----------------
  var SORTS = {
    // key: comparator on the row's data-* attributes. Ascending unless noted.
    'default': function (a, b) { return byClassPrice(a) - byClassPrice(b); },
    'price':   function (a, b) { return num(a, 'price') - num(b, 'price'); },
    'score':   function (a, b) { return num(b, 'score') - num(a, 'score'); },   // high first
    'fb':      function (a, b) { return num(b, 'fb') - num(a, 'fb'); },         // high first
    'ship':    function (a, b) { return num(a, 'ship') - num(b, 'ship'); },     // free first
    'type':    function (a, b) { return byClassPrice(a) - byClassPrice(b); },
    'date':    function (a, b) { return dateCmp(a, b); }                        // freshest first
  };

  function num(el, attr) {
    var v = parseFloat(el.getAttribute('data-' + attr));
    return isNaN(v) ? Infinity : v; // unknown sorts last, never dropped
  }

  function byClassPrice(el) {
    // default/type order: plain BIN < OBO < Auction (founder type-classing)
    var order = { 'bin': 0, 'obo': 1, 'auction': 2 };
    return (order[el.getAttribute('data-class')] || 3) * 1e12 + num(el, 'price');
  }

  function dateCmp(a, b) {
    var da = a.getAttribute('data-date') || '';
    var db = b.getAttribute('data-date') || '';
    return (db || '').localeCompare(da || '');
  }

  var sortState = null;
  try { sortState = sessionStorage.getItem('cardscout.sort'); } catch (e) {}

  var rowsHost = document.getElementById('listing-rows');
  var bar = document.querySelector('.sort-bar');

  function applySort(name) {
    if (!rowsHost || !SORTS[name]) return;
    var rows = Array.prototype.slice.call(rowsHost.children); // the IDENTICAL row set
    rows.sort(SORTS[name]);
    rows.forEach(function (row, i) {
      row.querySelector('.row-rank').textContent = '#' + (i + 1);
      rowsHost.appendChild(row);
    });
    if (bar) {
      var btns = bar.querySelectorAll('.sort-btn');
      for (var k = 0; k < btns.length; k++) {
        var on = btns[k].getAttribute('data-sort') === name;
        btns[k].classList.toggle('active', on);
      }
    }
    sortState = name;
    try { sessionStorage.setItem('cardscout.sort', name); } catch (e) {}
  }

  if (bar && rowsHost) {
    bar.addEventListener('click', function (ev) {
      var btn = ev.target.closest('.sort-btn');
      if (!btn) return;
      applySort(btn.getAttribute('data-sort'));
    });
    // restore the user's lens within the session
    applySort(sortState || 'default');
  }
})();