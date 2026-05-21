<script>
  let username = '';
  let password = '';
  let error = false;
  let loggedIn = false;

  //Zugangsdaten  (später aus Datenbank)
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

      <button on:click={login}>Anmelden</button>
    </div>
  </div>

{:else}
  <div class="main">

    <!-- inhalt nach login-->

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
</style>