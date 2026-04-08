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


@app.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """
    Erstellt ein neues Produkt.

    - **name**: Produktname (required)
    - **description**: Produktbeschreibung (optional)
    - **price**: Preis in Euro (required, > 0)
    - **category**: Kategorie (required)
    """
    product_dict = product.dict()
    now = datetime.now()

    product_dict["id"] = len(products_db) + 1
    product_dict["created_at"] = now
    product_dict["updated_at"] = now

    products_db.append(product_dict)
    return product_dict


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
    filtered_products = products_db

    if category is not None:
        filtered_products = [p for p in products_db if p["category"] == category]

    return filtered_products[skip:skip + limit]


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    Gibt ein spezifisches Produkt zurück.
    """
    product = next((p for p in products_db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate):
    """
    Aktualisiert ein bestehendes Produkt.
    """
    product = next((p for p in products_db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    update_data = product_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        product[key] = value

    product["updated_at"] = datetime.now()

    return product


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """
    Löscht ein Produkt.
    """
    product = next((p for p in products_db if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    products_db.remove(product)
    return None