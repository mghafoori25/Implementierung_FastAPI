import { useState, useEffect } from "react";

interface Produkt {
  id: number;
  name: string;
  preis: number;
  kategorie: string;
  istVerfuegbar: boolean;
}

function App() {
  const [produkte, setProdukte] = useState<Produkt[]>([]);
  const [laedt, setLaedt] = useState(true);
  const [fehler, setFehler] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/products")
      .then((res) => {
        if (!res.ok) throw new Error(`Status: ${res.status}`);
        return res.json() as Promise<Produkt[]>;
      })
      .then((daten) => {
        setProdukte(daten);
        setLaedt(false);
      })
      .catch((err) => {
        setFehler(err.message);
        setLaedt(false);
      });
  }, []);

  if (laedt) {
    return <div>Lade Produkte von der API...</div>;
  }

  if (fehler) {
    return <div style={{ color: "red" }}>Fehler: {fehler}</div>;
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h1>Produktverwaltung (API-Version)</h1>

      <table border={1} cellPadding={8} style={{ width: "100%" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Preis</th>
            <th>Kategorie</th>
            <th>Verfügbar</th>
          </tr>
        </thead>

        <tbody>
          {produkte.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.name}</td>
              <td>€{p.preis.toFixed(2)}</td>
              <td>{p.kategorie}</td>
              <td>{p.istVerfuegbar ? "✅" : "❌"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;