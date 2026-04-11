# Dependency Injection in FastAPI mit SQLAlchemy, Authentifizierung und Protected Endpoints

**Kurs:** Moderne Webentwicklung mit FastAPI  
**Abschnitt:** Dependency Injection in FastAPI  
 

-

## 3. Schritt 2 – Authentication via Dependency (JWT)

Jetzt fügen wir eine **Auth-Schicht** hinzu. Ziel:

- Endpoint zum **Registrieren/Login** (vereinfachter Ansatz),
- ein **JWT-Token** erzeugen,
- ein Dependency, das aus dem Token den aktuellen Benutzer liest.

### Was ist ein JWT (JSON Web Token)?

Ein JWT ist ein kompakter, signierter String, mit dem ein Server Informationen über einen Benutzer (Claims) an den Client übergibt.  
Das Token besteht aus drei Teilen, jeweils Base64URL-kodiert und mit Punkten getrennt:

`HEADER.PAYLOAD.SIGNATURE`

Ein Beispiel-Header und -Payload:

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload (Claims)
{
  "sub": "alice",
  "exp": 1712510400,
  "scope": "user"
}
```

Ein reales JWT sieht dann z.B. so aus (stark gekürzt):  
`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTcxMjUxMDQwMH0.abc123...`

Der Server signiert Header und Payload mit einem geheimen Schlüssel.  
Clients können das Token lesen, aber aufgrund der Signatur nicht unbemerkt verändern.

---

### 3.1 User-Model

In `models.py`:

```python
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

DB neu erzeugen (falls nötig DB-Datei löschen oder Migration nutzen).

### 3.2 Security-Grundlagen

In `auth.py` (oder direkt in `main.py`):

```python
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models

SECRET_KEY = "CHANGE_ME_IN_REAL_PROJECT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

#### SECRET_KEY – Speicherung in der Praxis

In diesem Beispiel steht der `SECRET_KEY` hart im Code, damit das Konzept klar wird.  
In echten Projekten sollte dieser Schlüssel:

- als Umgebungsvariable (z.B. `export SECRET_KEY=...`) gesetzt,
- aus einer `.env`-Datei oder einem Secret-Manager (Docker Secrets, Vault, Cloud-Secret-Store) gelesen

und **niemals** im Git-Repository eingecheckt werden.  
Der Key ist die Grundlage für die Signatur der JWTs: Wer den Key kennt, kann gültige Tokens erzeugen.

#### ALGORITHM = "HS256" – was bedeutet das?

`HS256` steht für HMAC (Hash-based Message Authentication Code) mit SHA‑256.  

- „HS“ = HMAC mit Shared Secret (symmetrisch: derselbe Key zum Signieren und Verifizieren).
- „256“ = SHA‑256 Hashfunktion.

Der Server verwendet den `SECRET_KEY`, um aus Header und Payload eine Signatur zu berechnen.  
Beim Verifizieren berechnet er die Signatur erneut und vergleicht sie mit der Signatur im Token.  
Wenn jemand die Payload manipuliert, passt die Signatur nicht mehr und das Token wird abgelehnt.

#### ACCESS_TOKEN_EXPIRE_MINUTES

Mit `ACCESS_TOKEN_EXPIRE_MINUTES = 30` legst du fest, wie lange ein Access Token gültig ist.

- Beim Erzeugen des Tokens wird die Claim `exp` (Expiration Time) gesetzt.
- Nach Ablauf dieser Zeit ist das Token ungültig, und der Server wird beim Decoden eine Fehlermeldung liefern.

Das schützt z.B. besser bei gestohlenen Tokens: Ein geleaktes Token ist nur für einen begrenzten Zeitraum verwendbar.

#### Was ist OAuth2 grundsätzlich?

OAuth2 ist ein Standard, der beschreibt, wie ein Client sicher an ein Access Token kommt, das er dann für HTTP‑Requests an eine API nutzt.

Wichtige Rollen im OAuth2‑Modell:

- *Resource Owner*: der Benutzer, dem die Daten gehören
- *Client*: die Anwendung (z.B. SPA, Mobile App), die im Namen des Benutzers auf Ressourcen zugreifen will
- *Authorization Server*: der Dienst, der die Identität prüft und Tokens ausstellt
- *Resource Server*: die API, die die geschützten Ressourcen bereitstellt und das Token überprüft

Unser FastAPI‑Beispiel vereinigt Authorization Server und Resource Server in einer App:  
Wir implementieren `/token` (Tokenausgabe) und geschützte Endpoints in derselben Anwendung.

#### Was macht `OAuth2PasswordBearer(tokenUrl="token")`?

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

`OAuth2PasswordBearer` definiert ein Security-Schema für FastAPI:

- Es sagt FastAPI: „Diese API verwendet OAuth2 mit Password-Flow und erwartet ein Bearer Token im Authorization-Header.“
- Ein Bearer Token ist ein Zugriffstoken, bei dem allein der Besitz des Tokens ausreicht, um Zugriff zu bekommen – nach dem Motto: Wer das Token trägt (engl. „to bear“), darf zugreifen.
- `tokenUrl="token"` verweist auf den Endpoint, bei dem sich der Client das Token holt (`POST /token`).
- In den automatisch generierten Swagger-Docs (`/docs`) sorgt dieses Schema dafür, dass du einen „Authorize“-Button bekommst, der genau diesen Flow abbildet:
  1. Client sendet Benutzername/Passwort an `/token`,
  2. erhält ein Access Token,
  3. sendet dieses bei weiteren Requests als `Authorization: Bearer <token>`.

`oauth2_scheme` selbst ist ein Dependency, das bei Aufruf eines Endpoints den reinen Token-String aus dem Header extrahiert und weitergibt.

#### `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

