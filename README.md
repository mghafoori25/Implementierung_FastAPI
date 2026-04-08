# Assignment: Erste FastAPI – Product API

## Lernziele

Nach diesem Assignment können Sie:

- eine einfache FastAPI-Anwendung starten und testen
- Pydantic-Modelle für Requests und Responses definieren
- CRUD-Endpunkte für eine Ressource (Produkt) implementieren
- kleine Änderungen/Erweiterungen an einer bestehenden API vornehmen

---

### I. Installation und Setup

#### A) Backend Setup (FastAPI)

**Voraussetzungen:**

- Python 3.8 oder höher
- pip (Python Package Manager)

**Windows Installation:**

```bash
# 1. Python von python.org downloaden und installieren
# 2. Neues Projektverzeichnis erstellen
mkdir product-api
cd product-api

# 3. Virtual Environment erstellen
python -m venv venv

# 4. Virtual Environment aktivieren
venv\Scripts\activate

# 5. FastAPI und Dependencies installieren
pip install fastapi uvicorn[standard] pydantic sqlalchemy

# 6. main.py erstellen (siehe Code oben)

# 7. Server starten
uvicorn main:app --reload
```

**macOS Installation:**

```bash
# 1. Python installieren (wenn nicht vorhanden)
brew install python

# 2. Projektverzeichnis erstellen
mkdir product-api
cd product-api

# 3. Virtual Environment erstellen
python3 -m venv venv

# 4. Aktivieren
source venv/bin/activate

# 5. Dependencies installieren
pip install fastapi uvicorn[standard] pydantic sqlalchemy

# 6. Server starten
uvicorn main:app --reload
```

**Linux (Ubuntu/Debian) Installation:**

```bash
# 1. Python installieren
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. Projektverzeichnis
mkdir product-api
cd product-api

# 3. Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 4. Dependencies
pip install fastapi uvicorn[standard] pydantic sqlalchemy

# 5. Server starten
uvicorn main:app --reload
```

**Nach Start:**

- API läuft auf `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### B) Frontend Setup (React + TypeScript)

**Voraussetzungen:**

- Node.js 18+ und npm

**Windows Installation:**

```bash
# 1. Node.js von nodejs.org downloaden und installieren

# 2. React App mit Vite erstellen
npm create vite@latest product-frontend -- --template react-ts

# 3. In Projektverzeichnis wechseln
cd product-frontend

# 4. Dependencies installieren
npm install

# 5. Axios für API Calls installieren
npm install axios

# 6. Development Server starten
npm run dev
```

**macOS Installation:**

```bash
# 1. Node.js installieren
brew install node

# 2. React App erstellen
npm create vite@latest product-frontend -- --template react-ts
cd product-frontend

# 3. Dependencies
npm install
npm install axios

# 4. Server starten
npm run dev
```

**Linux Installation:**

```bash
# 1. Node.js installieren
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. React App erstellen
npm create vite@latest product-frontend -- --template react-ts
cd product-frontend

# 3. Dependencies
npm install
npm install axios

# 4. Server starten
npm run dev
```

**Nach Start:**

- React App läuft auf `http://localhost:5173`

#### C) CORS Configuration (FastAPI)

Um Frontend und Backend zu verbinden, muss CORS aktiviert werden:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Dev Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 1. Vorbereitung

### 1.1 Repository / Starter-Code

Legen Sie ein Git-Repository mit folgendem Grundgerüst an:

```text
fastapi-product-api/
├─ app/
│  ├─ __init__.py
│  └─ main.py          # Starter-Code
├─ requirements.txt
└─ README.md           # Dieses Assignment
```

### 1.2 Installation

1. Python 3.10+ installieren.
2. Virtuelle Umgebung anlegen (empfohlen):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

4. Server starten:

```bash
fastapi dev app/main.py
```

5. Dokumentation im Browser öffnen:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

---

## 2. Starter-Code (gegeben)

