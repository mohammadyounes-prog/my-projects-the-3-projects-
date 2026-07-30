from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from auth_utils import get_current_admin_user, User
from database import get_db_connection

router = APIRouter()

class CurrencyIn(BaseModel):
    code: str
    name: str
    decimal_places: int = 2
    is_active: bool = True

class BundleIn(BaseModel):
    name: str
    currency: str
    price_cents: int
    credits_amount: int
    description: Optional[str] = None
    is_active: bool = True

# --- New Model for Billing Products ---
class ProductIn(BaseModel):
    product_type: str
    audience_type: str
    name: str
    description: Optional[str] = None
    price_cents: int
    currency_code: str
    questions_quota: int
    duration_days: Optional[int] = None
    is_active: bool = True

@router.get("/currencies")
def list_currencies(current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT code, name, decimal_places, is_active FROM currencies ORDER BY code")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

@router.post("/currencies", status_code=status.HTTP_201_CREATED)
def create_currency(payload: CurrencyIn, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO currencies (code, name, decimal_places, is_active) VALUES (?, ?, ?, ?)",
            (payload.code, payload.name, payload.decimal_places, 1 if payload.is_active else 0)
        )
        conn.commit()
        return {"code": payload.code}
    finally:
        conn.close()

@router.put("/currencies/{code}")
def update_currency(code: str, payload: CurrencyIn, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE currencies SET name = ?, decimal_places = ?, is_active = ? WHERE code = ?",
            (payload.name, payload.decimal_places, 1 if payload.is_active else 0, code)
        )
        conn.commit()
        return {"code": code}
    finally:
        conn.close()

@router.delete("/currencies/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency(code: str, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM currencies WHERE code = ?", (code,))
        conn.commit()
        return
    finally:
        conn.close()

# --- CRUD for billing_products ---

@router.get("/products/{product_id}")
def get_single_product(product_id: int, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_super_admin = current_user.get("is_super_admin", 0)
        tenant_id_filter = None
        if not is_super_admin:
            tenant_id_filter = current_user.get("tenant_id")

        if tenant_id_filter is None:
            cur.execute("SELECT * FROM billing_products WHERE id = ?", (product_id,))
        else:
            cur.execute("SELECT * FROM billing_products WHERE id = ? AND tenant_id = ?", (product_id, tenant_id_filter))
        product = cur.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(product)
    finally:
        conn.close()

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductIn, current_user: User = Depends(get_current_admin_user)):
    print(f"DEBUG: create_product received payload: {payload}")
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO billing_products (product_type, audience_type, name, description, price_cents, currency_code, questions_quota, duration_days, is_active, tenant_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (payload.product_type, payload.audience_type, payload.name, payload.description, payload.price_cents, payload.currency_code, payload.questions_quota, payload.duration_days, 1 if payload.is_active else 0, current_user.get("tenant_id") if not current_user.get("is_super_admin", 0) else None)
        )
        conn.commit()
        return {"id": cur.lastrowid}
    finally:
        conn.close()

@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductIn, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_super_admin = current_user.get("is_super_admin", 0)
        tenant_id_filter = None
        if not is_super_admin:
            tenant_id_filter = current_user.get("tenant_id")

        if tenant_id_filter is None:
            cur.execute(
                "UPDATE billing_products SET product_type=?, audience_type=?, name=?, description=?, price_cents=?, currency_code=?, questions_quota=?, duration_days=?, is_active=? WHERE id = ?",
                (payload.product_type, payload.audience_type, payload.name, payload.description, payload.price_cents, payload.currency_code, payload.questions_quota, payload.duration_days, 1 if payload.is_active else 0, product_id)
            )
        else:
            cur.execute(
                "UPDATE billing_products SET product_type=?, audience_type=?, name=?, description=?, price_cents=?, currency_code=?, questions_quota=?, duration_days=?, is_active=? WHERE id = ? AND tenant_id = ?",
                (payload.product_type, payload.audience_type, payload.name, payload.description, payload.price_cents, payload.currency_code, payload.questions_quota, payload.duration_days, 1 if payload.is_active else 0, product_id, tenant_id_filter)
            )
        conn.commit()
        return {"id": product_id}
    finally:
        conn.close()

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        print(f"Attempting to delete product with ID: {product_id}")

        # First, delete associated billing events
        cur.execute("DELETE FROM billing_events WHERE product_id = ?", (product_id,))
        print(f"Deleted {cur.rowcount} billing events for product ID: {product_id}")

        # Then, delete the product
        cur.execute("DELETE FROM billing_products WHERE id = ?", (product_id,))
        print(f"Deleted {cur.rowcount} product with ID: {product_id}")

        conn.commit()
        print(f"Committed deletion for product ID: {product_id}")
        return
    except Exception as e:
        conn.rollback()
        print(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting product: {e}")
    finally:
        conn.close()