`CryptContext` stammt aus `passlib` und kapselt die Logik zum Hashen und Verifizieren von Passwörtern.

- `schemes=["bcrypt"]` bedeutet, dass standardmäßig der Algorithmus *bcrypt* verwendet wird, ein bewährter Passwort-Hash-Algorithmus mit Salt und einstellbarem Work-Faktor.
- `deprecated="auto"` erlaubt es, alte Hash-Formate automatisch als „deprecated“ zu markieren, falls du später die Konfiguration änderst; so kannst du beim nächsten Login alte Hashes transparenter auf ein neues Format migrieren.

Du rufst dieses `pwd_context` später über `get_password_hash` und `verify_password` auf.

#### Was ist ein Passwort-Hash und wofür wird er verwendet?

Ein Passwort-Hash ist das Ergebnis eines Einweg-Algorithmus, der aus einem Klartext-Passwort einen String (den Hash) berechnet.

- Der Hash lässt sich praktisch nicht zurück in das ursprüngliche Passwort umrechnen.
- In der Datenbank speicherst du nur den Hash, nicht das Klartext-Passwort.

Beim Login wird das eingegebene Passwort mit demselben Algorithmus gehasht und mit dem gespeicherten Hash verglichen.  
Stimmen sie überein, gilt das Passwort als korrekt.

Hilfsfunktionen:

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### Wie funktioniert `create_access_token()`?

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

- `data` enthält Claims, die du in das Token packen willst, z.B. `{"sub": "alice"}` für den Benutzernamen.
- Die Funktion kopiert das Dictionary, berechnet ein Ablaufdatum `exp` (entweder über `expires_delta` oder den Default aus `ACCESS_TOKEN_EXPIRE_MINUTES`) und fügt dieses dem Payload hinzu.
- `jwt.encode(...)` baut daraus ein signiertes JWT mit dem angegebenen Algorithmus und deinem `SECRET_KEY`.

Das Ergebnis ist ein String, den du dem Client als Access Token zurückgibst.

---