Datei: `app/main.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Product API",
    description="API für Produktverwaltung (Starter-Version)",
    version="0.1.0"
)

# In-Memory Database (nur für Demo, geht beim Neustart verloren)
products_db = []


# ---------- Pydantic Models ----------

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    category: str

    @validator("price")
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Preis muss positiv sein")
        return v


class ProductCreate(ProductBase):
    """Input-Modell für Produkt-Erstellung"""
    pass


class ProductUpdate(BaseModel):
    """Input-Modell für Produkt-Update (alle Felder optional)"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None


class ProductResponse(ProductBase):
    """Output-Modell für API-Responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---------- Endpoints ----------

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## 3. Aufgabe Teil A – Erste API-Endpunkte implementieren

### Ziel

Erweitern Sie den Starter-Code so, dass eine vollständige CRUD-API für Produkte entsteht.

### A.1 POST `/products/` – Produkt erstellen

Implementieren Sie in `app/main.py`:

```python
@app.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """
    Erstellt ein neues Produkt.

    - **name**: Produktname (required)
    - **description**: Produktbeschreibung (optional)
    - **price**: Preis in Euro (required, > 0)
    - **category**: Kategorie (required)
    """
    # TODO: Produkt in products_db einfügen und zurückgeben
```

Anforderungen:

- Erzeugen Sie aus `product` ein `dict` (z.B. mit `.dict()`).
- Ergänzen Sie:
  - eine eindeutige `id` (z.B. `len(products_db) + 1`)
  - `created_at` (aktueller Zeitpunkt)
  - `updated_at` (aktueller Zeitpunkt)
- Fügen Sie das Produkt in `products_db` ein.
- Geben Sie das Produkt-Dict zurück (FastAPI kümmert sich um die Serialisierung).

Test:

- Öffnen Sie `/docs` und testen Sie den Endpunkt mit verschiedenen Produkten.
- Überprüfen Sie Validierungsfehler (z.B. `price <= 0`).

---

### A.2 GET `/products/` – Liste aller Produkte

Implementieren Sie:

```python
@app.get("/products/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
):
    """
    Gibt eine Liste von Produkten zurück.

    - **skip**: Anzahl zu überspringender Einträge (Pagination)
    - **limit**: maximale Anzahl von Einträgen
    - **category**: optionaler Filter nach Kategorie
    """
    # TODO: Filterung & Pagination implementieren
