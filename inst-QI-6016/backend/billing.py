import sqlite3
import os
from fastapi.concurrency import run_in_threadpool
from database import get_db

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from auth_utils import get_current_user, User
from database import get_db_connection
from payment_gateway import get_payment_gateway
from pathlib import Path

router = APIRouter()

class Product(BaseModel):
    id: int
    name: str
    product_type: str
    audience_type: str
    price_cents: int
    currency_code: str
    questions_quota: int
    duration_days: Optional[int] = None
    is_active: bool
    tenant_id: Optional[int] = None
    total_sold: int = 0

class Balance(BaseModel):
    audience_type: str
    balance: int
    generated_count: int = 0
    total_bought: int = 0

class PurchaseRequest(BaseModel):
    product_id: int

async def get_user_question_balance(user_id: int, audience_type: str) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        sql_query = "SELECT balance FROM billing_user_question_balances WHERE user_id = ? AND audience_type = ?"
        print(f"DEBUG: get_user_question_balance SQL Query: {sql_query}")
        print(f"DEBUG: get_user_question_balance Parameters: {(user_id, audience_type)}")
        cursor.execute(
            sql_query,
            (user_id, audience_type)
        )
        balance_row = cursor.fetchone()
        balance = balance_row["balance"] if balance_row else 0
        print(f"DEBUG: get_user_question_balance fetched balance: {balance}")
        return balance
    finally:
        conn.close()