### 3.3 User aus DB holen (Dependency + Hilfsfunktion)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()
```

#### `get_db()` als Dependency

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`get_db()` ist eine typische FastAPI-Dependency mit `yield`:

- Vor dem `yield` wird eine neue Datenbank-Session (`SessionLocal()`) erzeugt.
- FastAPI injiziert dieses `db`-Objekt in Endpoints, die `db: Session = Depends(get_db)` verwenden.
- Nach Abschluss des Requests läuft der Code im `finally`-Block und schließt die Session zuverlässig (Resource Cleanup).

So stellst du sicher, dass jede Anfrage ihre eigene, sauber aufgeräumte DB-Session hat.

#### `get_user_by_username`

```python
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()
```

Diese Hilfsfunktion kapselt die Datenbankabfrage für einen Benutzer.

- Sie nimmt eine `Session` und einen `username`.
- Sie fragt die `users`-Tabelle ab und gibt den ersten Treffer zurück oder `None`, falls es keinen gibt.

Das erleichtert das Wiederverwenden derselben Abfrage in verschiedenen Endpoints und Dependencies.

---

### 3.4 OAuth2-Login-Endpoint (`/token`)

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

Diesen Router in `main.py` registrieren:

```python
app.include_router(router)
```

#### `login_for_access_token` – Ablauf des Logins

```python
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ...
```

- `form_data: OAuth2PasswordRequestForm = Depends()` sagt FastAPI:  
  „Lies die Form-Parameter dieses Requests nach dem OAuth2-Password-Standard aus (`username`, `password`, optional `scope` usw.).“  
  FastAPI instanziiert `OAuth2PasswordRequestForm` automatisch aus dem Request-Body (`application/x-www-form-urlencoded`).
- `db: Session = Depends(get_db)` verwendet die oben definierte DB-Dependency.  
  Für jeden Request wird dadurch eine frische Datenbank-Session injiziert.

#### Was macht `Depends` genau?

`Depends()` ist der Mechanismus von FastAPI für Dependency Injection.

- Du definierst eine Funktion (z.B. `get_db`, `get_current_user`) und markierst Parameter in Endpoints so: `param_name: Typ = Depends(dependency_funktion)`.
- FastAPI erkennt, dass es vor dem Aufruf des Endpoints diese Dependency-Funktion aufrufen muss; deren Ergebnis wird dann als Argument in den Endpoint eingesetzt.
- Dependencies können ihrerseits andere Dependencies nutzen – FastAPI baut einen Graphen von Abhängigkeiten auf und löst ihn zur Laufzeit auf.

Dadurch kannst du z.B. Logging, Authentifizierung, DB-Sessions oder Konfiguration getrennt vom eigentlichen Business-Code kapseln.

#### Login-Logik im Detail

```python
user = get_user_by_username(db, form_data.username)
if not user or not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

access_token = create_access_token(data={"sub": user.username})
return {"access_token": access_token, "token_type": "bearer"}
```

- Zuerst wird der Benutzer anhand des Usernamens aus der Datenbank geladen.
- Falls kein User gefunden wird oder das Passwort nicht zum gespeicherten Hash passt, wird eine `401 Unauthorized` mit passendem `WWW-Authenticate`-Header zurückgegeben.
- Bei Erfolg wird ein Token mit der Claim `sub` (Subject) = Benutzername erzeugt und als JSON-Objekt zurückgegeben.

In Swagger kannst du dieses Token im „Authorize“-Dialog eintragen.

---

### 3.5 Dependency: aktueller Benutzer

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

Diese beiden Funktionen sind **Dependencies**, die ihr gleich in euren Endpoints verwenden könnt.

#### `get_current_user` – Token auslesen und Benutzer laden

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    ...
```

- `token: str = Depends(oauth2_scheme)` bedeutet: Verwende das zuvor definierte `OAuth2PasswordBearer`-Schema, um den Bearer-Token-String aus dem `Authorization`-Header zu extrahieren.  
  Praktisch wird hier also `Authorization: Bearer <token>` ausgelesen und `<token>` als String in den Parameter `token` gesetzt.
- `db: Session = Depends(get_db)` injiziert wieder eine Datenbank-Session.

Jeder Endpoint, der `current_user: User = Depends(get_current_user)` verwendet, bekommt auf diese Weise automatisch den aktuell authentifizierten Benutzer.

#### Warum wird `payload` decodiert?

```python
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
username: str | None = payload.get("sub")
```

- `jwt.decode(...)` überprüft die Signatur des Tokens mit deinem `SECRET_KEY` und dem angegebenen Algorithmus.  
  Wenn Signatur oder Ablaufzeit (`exp`) nicht stimmen, wirft die Funktion eine `JWTError`.
- Das Ergebnis ist das „Payload“-Dictionary des Tokens, in dem sich deine Claims befinden.
- Über `payload.get("sub")` holst du dir den Wert, den du beim Erzeugen des Tokens unter `"sub"` gespeichert hast – hier der Benutzername.

