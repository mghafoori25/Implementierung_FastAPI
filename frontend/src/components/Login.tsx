import { useState } from "react";
import type { FormEvent } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

function Login() {
  const [username, setUsername] = useState("neuer_testuser");
  const [password, setPassword] = useState("geheimespasswort");
  const [message, setMessage] = useState("");

  const { login } = useAuth();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post("/token", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      login(response.data.access_token);
      setMessage("Login erfolgreich. Token wurde gespeichert.");
    } catch {
      setMessage("Login fehlgeschlagen.");
    }
  };

  return (
    <div>
      <h1>Login</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Benutzername:</label>
          <br />
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </div>

        <div>
          <label>Passwort:</label>
          <br />
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>

        <br />

        <button type="submit">Einloggen</button>
      </form>

      {message && <p>{message}</p>}
    </div>
  );
}

export default Login;