async def deduct_from_balance(user_id: int, amount: int, tenant_id: int, event_type: str, audience_type: str, model_api_name: Optional[str] = None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Ensure user balance row exists (initialize to 0 if not present)
        print(f"DEBUG: Ensuring user balance row exists for user_id={user_id}, audience_type={audience_type}")
        cursor.execute(
            """INSERT OR IGNORE INTO billing_user_question_balances (user_id, audience_type, balance)
            VALUES (?, ?, 0)""",
            (user_id, audience_type)
        )
        # Deduct from user balance
        print(f"DEBUG: Deducting from user balance. SQL: UPDATE billing_user_question_balances SET balance = balance - ? WHERE user_id = ? AND audience_type = ? Parameters: {(amount, user_id, audience_type)}")
        cursor.execute(
            "UPDATE billing_user_question_balances SET balance = balance - ? WHERE user_id = ? AND audience_type = ?",
            (amount, user_id, audience_type)
        )
        print(f"DEBUG: User balance update rows affected: {cursor.rowcount}")

        # Ensure tenant balance row exists (initialize to 0 if not present)
        print(f"DEBUG: Ensuring tenant balance row exists for tenant_id={tenant_id}, audience_type={audience_type}")
        cursor.execute(
            """INSERT OR IGNORE INTO billing_tenant_question_balances (tenant_id, audience_type, balance)
            VALUES (?, ?, 0)""",
            (tenant_id, audience_type)
        )
        # Deduct from tenant balance
        print(f"DEBUG: Deducting from tenant balance. SQL: UPDATE billing_tenant_question_balances SET balance = balance - ? WHERE tenant_id = ? AND audience_type = ? Parameters: {(amount, tenant_id, audience_type)}")
        cursor.execute(
            "UPDATE billing_tenant_question_balances SET balance = balance - ? WHERE tenant_id = ? AND audience_type = ?",
            (amount, tenant_id, audience_type)
        )
        print(f"DEBUG: Tenant balance update rows affected: {cursor.rowcount}")

        # Record billing event
        print(f"DEBUG: Recording billing event. SQL: INSERT INTO billing_events (...) VALUES (...) Parameters: {(tenant_id, user_id, event_type, amount, 0, 'USD', audience_type, model_api_name)}")
        cursor.execute(
            """
            INSERT INTO billing_events (tenant_id, user_id, event_type, questions_debited, total_price_cents, currency, audience_type, model)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, event_type, amount, 0, 'USD', audience_type, model_api_name)
        )
        print(f"DEBUG: Billing event insert rows affected: {cursor.rowcount}")
        conn.commit()
        print("DEBUG: Transaction committed in deduct_from_balance.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@router.get("/balances", response_model=List[Balance])
async def get_tenant_balances(current_user: User = Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT audience_type, balance FROM billing_tenant_question_balances WHERE tenant_id = ?", (tenant_id,))
        balances_raw = cursor.fetchall()
        
        balances_with_generated = []
        for row in balances_raw:
            balance_dict = dict(row)
            audience_type = balance_dict["audience_type"]
            
            # Get total bought count for this audience type
            sql_query_total_bought = "SELECT SUM(be.questions_credited) FROM billing_events be WHERE be.tenant_id = ? AND be.event_type = 'credit' AND be.audience_type = ?"
            print(f"DEBUG: Executing total_bought SQL query: {sql_query_total_bought} with params: {(tenant_id, audience_type)}")
            cursor.execute(
                sql_query_total_bought,
                (tenant_id, audience_type)
            )
            total_bought = cursor.fetchone()[0] or 0
            print(f"DEBUG: Calculated total_bought for {audience_type}: {total_bought}")
            balance_dict["total_bought"] = total_bought

            # Get generated count for this audience type
            sql_query_generated = "SELECT SUM(be.questions_debited) FROM billing_events be WHERE be.tenant_id = ? AND be.event_type = 'debit' AND be.audience_type = ?"
            print(f"DEBUG: Executing generated_count SQL query: {sql_query_generated} with params: {(tenant_id, audience_type)}")
            cursor.execute(
                sql_query_generated,
                (tenant_id, audience_type)
            )
            generated_count = cursor.fetchone()[0] or 0
            print(f"DEBUG: Calculated generated_count for {audience_type}: {generated_count}")
            balance_dict["generated_count"] = generated_count
            balances_with_generated.append(balance_dict)
            
        return balances_with_generated
    finally:
        conn.close()

@router.get("/products", response_model=List[Product])
async def get_available_products(current_user: User = Depends(get_current_user)):
    try:
        tenant_id = current_user.get("tenant_id")
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            sql_query = "SELECT * FROM billing_products WHERE is_active = 1 AND (tenant_id IS NULL OR tenant_id = ?)"
            cursor.execute(sql_query, (tenant_id,))
            products = cursor.fetchall()
            processed_products = []
            for row in products:
                product_dict = {
                    "id": row["id"],
                    "name": row["name"],
                    "product_type": row["product_type"],
                    "audience_type": row["audience_type"],
                    "price_cents": row["price_cents"],
                    "currency_code": row["currency_code"],
                    "questions_quota": row["questions_quota"],
                    "duration_days": row["duration_days"],
                    "is_active": bool(row["is_active"]),
                    "tenant_id": row["tenant_id"]
                }
                processed_products.append(product_dict)
            from fastapi.encoders import jsonable_encoder
            return jsonable_encoder(processed_products)
        finally:
            conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/purchase", status_code=status.HTTP_200_OK)
async def purchase_product(purchase: PurchaseRequest, request: Request, current_user: User = Depends(get_current_user)):
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("id")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get product details
        cursor.execute("SELECT * FROM billing_products WHERE id = ? AND is_active = 1", (purchase.product_id,))
        product = cursor.fetchone()
        print(f"DEBUG: Product details from DB: {product}")
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not active")

        # Initiate payment with the payment gateway
        payment_gateway = get_payment_gateway()
        
        # Dynamically determine backend_public_url from the request
        backend_public_url = str(request.base_url).rstrip('/')
        print(f"DEBUG: backend_public_url determined from request: {backend_public_url}")

        payment_intent_details = payment_gateway.create_payment_intent(
            amount_cents=product['price_cents'],
            currency_code=product['currency_code'],
            description=f"Purchase of {product['name']} for tenant {tenant_id}",
            metadata={
                "product_id": product['id'],
                "tenant_id": tenant_id,
                "user_id": user_id,
                "questions_quota": product['questions_quota'],
                "audience_type": product['audience_type'],
                "amount_cents": product['price_cents'],
                "currency_code": product['currency_code'],
            },
            return_url=f"{backend_public_url}/billing/purchase_success"
        )
        
        # Return payment intent details to the frontend
        return {"message": "Payment initiated", "payment_intent": payment_intent_details}

    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during payment initiation: {e}")
    finally:
        conn.close()

@router.get("/purchase_success")
async def purchase_success():
    # This is a placeholder endpoint for the frontend to redirect to after payment.
    # The actual balance update will happen via webhook.
    return {"message": "Payment process completed. Awaiting final confirmation."}

# Synchronous helper function to run in threadpool
def _process_payment_webhook_sync(
    payload: Dict[str, Any],
    product_id: int,
    tenant_id: int,
    user_id: int,
    questions_quota: int,
    audience_type: str,
    total_price_cents: int,
    currency: str
):
    conn = get_db_connection() # Open connection in this thread
    try:
        cursor = conn.cursor()

        # --- Before Update ---
        cursor.execute("SELECT balance FROM billing_user_question_balances WHERE user_id = ? AND audience_type = ?", (user_id, audience_type))
        old_user_balance_row = cursor.fetchone()
        old_user_balance = old_user_balance_row["balance"] if old_user_balance_row else 0
        print(f"DEBUG: Webhook - User balance BEFORE update for {user_id}/{audience_type}: {old_user_balance}")

        cursor.execute("SELECT balance FROM billing_tenant_question_balances WHERE tenant_id = ? AND audience_type = ?", (tenant_id, audience_type))
        old_tenant_balance_row = cursor.fetchone()
        old_tenant_balance = old_tenant_balance_row["balance"] if old_tenant_balance_row else 0
        print(f"DEBUG: Webhook - Tenant balance BEFORE update for {tenant_id}/{audience_type}: {old_tenant_balance}")

        # Update user balance
        cursor.execute(
            """
            INSERT INTO billing_user_question_balances (user_id, audience_type, balance)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, audience_type) DO UPDATE SET
            balance = balance + excluded.balance;
            """, (user_id, audience_type, questions_quota)
        )
        print(f"DEBUG: Webhook - User balance UPSERT executed for {user_id}/{audience_type} with quota {questions_quota}")


        # Update tenant balance
        cursor.execute(
            """
            INSERT INTO billing_tenant_question_balances (tenant_id, audience_type, balance)
            VALUES (?, ?, ?)
            ON CONFLICT(tenant_id, audience_type) DO UPDATE SET
            balance = balance + excluded.balance;
            """, (tenant_id, audience_type, questions_quota)
        )
        print(f"DEBUG: Webhook - Tenant balance UPSERT executed for {tenant_id}/{audience_type} with quota {questions_quota}")

        # Record billing event
        cursor.execute(
            """
            INSERT INTO billing_events (tenant_id, user_id, event_type, product_id, questions_debited, questions_credited, total_price_cents, currency, audience_type)
            VALUES (?, ?, 'credit', ?, 0, ?, ?, ?, ?)
            """, (tenant_id, user_id, product_id, questions_quota, total_price_cents, currency, audience_type)
        )
        print(f"DEBUG: Webhook - Billing event INSERT executed with values: tenant_id={tenant_id}, user_id={user_id}, product_id={product_id}, questions_credited={questions_quota}, total_price_cents={total_price_cents}, currency={currency}")
        
        conn.commit()
        print("DEBUG: Webhook - Transaction committed.")

        # --- After Update ---
        cursor.execute("SELECT balance FROM billing_user_question_balances WHERE user_id = ? AND audience_type = ?", (user_id, audience_type))
        new_user_balance_row = cursor.fetchone()
        new_user_balance = new_user_balance_row["balance"] if new_user_balance_row else 0
        print(f"DEBUG: Webhook - User balance AFTER update for {user_id}/{audience_type}: {new_user_balance}")

        cursor.execute("SELECT balance FROM billing_tenant_question_balances WHERE tenant_id = ? AND audience_type = ?", (tenant_id, audience_type))
        new_tenant_balance_row = cursor.fetchone()
        new_tenant_balance = new_tenant_balance_row["balance"] if new_tenant_balance_row else 0
        print(f"DEBUG: Webhook - Tenant balance AFTER update for {tenant_id}/{audience_type}: {new_tenant_balance}")

    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        print(f"ERROR: Webhook processing error: {e}") # Log error for server
        raise e
    finally:
        conn.close()

@router.post("/webhook")
async def payment_webhook(request: Request, db: sqlite3.Connection = Depends(get_db), payload_from_trigger: Optional[dict] = None):
    print("DEBUG: payment_webhook entered.")
    if payload_from_trigger is None:
        payload = await request.json()
    else:
        payload = payload_from_trigger
    if payload_from_trigger is None: # Only get signature if it's a real webhook
        signature = request.headers.get("stripe-signature") # Assuming Stripe for now
    else:
        signature = "dummy_signature" # Dummy signature for internal calls
    print(f"DEBUG: Webhook received payload: {payload}")

    payment_gateway = get_payment_gateway()
    try:
        event = payment_gateway.handle_webhook(payload, signature)
        print(f"DEBUG: Webhook processed event: {event}")
    except ValueError as e:
        print(f"ERROR: Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Process the event
    if event['type'] == "payment_intent.succeeded":
        payment_intent = event['data']['object']
        metadata = payment_intent['metadata']

        product_id = int(metadata['product_id']) # Ensure int
        tenant_id = int(metadata['tenant_id'])   # Ensure int
        user_id = int(metadata['user_id'])       # Ensure int
        questions_quota = int(metadata['questions_quota']) # Ensure int
        audience_type = metadata['audience_type']
        
        # Get amount and currency directly from payment_intent, which are standard fields
        total_price_cents = payment_intent.get('amount') # Amount is in cents
        currency = payment_intent.get('currency') # Currency code (e.g., 'usd')

        # Ensure these are not None and are of correct type
        if total_price_cents is None:
            raise ValueError("Payment intent 'amount' is missing.")
        if not isinstance(total_price_cents, int):
            raise TypeError("Payment intent 'amount' must be an integer.")
        if currency is None:
            raise ValueError("Payment intent 'currency' is missing.")
        if not isinstance(currency, str):
            raise TypeError("Payment intent 'currency' must be a string.")

        print(f"DEBUG: Webhook - Extracted metadata: product_id={product_id}, tenant_id={tenant_id}, user_id={user_id}, questions_quota={questions_quota}, audience_type={audience_type}, total_price_cents={total_price_cents}, currency={currency}")

        # Call the synchronous helper function in the thread pool
        await run_in_threadpool(
            _process_payment_webhook_sync,
            payload, # Pass the full payload for debug consistency if needed
            product_id,
            tenant_id,
            user_id,
            questions_quota,
            audience_type,
            total_price_cents,
            currency
        )

    return {"status": "success"}

@router.get("/dummy_webhook_trigger")
async def dummy_webhook_trigger(
    payment_intent_id: str,
    status: str,
    product_id: int,
    tenant_id: int,
    user_id: int,
    questions_quota: int,
    audience_type: str,
    amount_cents: int,
    currency_code: str,
    db: sqlite3.Connection = Depends(get_db)
):
    print(f"DEBUG: dummy_webhook_trigger received: payment_intent_id={payment_intent_id}, status={status}, product_id={product_id}, tenant_id={tenant_id}, user_id={user_id}, questions_quota={questions_quota}, audience_type={audience_type}, amount_cents={amount_cents}, currency_code={currency_code}")

    if status == "succeeded":
        # Manually construct a payload similar to what a real webhook would send
        # and call the payment_webhook function internally.
        payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "payment_intent_id": payment_intent_id,
                    "amount": amount_cents, # Direct amount from payment intent
                    "currency": currency_code, # Direct currency from payment intent
                    "metadata": {
                        "product_id": product_id,
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "questions_quota": questions_quota,
                        "audience_type": audience_type,
                        # No need to duplicate amount_cents and currency_code in metadata here
                    }
                }
            }
        }
        # Call the actual webhook processing logic
        # Note: We're passing a dummy Request object here, as payment_webhook expects it.
        # The actual payload is what matters for processing.
        await payment_webhook(Request(scope={'type': 'http'}), db=db, payload_from_trigger=payload)
        return {"message": "Dummy webhook triggered successfully."}
    else:
        return {"message": f"Dummy webhook not triggered due to status: {status}"}