Das Decoden ist notwendig, um aus dem reinen String-Ticket wieder strukturierte Informationen zu machen und gleichzeitig sicherzustellen, dass es unverändert und gültig ist.

#### Fehlerbehandlung mit `credentials_exception`

```python
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
```

Diese Exception wird in allen Fehlerfällen (Token fehlt, ungültig, Benutzer existiert nicht mehr) verwendet.

- So verhält sich der Server konsistent gegenüber Clients: Bei allen Auth‑Fehlern gibt er dieselbe Art von 401‑Antwort und `WWW-Authenticate`‑Header zurück.
- Clients können dadurch standardisiert erkennen, dass das Token erneuert oder der User neu eingeloggt werden muss.

#### `get_current_active_user` – aktive Benutzer erzwingen

```python
async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

- Diese Dependency baut auf `get_current_user` auf: Erst wird der User per Token ermittelt.
- Dann wird geprüft, ob `is_active` gesetzt ist. Inaktive Benutzer werden mit einem passenden HTTP-Status (hier 400) abgewiesen.
- Alle Endpoints, die `current_user: User = Depends(get_current_active_user)` verwenden, sind damit automatisch sowohl authentifiziert als auch auf aktive Benutzer beschränkt.

---

## 4. Schritt 3 – Protected Endpoints

Jetzt machen wir bestimmte Produkt-Endpunkte „protected“, d.h. nur mit gültigem JWT-Token erreichbar.

Beispiel: Nur eingeloggte (aktive) User dürfen Produkte erstellen, updaten, löschen.

```python
from .auth import get_current_active_user

@app.post("/products", response_model=schemas.ProductRead, status_code=201)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    # current_user steht zur Verfügung, falls ihr z.B. Ownership speichern wollt
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
```

Analog könnt ihr `update_product` und `delete_product` schützen:

```python
@app.put("/products/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    ...

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    ...
```

**Wichtig:**

- In Swagger (`/docs`) könnt ihr jetzt bei geschützten Endpoints oben auf „Authorize“ klicken.
- Token bekommt ihr über `POST /token` (Form-Data: `username`, `password`).

---

## Zusammenfassung  – Assignment: Dependency Injection, SQLAlchemy, Auth & Protected Endpoints

###

Erweitert eure bestehende Product-API (mit Swagger und CRUD-Endpoints) um:

1. **SQLAlchemy + Dependency Injection**
   - Ersetzt die In-Memory-Liste durch eine SQLite-Datenbank.
   - Verwendet ein `Product`-SQLAlchemy-Model.
   - Nutzt `get_db()` als Dependency in allen Product-Endpoints.
2. **User-Management (Minimal)**
   - Erstellt ein `User`-Model (SQLAlchemy).
   - Implementiert ein Registration-Endpoint `POST /users/`:
     - Eingabe: `username`, `password`
     - Passwort wird gehasht gespeichert.
   - Optional: Endpoint `GET /users/me` (gibt aktuellen User zurück, protected).
3. **Authentication mit JWT**
   - Implementiert `POST /token` mit `OAuth2PasswordRequestForm`.
   - Wenn Username/Passwort korrekt sind:
     - JWT-Token erzeugen und zurückgeben.
   - Implementiert `get_current_user` und `get_current_active_user` als Dependencies.
4. **Protected Endpoints**
   - Schützt mindestens `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}`.
   - Nur eingeloggte (aktive) User dürfen diese Endpoints nutzen.
   - `GET /products` und `GET /products/{id}` bleiben öffentlich.
5. **Swagger-Dokumentation**
   - Stellt sicher, dass alle neuen Endpoints in `/docs` sichtbar sind.
   - Testet Login-Prozess und protected Endpoints direkt in Swagger über „Authorize“.


## Reflexionsfragen

Bereitet euch darauf vor, folgende Fragen kurz zu beantworten:

1. Welche Vorteile bietet Dependency Injection gegenüber „hart verdrahteten“ Objekten?

2. Warum ist es sinnvoll, DB-Sessions als Dependency bereitzustellen?

3. Wie funktioniert der Authentifizierungs-Flow von `POST /token` bis zum Aufruf eines geschützten Endpoints?

4. Wie trägt die Trennung zwischen Auth-Dependencies und Business-Logik zu besserer Wartbarkeit bei?
   