```

Anforderungen:

- Starten Sie mit der vollständigen `products_db`.
- Wenn `category` gesetzt ist, filtern Sie nach `p["category"] == category`.
- Wenden Sie `skip` und `limit` auf die (ggf. gefilterte) Liste an.
- Geben Sie die resultierende Liste zurück.

---

### A.3 GET `/products/{product_id}` – Einzelnes Produkt

Implementieren Sie:

```python
@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Gibt ein spezifisches Produkt zurück.
    """
    # TODO: Produkt anhand der ID suchen und zurückgeben
```

Anforderungen:

- Suchen Sie das Produkt in `products_db` (z.B. mit `next(...)`).
- Wenn kein Produkt gefunden wird:
  - Werfen Sie eine `HTTPException` mit `status_code=404` und `detail="Produkt nicht gefunden"`.

---

### A.4 PUT `/products/{product_id}` – Produkt aktualisieren

Implementieren Sie:

```python
@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate):
    """
    Aktualisiert ein bestehendes Produkt.
    """
    # TODO: Produkt suchen, Felder aktualisieren
```

Anforderungen:

- Suchen Sie das Produkt wie in A.3.
- Falls nicht gefunden → `HTTPException(404, "Produkt nicht gefunden")`.
- Erzeugen Sie ein Dict aus `product_update` mit `exclude_unset=True`, z.B.:

```python
update_data = product_update.dict(exclude_unset=True)
```

- Aktualisieren Sie nur die Felder, die in `update_data` enthalten sind.
- Setzen Sie `updated_at` auf den aktuellen Zeitpunkt.
- Geben Sie das aktualisierte Produkt zurück.

---

### A.5 DELETE `/products/{product_id}` – Produkt löschen

Implementieren Sie:

```python
@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """
    Löscht ein Produkt.
    """
    # TODO: Produkt löschen oder 404
```

Anforderungen:

- Suchen Sie das Produkt wie in A.3.
- Falls nicht gefunden → `HTTPException(404, "Produkt nicht gefunden")`.
- Entfernen Sie das Produkt aus `products_db`.
- Geben Sie `None` zurück (204 hat keinen Body).

---

## 4. Aufgabe Teil B – Erweiterungen / Änderungen

Führen Sie die folgenden Änderungen auf Basis Ihrer laufenden API durch.

### B.1 Neues Feld `stock` hinzufügen

Ziel: Jedes Produkt soll zusätzlich ein Feld `stock` (int, ≥ 0) bekommen.

1. Ergänzen Sie in `ProductBase`:

```python
stock: int = Field(..., ge=0)
```

2. Passen Sie `ProductCreate` und `ProductResponse` automatisch an (erben von `ProductBase`).
3. Testen Sie:
   - POST `/products/` mit gültigem `stock`.
   - Validierungsfehler bei negativem `stock`.

---

### B.2 Zusätzlicher Filter: `min_price` und `max_price`

Erweitern Sie den GET-Endpunkt `/products/`:

```python
@app.get("/products/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    ...
```

Anforderungen:

- Wenn `min_price` gesetzt ist, filtern Sie zusätzlich auf `price >= min_price`.
- Wenn `max_price` gesetzt ist, filtern Sie zusätzlich auf `price <= max_price`.
- Kombinieren Sie Filter (Kategorie + Preis) logisch UND.

---

### B.3 Fehlerhandling-Verbesserung (optional)

Optional (für Schnellere):

- Fügen Sie eine einfache Validierung hinzu, die `min_price <= max_price` sicherstellt.
- Falls diese Bedingung verletzt ist, werfen Sie eine `HTTPException` mit `400 Bad Request`.

---

## 5. Abgabe

Sie geben ab:

- Link zu Ihrem GitHub-Repository (Fork des Starter-Repos).
- Die API muss lokal startbar sein mit:

```bash
fastapi dev app/main.py
```

- In der Datei `README_STUDENT.md`:
  - Kurze Beschreibung der von Ihnen umgesetzten Features.
  - 1–2 Screenshots aus der Swagger UI (/docs), die Ihre Endpunkte zeigen.

---

## 6. Bonus (freiwillig)

Wenn Sie noch weitergehen möchten:

- Fügen Sie einen asynchronen Endpunkt hinzu, der mehrere „Fake-APIs“ parallel aufruft (z.B. mit `httpx.AsyncClient` und `asyncio.gather`).
- Implementieren Sie eine sehr einfache „Authentication“-Simulation (z.B. Header `X-API-Key` prüfen) und schützen Sie einen Endpunkt damit.

Viel Erfolg!

[^1]: https://github.com/rzmk/fastapi-practice

[^2]: https://github.com/hygull/fastapi-kickstart-guide

[^3]: https://github.com/fastapi/fastapi

[^4]: https://github.com/Ayushupadhyay14/LearnFastapI

[^5]: https://www.youtube.com/watch?v=Lu8lXXlstvM

[^6]: https://www.youtube.com/watch?v=dglcDIUTSsY

[^7]: https://github.com/HAL24K/fast-api-training

[^8]: https://www.youtube.com/watch?v=dglcDIUTSsY\&vl=de

[^9]: https://www.youtube.com/watch?v=8TMQcRcBnW8

[^10]: https://fastapi.tiangolo.com/tutorial/first-steps/

[^11]: https://docs.github.com/en/rest/classroom/classroom

[^12]: https://www.geeksforgeeks.org/python/creating-first-rest-api-with-fastapi/

[^13]: https://github.com/rochacbruno/fastapi-workshop

[^14]: https://www.youtube.com/watch?v=ICnKq9fgLrI

[^15]: https://github.com/CatalinStefan/full-fastapi-course
