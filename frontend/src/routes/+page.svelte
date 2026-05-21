<script>
  let username = $state('');
  let password = $state('');
  let error = $state(false);
  let loggedIn = $state(false);

  const VALID_USER = 'admin';
  const VALID_PASS = 'passwort123';

  function login() {
    if (username === VALID_USER && password === VALID_PASS) {
      error = false;
      loggedIn = true;
    } else {
      error = true;
    }
  }
  let recipes = $state([
    { id: 1, title: 'Spaghetti Bolognese', category: 'Pasta', time: '30 min', ingredients: 'Hackfleisch, Tomaten, Zwiebeln', description: 'Klassische italienische Bolognese.' },
    { id: 2, title: 'Pancakes', category: 'Frühstück', time: '20 min', ingredients: 'Mehl, Eier, Milch, Butter', description: 'Fluffige amerikanische Pancakes.' },
  ]);
  let showForm = $state(false);
  let editRecipe = $state(null);
  let form = $state({ title: '', category: '', time: '', ingredients: '', description: '' });

  function openAdd() {
    editRecipe = null;
    form = { title: '', category: '', time: '', ingredients: '', description: '' };
    showForm = true;
  }

  function openEdit(r) {
    editRecipe = r;
    form = { ...r };
    showForm = true;
  }

  function saveRecipe() {
    if (!form.title) return;
    if (editRecipe) {
      recipes = recipes.map(r => r.id === editRecipe.id ? { ...form, id: r.id } : r);
    } else {
      recipes = [...recipes, { ...form, id: Date.now() }];
    }
    showForm = false;
  }

  function deleteRecipe(id) {
    recipes = recipes.filter(r => r.id !== id);
  }
</script>

{#if !loggedIn}
  <div class="screen">
    <div class="card">
      <h1>Anmelden</h1>
      <p class="sub">Bitte gib deine Zugangsdaten ein.</p>

      <label>Benutzername</label>
      <input type="text" bind:value={username} placeholder="Benutzername"/>
      <label>Passwort</label>
      <input type="password" bind:value={password} placeholder="Passwort"/>

      {#if error}
        <p class="error">Benutzername oder Passwort falsch.</p>
      {/if}

      <button onclick={login}>Anmelden</button>
    </div>
  </div>

  {:else}
  <div class="main">
    <header>
      <h2>Meine Rezepte</h2>
      <button class="btn-add" onclick={openAdd}>+ Rezept hinzufügen</button>
    </header>

    <div class="grid">
      {#each recipes as r}
        <div class="recipe-card">
          <div class="recipe-top">
            <span class="category">{r.category}</span>
            <span class="time">⏱ {r.time}</span>
          </div>
          <h3>{r.title}</h3>
          <p class="desc">{r.description}</p>
          <p class="ingredients"><strong>Zutaten:</strong> {r.ingredients}</p>
          <div class="actions">
            <button class="btn-edit" onclick={() => openEdit(r)}>Bearbeiten</button>
            <button class="btn-delete" onclick={() => deleteRecipe(r.id)}>Löschen</button>
          </div>
        </div>
      {/each}
    </div>

    {#if showForm}
      <div class="overlay" onclick={() => showForm = false}>
        <div class="modal" onclick={(e) => e.stopPropagation()}>
          <h3>{editRecipe ? 'Rezept bearbeiten' : 'Neues Rezept'}</h3>

          <label>Titel</label>
          <input type="text" bind:value={form.title} placeholder="z.B. Spaghetti Bolognese"/>

          <label>Kategorie</label>
          <input type="text" bind:value={form.category} placeholder="z.B. Pasta"/>

          <label>Zeit</label>
          <input type="text" bind:value={form.time} placeholder="z.B. 30 min"/>

          <label>Zutaten</label>
          <input type="text" bind:value={form.ingredients} placeholder="z.B. Mehl, Eier, Milch"/>

          <label>Beschreibung</label>
          <textarea bind:value={form.description} placeholder="Kurze Beschreibung..."></textarea>

          <div class="modal-actions">
            <button class="btn-cancel" onclick={() => showForm = false}>Abbrechen</button>
            <button class="btn" onclick={saveRecipe}>Speichern</button>
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

  .card { width: 340px; }

  h1 {
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .sub {
    font-size: 13px;
    color: #888;
    margin-bottom: 28px;
  }

  label {
    display: block;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 6px;
    margin-top: 14px;
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
  }

  input:focus { border-color: #111; }

  .error {
    font-size: 12px;
    color: #c0392b;
    margin-top: 10px;
  }

  button {
    width: 100%;
    margin-top: 20px;
    padding: 11px;
    background: #111;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    transition: background .2s;
  }

  button:hover { background: #333; }

  .main {
    min-height: 100vh;
    background: #fff;
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
    padding: 9px 18px;
    background: #111;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: background .2s;
  }

  .btn-add:hover { background: #333; }

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
    padding: 6px 14px;
    background: #000000;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    transition: background .2s;
  }

  .btn-edit:hover { background: #444242; }

  .btn-delete {
    padding: 6px 14px;
    background: #fff0f0;
    color: #c0392b;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    transition: background .2s;
  }

  .btn-delete:hover { background: #fde0e0; }

  /* Modal */
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .modal {
    background: #fff;
    border-radius: 10px;
    padding: 32px;
    width: 440px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .modal h3 {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .modal input, .modal textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    outline: none;
    transition: border-color .2s;
  }

  .modal input:focus, .modal textarea:focus { border-color: #111; }

  .modal textarea {
    resize: vertical;
    min-height: 80px;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .btn-cancel {
    padding: 9px 18px;
    background: #494949;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
  }
</style>