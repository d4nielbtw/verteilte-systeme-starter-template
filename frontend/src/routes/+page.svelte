<script>
  // Auth
  let username = $state('');
  let password = $state('');
  let email = $state('');
  let error = $state('');
  let loggedIn = $state(false);
  let showRegister = $state(false);
  let token = $state('');

  // Rezepte
  let recipes = $state([]);
  let showForm = $state(false);
  let editRecipe = $state(null);
  let form = $state({ Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '' });

  const API = 'http://localhost:8000';

  // Auth Funktionen
  async function login() {
    error = '';
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch(`${API}/token`, {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      const data = await res.json();
      token = data.access_token;
      localStorage.setItem('token', token);
      loggedIn = true;
      await loadRecipes();
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

  // Rezept Funktionen
  async function loadRecipes() {
    const res = await fetch(`${API}/rezepte`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      recipes = await res.json();
    }
  }

  function openAdd() {
    editRecipe = null;
    form = { Kochrezept_Name: '', kategorie: '', zeit: '', zutaten: '', description: '' };
    showForm = true;
  }

  function openEdit(r) {
    editRecipe = r;
    form = {
      Kochrezept_Name: r.Kochrezept_Name,
      kategorie: r.kategorie,
      zeit: r.zeit,
      zutaten: r.zutaten,
      description: r.description
    };
    showForm = true;
  }

  async function saveRecipe() {
    if (!form.Kochrezept_Name) return;

    if (editRecipe) {
      const res = await fetch(`${API}/rezepte/${editRecipe.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(form)
      });
      if (res.ok) await loadRecipes();
    } else {
      const res = await fetch(`${API}/rezepte`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(form)
      });
      if (res.ok) await loadRecipes();
    }
    showForm = false;
  }

  async function deleteRecipe(id) {
    const res = await fetch(`${API}/rezepte/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) await loadRecipes();
  }
</script>

{#if !loggedIn}
  <div class="screen">
    <div class="card">

      {#if !showRegister}
        <h1>Anmelden</h1>
        <p class="sub">Bitte gib deine Zugangsdaten ein.</p>

        <label for="user">Benutzername</label>
        <input type="text" id="user" bind:value={username} placeholder="Benutzername"/>

        <label for="pass">Passwort</label>
        <input type="password" id="pass" bind:value={password} placeholder="Passwort"/>

        {#if error}
          <p class="error">{error}</p>
        {/if}

        <button onclick={login}>Anmelden</button>
        <button class="btn-secondary" onclick={() => { showRegister = true; error = ''; }}>
          Noch kein Konto? Registrieren
        </button>

      {:else}
        <h1>Registrieren</h1>
        <p class="sub">Erstelle ein neues Konto.</p>

        <label for="reg-user">Benutzername</label>
        <input type="text" id="reg-user" bind:value={username} placeholder="Benutzername"/>

        <label for="reg-email">E-Mail</label>
        <input type="email" id="reg-email" bind:value={email} placeholder="E-Mail"/>

        <label for="reg-pass">Passwort</label>
        <input type="password" id="reg-pass" bind:value={password} placeholder="Passwort"/>

        {#if error}
          <p class="error">{error}</p>
        {/if}

        <button onclick={register}>Konto erstellen</button>
        <button class="btn-secondary" onclick={() => { showRegister = false; error = ''; }}>
          Zurück zum Login
        </button>
      {/if}

    </div>
  </div>

{:else}
  <div class="main">
    <header>
      <h2>Meine Rezepte</h2>
      <button class="btn-add" onclick={openAdd}>+ Rezept hinzufügen</button>
    </header>

    {#if recipes.length === 0}
      <p class="empty">Noch keine Rezepte. Füge dein erstes hinzu!</p>
    {/if}

    <div class="grid">
      {#each recipes as r}
        <div class="recipe-card">
          <div class="recipe-top">
            <span class="category">{r.kategorie}</span>
            <span class="time">⏱ {r.zeit}</span>
          </div>
          <h3>{r.Kochrezept_Name}</h3>
          <p class="desc">{r.description}</p>
          <p class="ingredients"><strong>Zutaten:</strong> {r.zutaten}</p>
          <div class="actions">
            <button class="btn-edit" onclick={() => openEdit(r)}>Bearbeiten</button>
            <button class="btn-delete" onclick={() => deleteRecipe(r.id)}>Löschen</button>
          </div>
        </div>
      {/each}
    </div>

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

          <div class="modal-actions">
            <button class="btn-cancel" onclick={() => showForm = false}>Abbrechen</button>
            <button onclick={saveRecipe}>Speichern</button>
          </div>
        </div>
      </div>
    {/if}
  </div>
{/if}

<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :global(body) {
    font-family: 'DM Sans', sans-serif;
    background: #fff;
  }

  .screen {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
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

  .sub {
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

  input {
    width: 100%;
    padding: 11px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
    color: #111;
    outline: none;
    transition: border-color .2s;
    font-family: 'DM Sans', sans-serif;
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

  .btn-secondary:hover {
    background: #f5f5f5;
    color: #111;
  }

  .main {
    min-height: 100vh;
    padding: 40px;
    background: #fff;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
  }

  header h2 {
    font-size: 22px;
    font-weight: 500;
  }

  .btn-add {
    width: auto;
    padding: 9px 18px;
    font-size: 13px;
  }

  .empty {
    font-size: 14px;
    color: #aaa;
    margin-bottom: 20px;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }

  .recipe-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
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

  .time {
    font-size: 12px;
    color: #aaa;
  }

  .recipe-card h3 {
    font-size: 16px;
    font-weight: 500;
  }

  .desc {
    font-size: 13px;
    color: #666;
  }

  .ingredients {
    font-size: 12px;
    color: #888;
  }

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

  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    cursor: default;
  }

  .modal {
    background: #fff;
    border-radius: 10px;
    padding: 32px;
    width: 440px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    cursor: default;
  }

  .modal h3 {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 4px;
  }

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

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .modal-actions button {
    width: auto;
    padding: 9px 18px;
  }

  .btn-cancel {
    background: #f5f5f5 !important;
    color: #111 !important;
  }

  .btn-cancel:hover { background: #e8e8e8 !important; }
</style>