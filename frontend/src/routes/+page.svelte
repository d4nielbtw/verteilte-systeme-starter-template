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

  // Seiten: 'start' | 'meine'
  let page = $state('start');

  // Rezepte
  let publicRecipes = $state([]);
  let myRecipes = $state([]);
  let showForm = $state(false);
  let editRecipe = $state(null);
  let form = $state({ Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '', image_url: '', is_public: false });

  const API = 'http://localhost:8000';

  // Startseite laden (ohne Login)
  async function loadPublic() {
    const res = await fetch(`${API}/startseite`);
    if (res.ok) publicRecipes = await res.json();
  }

  onMount(() => {
  loadPublic();
});
  // Auth
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

  // Meine Rezepte
  async function loadMyRecipes() {
    const res = await fetch(`${API}/rezepte`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) myRecipes = await res.json();
  }

  function openAdd() {
    editRecipe = null;
    form = { Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '', image_url: '', is_public: false };
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
    showForm = true;
  }

  async function saveRecipe() {
    if (!form.Kochrezept_Name) return;
    const method = editRecipe ? 'PUT' : 'POST';
    const url = editRecipe ? `${API}/rezepte/${editRecipe.id}` : `${API}/rezepte`;
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(form)
    });
    if (res.ok) {
      await loadMyRecipes();
      await loadPublic();
    }
    showForm = false;
  }

  async function deleteRecipe(id) {
    const res = await fetch(`${API}/rezepte/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      await loadMyRecipes();
      await loadPublic();
    }
  }

  // Bewertung
  async function bewerten(rezeptId, sterne) {
    if (!loggedIn) return;
    await fetch(`${API}/rezepte/${rezeptId}/bewertung`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ sterne })
    });
    await loadPublic();
  }

  function sterne(n) {
    return Array.from({ length: 5 }, (_, i) => i < n ? '★' : '☆').join('');
  }
</script>

<!-- ══════════════════════════════════════════════
     LOGIN / REGISTER OVERLAY
══════════════════════════════════════════════ -->
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
        <button class="btn-secondary" onclick={() => { showRegister = true; error = ''; }}>
          Noch kein Konto? Registrieren
        </button>
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
        <button class="btn-secondary" onclick={() => { showRegister = false; error = ''; }}>
          Zurück zum Login
        </button>
      {/if}
    </div>
  </div>

<!-- ══════════════════════════════════════════════
     HAUPTSEITE
══════════════════════════════════════════════ -->
{:else}
  <!-- Navbar -->
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

  <!-- STARTSEITE -->
  {#if page === 'start'}
    <div class="main">
      <h2>Öffentliche Rezepte</h2>
      <p class="page-sub">Entdecke Rezepte aus der Community</p>

      {#if publicRecipes.length === 0}
        <p class="empty">Noch keine öffentlichen Rezepte vorhanden.</p>
      {/if}

      <div class="grid">
        {#each publicRecipes as r}
          <div class="recipe-card">
            {#if r.image_url}
              <img src={r.image_url} alt={r.Kochrezept_Name} class="recipe-img"/>
            {/if}
            <div class="recipe-top">
              <span class="category">{r.kategorie}</span>
              <span class="time">⏱ {r.zeit}</span>
            </div>
            <h3>{r.Kochrezept_Name}</h3>
            <p class="desc">{r.description}</p>
            <p class="ingredients"><strong>Zutaten:</strong> {r.zutaten}</p>

            <!-- Bewertung -->
            <div class="rating-section">
              <span class="stars-display">{sterne(Math.round(r.durchschnitt))}</span>
              <span class="rating-info">
                {r.durchschnitt > 0 ? r.durchschnitt.toFixed(1) : '–'} 
                ({r.anzahl_bewertungen} {r.anzahl_bewertungen === 1 ? 'Bewertung' : 'Bewertungen'})
              </span>
            </div>

            {#if loggedIn}
              <div class="rate-row">
                <span class="rate-label">Bewerten:</span>
                {#each [1,2,3,4,5] as s}
                  <button class="star-btn" onclick={() => bewerten(r.id, s)}>★</button>
                {/each}
              </div>
            {:else}
              <p class="login-hint">
                <button class="link-btn" onclick={() => { page = 'login'; showRegister = false; }}>Anmelden</button>
                um zu bewerten
              </p>
            {/if}
          </div>
        {/each}
      </div>
    </div>

  <!-- MEINE REZEPTE -->
  {:else if page === 'meine'}
    <div class="main">
      <div class="page-header">
        <div>
          <h2>Meine Rezepte</h2>
          <p class="page-sub">Verwalte deine persönlichen Rezepte</p>
        </div>
        <button class="btn-add" onclick={openAdd}>+ Rezept hinzufügen</button>
      </div>

      {#if myRecipes.length === 0}
        <p class="empty">Noch keine Rezepte. Füge dein erstes hinzu!</p>
      {/if}

      <div class="grid">
        {#each myRecipes as r}
          <div class="recipe-card">
            {#if r.image_url}
              <img src={r.image_url} alt={r.Kochrezept_Name} class="recipe-img"/>
            {/if}
            <div class="recipe-top">
              <span class="category">{r.kategorie}</span>
              <span class="time">⏱ {r.zeit}</span>
            </div>
            <h3>{r.Kochrezept_Name}</h3>
            <p class="desc">{r.description}</p>
            <p class="ingredients"><strong>Zutaten:</strong> {r.zutaten}</p>

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

            <div class="actions">
              <button class="btn-edit" onclick={() => openEdit(r)}>Bearbeiten</button>
              <button class="btn-delete" onclick={() => deleteRecipe(r.id)}>Löschen</button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <!-- MODAL -->
  {#if showForm}
    <div class="overlay" role="button" tabindex="0" onclick={() => showForm = false} onkeydown={() => showForm = false}>
      <div class="modal" role="button" tabindex="0" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
        <h3>{editRecipe ? 'Rezept bearbeiten' : 'Neues Rezept'}</h3>

        <label for="title">Titel</label>
        <input type="text" id="title" bind:value={form.Kochrezept_Name} placeholder="z.B. Spaghetti Bolognese"/>

        <label for="cat">Kategorie</label>
        <input type="text" id="cat" bind:value={form.kategorie} placeholder="z.B. Pasta"/>

        <label for="zeit">Zeit</label>
        <input type="text" id="zeit" bind:value={form.zeit} placeholder="z.B. 30 min"/>

        <label for="ingr">Zutaten</label>
        <input type="text" id="ingr" bind:value={form.zutaten} placeholder="z.B. Mehl, Eier, Milch"/>

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

  :global(body) {
    font-family: 'DM Sans', sans-serif;
    background: #fafafa;
    color: #111;
  }

  /* ── Navbar ── */
  nav {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 56px;
    background: #fff;
    border-bottom: 1px solid #e0e0e0;
  }

  .nav-logo {
    font-size: 23px;
    font-weight: 500;
  }

  .nav-links {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .nav-btn {
    width: auto;
    padding: 7px 16px;
    background: transparent;
    color: #666;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: background .2s, color .2s;
    font-family: 'DM Sans', sans-serif;
  }

  .nav-btn:hover { background: #f5f5f5; color: #111; }
  .nav-btn.active { background: #f0f0f0; color: #111; font-weight: 500; }

  .nav-login {
    background: #111;
    color: #fff;
  }

  .nav-login:hover { background: #333; color: #fff; }

  .nav-logout {
    color: #c0392b;
  }

  .nav-logout:hover { background: #fff0f0; color: #c0392b; }

  /* ── Login Screen ── */
  .screen {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fff;
  }

  .card {
    width: 340px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  h1 {
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 2px;
  }

  .sub, .page-sub {
    font-size: 13px;
    color: #888;
    margin-bottom: 10px;
  }

  label {
    display: block;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 2px;
  }

  input[type="text"],
  input[type="password"],
  input[type="email"] {
    width: 100%;
    padding: 11px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    color: #111;
    outline: none;
    transition: border-color .2s;
    font-family: 'DM Sans', sans-serif;
    background: #fff;
  }

  input:focus { border-color: #111; }

  .error {
    font-size: 12px;
    color: #c0392b;
  }

  button {
    width: 100%;
    padding: 11px;
    background: #111;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background .2s;
    font-family: 'DM Sans', sans-serif;
  }

  button:hover { background: #333; }

  .btn-secondary {
    background: #fff;
    color: #888;
    border: 1px solid #e0e0e0;
  }

  .btn-secondary:hover { background: #f5f5f5; color: #111; }

  /* ── Main ── */
  .main {
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 40px;
  }

  .main h2 {
    font-size: 22px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 28px;
  }

  .btn-add {
    width: auto;
    padding: 9px 18px;
    font-size: 13px;
    margin-top: 4px;
  }

  .empty {
    font-size: 14px;
    color: #aaa;
    margin: 20px 0;
  }

  /* ── Grid ── */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 24px;
  }

  .recipe-card {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .recipe-img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    border-radius: 6px;
  }

  .recipe-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .category {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #999;
  }

  .time { font-size: 12px; color: #aaa; }

  .recipe-card h3 { font-size: 16px; font-weight: 500; }
  .desc { font-size: 13px; color: #666; }
  .ingredients { font-size: 12px; color: #888; }

  /* ── Bewertung ── */
  .rating-section {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 4px;
  }

  .stars-display { font-size: 16px; color: #f0a500; letter-spacing: 2px; }
  .rating-info { font-size: 12px; color: #999; }

  .rate-row {
    display: flex;
    align-items: center;
    gap: 2px;
    margin-top: 2px;
  }

  .rate-label { font-size: 12px; color: #999; margin-right: 4px; }

  .star-btn {
    width: auto;
    padding: 2px 4px;
    background: none;
    color: #ccc;
    border: none;
    font-size: 18px;
    cursor: pointer;
    transition: color .15s;
  }

  .star-btn:hover { background: none; color: #f0a500; }

  .login-hint {
    font-size: 12px;
    color: #aaa;
    margin-top: 2px;
  }

  .link-btn {
    width: auto;
    background: none;
    color: #111;
    border: none;
    font-size: 12px;
    padding: 0;
    text-decoration: underline;
    cursor: pointer;
    display: inline;
  }

  .link-btn:hover { background: none; color: #555; }

  /* ── Badges ── */
  .visibility { margin-top: 2px; }

  .badge {
    display: inline-block;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 20px;
    font-weight: 500;
  }

  .public { background: #e8f5e9; color: #2e7d32; }
  .private { background: #f5f5f5; color: #888; }

  /* ── Actions ── */
  .actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }

  .btn-edit {
    width: auto;
    padding: 6px 14px;
    background: #f5f5f5;
    color: #111;
    border: none;
    border-radius: 6px;
    font-size: 12px;
  }

  .btn-edit:hover { background: #e8e8e8; }

  .btn-delete {
    width: auto;
    padding: 6px 14px;
    background: #fff0f0;
    color: #c0392b;
    border: none;
    border-radius: 6px;
    font-size: 12px;
  }

  .btn-delete:hover { background: #fde0e0; }

  /* ── Modal ── */
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .modal {
    background: #fff;
    border-radius: 10px;
    padding: 32px;
    width: 440px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal h3 { font-size: 18px; font-weight: 500; margin-bottom: 4px; }

  .modal textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    outline: none;
    resize: vertical;
    min-height: 80px;
    transition: border-color .2s;
  }

  .modal textarea:focus { border-color: #111; }

  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
  }

  .toggle-label {
    font-size: 13px;
    color: #111;
    text-transform: none;
    letter-spacing: 0;
    font-weight: 400;
    margin: 0;
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: #111;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .modal-actions button { width: auto; padding: 9px 18px; }

  .btn-cancel {
    background: #f5f5f5 !important;
    color: #111 !important;
  }

  .btn-cancel:hover { background: #e8e8e8 !important; }
</style>