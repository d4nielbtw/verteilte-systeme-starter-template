<script>
  import { onMount } from 'svelte';

  // Auth
  let username = $state('');
  let password = $state('');
  let email = $state('');
  let error = $state('');
  let loggedIn = $state(false);
  let showRegister = $state(false);
  let token = $state('');

  let page = $state('start');

  // Rezepte
  let publicRecipes = $state([]);
  let myRecipes = $state([]);
  let showForm = $state(false);
  let editRecipe = $state(null);
  let selectedRecipe = $state(null);
  let form = $state({ Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '', image_url: '', is_public: false });

  // Zutaten
  let zutatenListe = $state([]);
  let zutatenInput = $state('');

  // Filter Startseite
  let searchPublic = $state('');
  let filterKatPublic = $state('');
  let filterZeitPublic = $state('');
  let filterZutatPublic = $state('');

  // Filter Meine Rezepte
  let searchMeine = $state('');
  let filterKatMeine = $state('');
  let filterZeitMeine = $state('');
  let filterZutatMeine = $state('');

  const API = 'http://localhost:8000';

  const kategorien = [
    'Frühstück', 'Mittagessen', 'Abendessen', 'Snack', 'Dessert',
    'Pasta', 'Suppe', 'Salat', 'Backen', 'Vegetarisch', 'Vegan', 'Grillen', 'Sonstiges'
  ];

  const zeiten = [
    'unter 15 min', '15 min', '30 min', '45 min', '1 Stunde',
    '1,5 Stunden', '2 Stunden', 'über 2 Stunden'
  ];

  onMount(() => { loadPublic(); });

  async function loadPublic() {
    const res = await fetch(`${API}/startseite`);
    if (res.ok) publicRecipes = await res.json();
  }

  async function login() {
    error = '';
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const res = await fetch(`${API}/token`, { method: 'POST', body: formData });
    if (res.ok) {
      const data = await res.json();
      token = data.access_token;
      localStorage.setItem('token', token);
      loggedIn = true;
      page = 'start';
      await loadPublic();
      await loadMyRecipes();
    } else {
      error = 'Benutzername oder Passwort falsch.';
    }
  }

  async function register() {
    error = '';
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    if (res.ok) {
      showRegister = false;
      error = '';
      username = '';
      password = '';
      email = '';
    } else {
      const data = await res.json();
      error = data.detail || 'Registrierung fehlgeschlagen.';
    }
  }

  function logout() {
    loggedIn = false;
    token = '';
    myRecipes = [];
    page = 'start';
    localStorage.removeItem('token');
  }

  async function loadMyRecipes() {
    const res = await fetch(`${API}/rezepte`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) myRecipes = await res.json();
  }

  function openAdd() {
    editRecipe = null;
    form = { Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '', image_url: '', is_public: false };
    zutatenListe = [];
    zutatenInput = '';
    showForm = true;
  }

  function openEdit(r) {
    editRecipe = r;
    form = {
      Kochrezept_Name: r.Kochrezept_Name,
      kategorie: r.kategorie,
      zeit: r.zeit,
      zutaten: r.zutaten,
      description: r.description,
      image_url: r.image_url,
      is_public: r.is_public
    };
    zutatenListe = r.zutaten ? r.zutaten.split(',').map(z => z.trim()).filter(z => z) : [];
    zutatenInput = '';
    showForm = true;
  }

  function zutatHinzufuegen() {
    const z = zutatenInput.trim();
    if (z && !zutatenListe.includes(z)) zutatenListe = [...zutatenListe, z];
    zutatenInput = '';
  }

  function zutatEntfernen(z) {
    zutatenListe = zutatenListe.filter(item => item !== z);
  }

  function handleZutatKeydown(e) {
    if (e.key === 'Enter') { e.preventDefault(); zutatHinzufuegen(); }
  }

  async function saveRecipe() {
    if (!form.Kochrezept_Name) return;
    form.zutaten = zutatenListe.join(', ');
    const method = editRecipe ? 'PUT' : 'POST';
    const url = editRecipe ? `${API}/rezepte/${editRecipe.id}` : `${API}/rezepte`;
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(form)
    });
    if (res.ok) { await loadMyRecipes(); await loadPublic(); }
    showForm = false;
  }

  async function deleteRecipe(id) {
    const res = await fetch(`${API}/rezepte/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) { await loadMyRecipes(); await loadPublic(); }
  }

  async function bewerten(rezeptId, s) {
    if (!loggedIn) return;
    await fetch(`${API}/rezepte/${rezeptId}/bewertung`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ sterne: s })
    });
    await loadPublic();
  }

  function sterne(n) {
    return Array.from({ length: 5 }, (_, i) => i < n ? '★' : '☆').join('');
  }

  function filterRezepte(liste, search, kat, zeit, zutat) {
    const s = search.toLowerCase();
    const z = zutat.toLowerCase();
    return liste.filter(r => {
      const matchSearch = !s ||
        r.Kochrezept_Name.toLowerCase().includes(s) ||
        r.description.toLowerCase().includes(s) ||
        r.zutaten.toLowerCase().includes(s);
      const matchKat = !kat || r.kategorie === kat;
      const matchZeit = !zeit || r.zeit === zeit;
      const matchZutat = !z || r.zutaten.toLowerCase().includes(z);
      return matchSearch && matchKat && matchZeit && matchZutat;
    });
  }

  let filteredPublic = $derived(filterRezepte(publicRecipes, searchPublic, filterKatPublic, filterZeitPublic, filterZutatPublic));
  let filteredMeine = $derived(filterRezepte(myRecipes, searchMeine, filterKatMeine, filterZeitMeine, filterZutatMeine));

  function resetFiltersPublic() {
    searchPublic = ''; filterKatPublic = ''; filterZeitPublic = ''; filterZutatPublic = '';
  }

  function resetFiltersMeine() {
    searchMeine = ''; filterKatMeine = ''; filterZeitMeine = ''; filterZutatMeine = '';
  }
</script>

{#if !loggedIn && page === 'login'}
  <div class="screen">
    <div class="card">
      {#if !showRegister}
        <h1>Anmelden</h1>
        <p class="sub">Bitte gib deine Zugangsdaten ein.</p>
        <label for="user">Benutzername</label>
        <input type="text" id="user" bind:value={username} placeholder="Benutzername"/>
        <label for="pass">Passwort</label>
        <input type="password" id="pass" bind:value={password} placeholder="Passwort"/>
        {#if error}<p class="error">{error}</p>{/if}
        <button onclick={login}>Anmelden</button>
        <button class="btn-secondary" onclick={() => { showRegister = true; error = ''; }}>Noch kein Konto? Registrieren</button>
        <button class="btn-secondary" onclick={() => page = 'start'}>Zurück</button>
      {:else}
        <h1>Registrieren</h1>
        <p class="sub">Erstelle ein neues Konto.</p>
        <label for="reg-user">Benutzername</label>
        <input type="text" id="reg-user" bind:value={username} placeholder="Benutzername"/>
        <label for="reg-email">E-Mail</label>
        <input type="email" id="reg-email" bind:value={email} placeholder="E-Mail"/>
        <label for="reg-pass">Passwort</label>
        <input type="password" id="reg-pass" bind:value={password} placeholder="Passwort"/>
        {#if error}<p class="error">{error}</p>{/if}
        <button onclick={register}>Konto erstellen</button>
        <button class="btn-secondary" onclick={() => { showRegister = false; error = ''; }}>Zurück zum Login</button>
      {/if}
    </div>
  </div>

{:else}
  <nav>
    <span class="nav-logo">🍽 Koch wie Mutti</span>
    <div class="nav-links">
      <button class="nav-btn" class:active={page === 'start'} onclick={() => page = 'start'}>Startseite</button>
      {#if loggedIn}
        <button class="nav-btn" class:active={page === 'meine'} onclick={() => { page = 'meine'; loadMyRecipes(); }}>Meine Rezepte</button>
        <button class="nav-btn nav-logout" onclick={logout}>Abmelden</button>
      {:else}
        <button class="nav-btn nav-login" onclick={() => { page = 'login'; showRegister = false; }}>Anmelden</button>
      {/if}
    </div>
  </nav>

  {#if page === 'start'}
    <div class="main">
      <h2>Öffentliche Rezepte</h2>
      <p class="page-sub">Entdecke Rezepte aus der Community</p>

      <div class="filter-bar">
        <input class="search-input" type="text" bind:value={searchPublic} placeholder="🔍 Suchen..."/>
        <select bind:value={filterKatPublic}>
          <option value="">Alle Kategorien</option>
          {#each kategorien as k}<option value={k}>{k}</option>{/each}
        </select>
        <select bind:value={filterZeitPublic}>
          <option value="">Alle Zeiten</option>
          {#each zeiten as z}<option value={z}>{z}</option>{/each}
        </select>
        <input class="search-input" type="text" bind:value={filterZutatPublic} placeholder="Zutat filtern..."/>
        {#if searchPublic || filterKatPublic || filterZeitPublic || filterZutatPublic}
          <button class="btn-reset" onclick={resetFiltersPublic}>✕ Zurücksetzen</button>
        {/if}
      </div>

      {#if filteredPublic.length === 0}
        <p class="empty">Keine Rezepte gefunden.</p>
      {/if}

      <div class="grid">
        {#each filteredPublic as r}
          <div class="recipe-card" role="button" tabindex="0" onclick={() => selectedRecipe = r} onkeydown={() => selectedRecipe = r}>
            {#if r.image_url}
              <img src={r.image_url} alt={r.Kochrezept_Name} class="recipe-img"/>
            {/if}
            <div class="recipe-top">
              <span class="category">{r.kategorie}</span>
              <span class="time">⏱ {r.zeit}</span>
            </div>
            <h3>{r.Kochrezept_Name}</h3>
            <p class="author">👤 {r.username}</p>
            <div class="zutaten-tags">
              {#each r.zutaten.split(',').map(z => z.trim()).filter(z => z) as z}
                <span class="zutat-tag">{z}</span>
              {/each}
            </div>
            <div class="rating-section">
              <span class="stars-display">{sterne(Math.round(r.durchschnitt))}</span>
              <span class="rating-info">
                {r.durchschnitt > 0 ? r.durchschnitt.toFixed(1) : '–'}
                ({r.anzahl_bewertungen} {r.anzahl_bewertungen === 1 ? 'Bewertung' : 'Bewertungen'})
              </span>
            </div>
            {#if loggedIn}
              <div class="rate-row" onclick={(e) => e.stopPropagation()}>
                <span class="rate-label">Bewerten:</span>
                {#each [1,2,3,4,5] as s}
                  <button class="star-btn" onclick={() => bewerten(r.id, s)}>★</button>
                {/each}
              </div>
            {:else}
              <p class="login-hint">
                <button class="link-btn" onclick={(e) => { e.stopPropagation(); page = 'login'; showRegister = false; }}>Anmelden</button>
                um zu bewerten
              </p>
            {/if}
          </div>
        {/each}
      </div>
    </div>

  {:else if page === 'meine'}
    <div class="main">
      <div class="page-header">
        <div>
          <h2>Meine Rezepte</h2>
          <p class="page-sub">Verwalte deine persönlichen Rezepte</p>
        </div>
        <button class="btn-add" onclick={openAdd}>+ Rezept hinzufügen</button>
      </div>

      <div class="filter-bar">
        <input class="search-input" type="text" bind:value={searchMeine} placeholder="🔍 Suchen..."/>
        <select bind:value={filterKatMeine}>
          <option value="">Alle Kategorien</option>
          {#each kategorien as k}<option value={k}>{k}</option>{/each}
        </select>
        <select bind:value={filterZeitMeine}>
          <option value="">Alle Zeiten</option>
          {#each zeiten as z}<option value={z}>{z}</option>{/each}
        </select>
        <input class="search-input" type="text" bind:value={filterZutatMeine} placeholder="Zutat filtern..."/>
        {#if searchMeine || filterKatMeine || filterZeitMeine || filterZutatMeine}
          <button class="btn-reset" onclick={resetFiltersMeine}>✕ Zurücksetzen</button>
        {/if}
      </div>

      {#if filteredMeine.length === 0}
        <p class="empty">Keine Rezepte gefunden.</p>
      {/if}

      <div class="grid">
        {#each filteredMeine as r}
          <div class="recipe-card" role="button" tabindex="0" onclick={() => selectedRecipe = r} onkeydown={() => selectedRecipe = r}>
            {#if r.image_url}
              <img src={r.image_url} alt={r.Kochrezept_Name} class="recipe-img"/>
            {/if}
            <div class="recipe-top">
              <span class="category">{r.kategorie}</span>
              <span class="time">⏱ {r.zeit}</span>
            </div>
            <h3>{r.Kochrezept_Name}</h3>
            <div class="zutaten-tags">
              {#each r.zutaten.split(',').map(z => z.trim()).filter(z => z) as z}
                <span class="zutat-tag">{z}</span>
              {/each}
            </div>
            <div class="rating-section">
              <span class="stars-display">{sterne(Math.round(r.durchschnitt))}</span>
              <span class="rating-info">
                {r.durchschnitt > 0 ? r.durchschnitt.toFixed(1) : '–'}
                ({r.anzahl_bewertungen} {r.anzahl_bewertungen === 1 ? 'Bewertung' : 'Bewertungen'})
              </span>
            </div>
            <div class="visibility">
              {#if r.is_public}
                <span class="badge public">🌍 Öffentlich</span>
              {:else}
                <span class="badge private">🔒 Privat</span>
              {/if}
            </div>
            <div class="actions" onclick={(e) => e.stopPropagation()}>
              <button class="btn-edit" onclick={() => openEdit(r)}>Bearbeiten</button>
              <button class="btn-delete" onclick={() => deleteRecipe(r.id)}>Löschen</button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Detail Modal -->
  {#if selectedRecipe}
    <div class="overlay" role="button" tabindex="0" onclick={() => selectedRecipe = null} onkeydown={() => selectedRecipe = null}>
      <div class="modal detail-modal" role="button" tabindex="0" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
        {#if selectedRecipe.image_url}
          <img src={selectedRecipe.image_url} alt={selectedRecipe.Kochrezept_Name} class="detail-img"/>
        {/if}
        <div class="detail-top">
          <span class="category">{selectedRecipe.kategorie}</span>
          <span class="time">⏱ {selectedRecipe.zeit}</span>
        </div>
        <h3>{selectedRecipe.Kochrezept_Name}</h3>
        <p class="detail-desc">{selectedRecipe.description}</p>
        <div class="zutaten-tags">
          {#each selectedRecipe.zutaten.split(',').map(z => z.trim()).filter(z => z) as z}
            <span class="zutat-tag">{z}</span>
          {/each}
        </div>
        <div class="rating-section">
          <span class="stars-display">{sterne(Math.round(selectedRecipe.durchschnitt))}</span>
          <span class="rating-info">
            {selectedRecipe.durchschnitt > 0 ? selectedRecipe.durchschnitt.toFixed(1) : '–'}
            ({selectedRecipe.anzahl_bewertungen} {selectedRecipe.anzahl_bewertungen === 1 ? 'Bewertung' : 'Bewertungen'})
          </span>
        </div>
        <button class="btn-cancel" onclick={() => selectedRecipe = null}>Schließen</button>
      </div>
    </div>
  {/if}

  <!-- Form Modal -->
  {#if showForm}
    <div class="overlay" role="button" tabindex="0" onclick={() => showForm = false} onkeydown={() => showForm = false}>
      <div class="modal" role="button" tabindex="0" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
        <h3>{editRecipe ? 'Rezept bearbeiten' : 'Neues Rezept'}</h3>

        <label for="title">Titel</label>
        <input type="text" id="title" bind:value={form.Kochrezept_Name} placeholder="z.B. Spaghetti Bolognese"/>

        <label for="cat">Kategorie</label>
        <select id="cat" bind:value={form.kategorie}>
          <option value="" disabled>Kategorie wählen</option>
          {#each kategorien as k}<option value={k}>{k}</option>{/each}
        </select>

        <label for="zeit">Zeit</label>
        <select id="zeit" bind:value={form.zeit}>
          <option value="" disabled>Zeit wählen</option>
          {#each zeiten as z}<option value={z}>{z}</option>{/each}
        </select>

        <label for="zutaten-input">Zutaten</label>
        <div class="zutaten-input-row">
          <input type="text" id="zutaten-input" bind:value={zutatenInput} placeholder="z.B. Mehl" onkeydown={handleZutatKeydown}/>
          <button class="btn-zutat-add" onclick={zutatHinzufuegen} type="button">+</button>
        </div>
        {#if zutatenListe.length > 0}
          <div class="zutaten-tags-edit">
            {#each zutatenListe as z}
              <span class="zutat-tag-edit">
                {z}
                <button class="zutat-remove" onclick={() => zutatEntfernen(z)}>✕</button>
              </span>
            {/each}
          </div>
        {/if}

        <label for="descr">Beschreibung</label>
        <textarea id="descr" bind:value={form.description} placeholder="Kurze Beschreibung..."></textarea>

        <label for="imgurl">Bild URL</label>
        <input type="text" id="imgurl" bind:value={form.image_url} placeholder="https://i.imgur.com/beispiel.jpg"/>

        <div class="toggle-row">
          <label for="pub" class="toggle-label">Öffentlich sichtbar</label>
          <input type="checkbox" id="pub" bind:checked={form.is_public}/>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" onclick={() => showForm = false}>Abbrechen</button>
          <button onclick={saveRecipe}>Speichern</button>
        </div>
      </div>
    </div>
  {/if}
{/if}

<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :global(body) { font-family: 'DM Sans', sans-serif; background: #fafafa; color: #111; }

  nav {
    position: sticky; top: 0; z-index: 50;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px; height: 56px; background: #fff; border-bottom: 1px solid #e0e0e0;
  }

  .nav-logo { font-size: 25px; font-weight: 500; }
  .nav-links { display: flex; gap: 8px; align-items: center; }

  .nav-btn {
    width: auto; padding: 7px 16px; background: transparent; color: #666;
    border: none; border-radius: 6px; font-size: 13px; cursor: pointer;
    transition: background .2s, color .2s; font-family: 'DM Sans', sans-serif;
  }

  .nav-btn:hover { background: #f5f5f5; color: #111; }
  .nav-btn.active { background: #f0f0f0; color: #111; font-weight: 500; }
  .nav-login { background: #111; color: #fff; }
  .nav-login:hover { background: #333; color: #fff; }
  .nav-logout { color: #c0392b; }
  .nav-logout:hover { background: #fff0f0; color: #c0392b; }

  .screen { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #fff; }
  .card { width: 340px; display: flex; flex-direction: column; gap: 10px; }

  h1 { font-size: 20px; font-weight: 500; margin-bottom: 2px; }
  .sub, .page-sub { font-size: 13px; color: #888; margin-bottom: 10px; }

  label {
    display: block; font-size: 11px; font-weight: 500;
    letter-spacing: .06em; text-transform: uppercase; color: #999; margin-bottom: 2px;
  }

  input[type="text"], input[type="password"], input[type="email"] {
    width: 100%; padding: 11px 12px; border: 1px solid #e0e0e0; border-radius: 6px;
    font-size: 14px; color: #111; outline: none; transition: border-color .2s;
    font-family: 'DM Sans', sans-serif; background: #fff;
  }

  input:focus { border-color: #111; }

  select {
    width: 100%; padding: 11px 12px; border: 1px solid #e0e0e0; border-radius: 6px;
    font-size: 14px; color: #111; outline: none; background: #fff;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: border-color .2s;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23999' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 12px center;
  }

  select:focus { border-color: #111; }
  .error { font-size: 12px; color: #c0392b; }

  button {
    width: 100%; padding: 11px; background: #111; color: #fff; border: none;
    border-radius: 6px; font-size: 14px; cursor: pointer; transition: background .2s;
    font-family: 'DM Sans', sans-serif;
  }

  button:hover { background: #333; }
  .btn-secondary { background: #fff; color: #888; border: 1px solid #e0e0e0; }
  .btn-secondary:hover { background: #f5f5f5; color: #111; }

  .main { max-width: 1100px; margin: 0 auto; padding: 40px; }
  .main h2 { font-size: 22px; font-weight: 500; margin-bottom: 4px; }

  .filter-bar { display: flex; flex-wrap: wrap; gap: 10px; margin: 20px 0; align-items: center; }
  .filter-bar select { width: auto; min-width: 160px; }
  .search-input { width: auto; min-width: 180px; flex: 1; }

  .btn-reset {
    width: auto; padding: 9px 14px; background: #fff; color: #888;
    border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px; cursor: pointer; white-space: nowrap;
  }

  .btn-reset:hover { background: #f5f5f5; color: #c0392b; border-color: #c0392b; }

  .page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 4px; }
  .btn-add { width: auto; padding: 9px 18px; font-size: 13px; margin-top: 4px; }
  .empty { font-size: 14px; color: #aaa; margin: 20px 0; }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 8px; }

  .recipe-card {
    background: #fff; border: 1px solid #e0e0e0; border-radius: 10px;
    padding: 20px; display: flex; flex-direction: column; gap: 8px;
    cursor: pointer; transition: box-shadow .2s, transform .15s;
  }

  .recipe-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.08); transform: translateY(-2px); }

  .recipe-img { width: 100%; height: 160px; object-fit: cover; border-radius: 6px; }
  .recipe-top { display: flex; justify-content: space-between; align-items: center; }
  .category { font-size: 11px; font-weight: 500; letter-spacing: .06em; text-transform: uppercase; color: #999; }
  .time { font-size: 12px; color: #aaa; }
  .recipe-card h3 { font-size: 16px; font-weight: 500; }
  .author { font-size: 12px; color: #aaa; }

  .zutaten-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
  .zutat-tag { font-size: 11px; padding: 3px 8px; background: #f5f5f5; color: #555; border-radius: 20px; white-space: nowrap; }

  .zutaten-input-row { display: flex; gap: 8px; }
  .zutaten-input-row input { flex: 1; }

  .btn-zutat-add {
    width: 42px; padding: 0; flex-shrink: 0; background: #111; color: #fff;
    border: none; border-radius: 6px; font-size: 20px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
  }

  .btn-zutat-add:hover { background: #333; }

  .zutaten-tags-edit { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }

  .zutat-tag-edit {
    display: flex; align-items: center; gap: 4px;
    font-size: 12px; padding: 4px 10px; background: #f0f0f0; color: #333; border-radius: 20px;
  }

  .zutat-remove { width: auto; padding: 0; background: none; color: #999; border: none; font-size: 11px; cursor: pointer; line-height: 1; }
  .zutat-remove:hover { background: none; color: #c0392b; }

  .rating-section { display: flex; align-items: center; gap: 6px; margin-top: 4px; }
  .stars-display { font-size: 16px; color: #f0a500; letter-spacing: 2px; }
  .rating-info { font-size: 12px; color: #999; }

  .rate-row { display: flex; align-items: center; gap: 2px; margin-top: 2px; }
  .rate-label { font-size: 12px; color: #999; margin-right: 4px; }

  .star-btn { width: auto; padding: 2px 4px; background: none; color: #ccc; border: none; font-size: 18px; cursor: pointer; transition: color .15s; }
  .star-btn:hover { background: none; color: #f0a500; }

  .login-hint { font-size: 12px; color: #aaa; margin-top: 2px; }

  .link-btn { width: auto; background: none; color: #111; border: none; font-size: 12px; padding: 0; text-decoration: underline; cursor: pointer; display: inline; }
  .link-btn:hover { background: none; color: #555; }

  .visibility { margin-top: 2px; }
  .badge { display: inline-block; font-size: 11px; padding: 3px 8px; border-radius: 20px; font-weight: 500; }
  .public { background: #e8f5e9; color: #2e7d32; }
  .private { background: #f5f5f5; color: #888; }

  .actions { display: flex; gap: 8px; margin-top: 8px; }
  .btn-edit { width: auto; padding: 6px 14px; background: #f5f5f5; color: #111; border: none; border-radius: 6px; font-size: 12px; }
  .btn-edit:hover { background: #e8e8e8; }
  .btn-delete { width: auto; padding: 6px 14px; background: #fff0f0; color: #c0392b; border: none; border-radius: 6px; font-size: 12px; }
  .btn-delete:hover { background: #fde0e0; }

  .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.3); display: flex; align-items: center; justify-content: center; z-index: 100; }

  .modal {
    background: #fff; border-radius: 10px; padding: 32px; width: 440px;
    display: flex; flex-direction: column; gap: 10px; max-height: 90vh; overflow-y: auto;
  }

  .detail-modal { width: 520px; }
  .detail-img { width: 100%; height: 220px; object-fit: cover; border-radius: 8px; }
  .detail-top { display: flex; justify-content: space-between; align-items: center; }
  .detail-desc { font-size: 14px; color: #444; line-height: 1.7; }

  .modal h3 { font-size: 18px; font-weight: 500; margin-bottom: 4px; }

  .modal textarea {
    width: 100%; padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 6px;
    font-size: 13px; font-family: 'DM Sans', sans-serif; outline: none;
    resize: vertical; min-height: 80px; transition: border-color .2s;
  }

  .modal textarea:focus { border-color: #111; }

  .toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; }
  .toggle-label { font-size: 13px; color: #111; text-transform: none; letter-spacing: 0; font-weight: 400; margin: 0; }
  input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: #111; }

  .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }
  .modal-actions button { width: auto; padding: 9px 18px; }
  .btn-cancel { background: #f5f5f5 !important; color: #111 !important; }
  .btn-cancel:hover { background: #e8e8e8 !important; }
</style>