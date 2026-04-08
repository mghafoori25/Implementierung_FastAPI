from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .database import SessionLocal, engine
from . import models, schemas

app = FastAPI(
    title="Product API mit Dependency Injection",
    description="API für Produktverwaltung mit FastAPI, SQLAlchemy und SQLite",
    version="2.0.0"
)

# Tabellen anlegen
models.Base.metadata.create_all(bind=engine)


# ---------- Dependency ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Endpoints ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/products", response_model=schemas.ProductRead, status_code=201)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Erstellt ein neues Produkt.
    """
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[schemas.ProductRead])
def read_products(db: Session = Depends(get_db)):
    """
    Gibt alle Produkte zurück.
    """
    products = db.execute(select(models.Product)).scalars().all()
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Gibt ein einzelnes Produkt zurück.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=schemas.ProductRead)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Aktualisiert ein bestehendes Produkt.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Löscht ein Produkt.
    """
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None