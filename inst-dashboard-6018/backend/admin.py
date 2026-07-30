from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
import re
from pydantic import BaseModel, RootModel
from billing import Product
from database import get_audience_fields, update_audience_fields, get_all_users, get_user_by_id, create_user, update_user, delete_user, get_lookup_data_list, add_lookup_data, update_lookup_data, delete_lookup_data, get_user, update_user_password, get_property_types_by_audience, create_property_type, get_property_type_by_api_name, delete_property_type, get_all_tenants, create_tenant, update_tenant, delete_tenant, get_db_connection, get_all_models, get_model_by_name, create_model, update_model, delete_model, create_generation_model, get_all_generation_models, get_generation_model_by_id, update_generation_model, delete_generation_model, get_tenant_by_id, get_tenant_hierarchy, get_all_billing_products, get_all_billing_events
from auth_utils import get_current_admin_user, User, get_current_user, get_password_hash
from openai_api import call_openai_chat
import os

router = APIRouter()

class TenantOut(BaseModel):
    id: int
    name: str
    created_at: str
    country: Optional[str] = None
    created_by_username: Optional[str] = None

class TenantCreate(BaseModel):
    name: str
    country: str
    admin_username: str
    admin_password: str
    admin_mobile_phone: Optional[str] = None
    admin_email: Optional[str] = None # Added email field for admin user

class TenantUpdate(BaseModel):
    name: str
    country: Optional[str] = None
    new_password: Optional[str] = None
    user_id_to_update: Optional[int] = None
    admin_mobile_phone: Optional[str] = None

class GenerationModel(BaseModel):
    id: int
    model_name: str
    model_api_name: str
    api_key: Optional[str] = None

class GenerationModelIn(BaseModel):
    model_name: str
    model_api_name: str
    generation_method: str
    is_default: bool = False
    is_active: bool = True
    api_key: Optional[str] = None
    tenant_id: Optional[int] = None

class PasswordVerifyRequest(BaseModel):
    password: str

@router.post("/verify-password")
async def verify_admin_password(request: PasswordVerifyRequest, current_user: User = Depends(get_current_admin_user)):
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user session")

    # We need to fetch the user from DB to get the password hash
    # The user object from the token doesn't contain it.
    db_user = get_user_by_id(user_id, tenant_id=current_user.get("tenant_id"))
    if not db_user or "password" not in db_user:
        raise HTTPException(status_code=404, detail="User not found or password hash is missing")

    if verify_password(request.password, db_user["password"]):
        return {"verified": True}
    else:
        return {"verified": False}

class TenantIdsRequest(BaseModel):
    tenant_ids: List[int]

@router.delete("/tenants/batch", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_tenants_endpoint(payload: TenantIdsRequest, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    is_admin = current_user.get("is_admin", 0)
    if not (is_super_admin == 1 or is_admin == 1):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete tenants")
    
    # Optional: Add more robust checks here to ensure tenants being deleted belong to the admin's scope
    # For now, delete_multiple_tenants in database.py will handle the tenant filtering if implemented.
    delete_multiple_tenants(payload.tenant_ids)
    return

@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_tenant(tenant_id: int, payload: PasswordVerifyRequest, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    is_admin = current_user.get("is_admin", 0)
    if not (is_super_admin == 1 or is_admin == 1):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tenant")

    # Verify password
    user_from_db = get_user_by_id(current_user["id"])
    if not user_from_db or not verify_password(payload.password, user_from_db["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    delete_tenant(tenant_id)
    return

@router.put("/tenants/{tenant_id}", response_model=TenantOut)
async def update_single_tenant(tenant_id: int, tenant: TenantUpdate, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    is_admin = current_user.get("is_admin", 0)
    if not (is_super_admin == 1 or is_admin == 1):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this tenant")
    
    try:
        # Update tenant name
        update_tenant(tenant_id, tenant.name)

        # Update user details if user_id_to_update is provided
        if tenant.user_id_to_update:
            user_to_update = get_user_by_id(tenant.user_id_to_update)
            if not user_to_update or user_to_update['tenant_id'] != tenant_id:
                 raise HTTPException(status_code=403, detail="User does not belong to this tenant.")

            # Update password if provided
            if tenant.new_password:
                hashed_password = get_password_hash(tenant.new_password)
                update_user_password(tenant.user_id_to_update, hashed_password)
            
            # Update mobile phone if provided
            if tenant.admin_mobile_phone is not None:
                update_user(user_id=tenant.user_id_to_update, mobile_phone=tenant.admin_mobile_phone)

        # Update country association
        if tenant.country:
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM tenant_countries WHERE tenant_id = ?", (tenant_id,))
                cur.execute("SELECT country_id FROM countries WHERE name = ?", (tenant.country,))
                country_row = cur.fetchone()
                if not country_row:
                    raise HTTPException(status_code=400, detail="Country not found")
                country_id = country_row["country_id"]
                cur.execute("INSERT INTO tenant_countries (tenant_id, country_id) VALUES (?, ?)", (tenant_id, country_id))
                conn.commit()
            finally:
                conn.close()

        updated_tenant = get_tenant_by_id(tenant_id)
        if not updated_tenant:
            raise HTTPException(status_code=404, detail="Tenant not found after update")
        return updated_tenant
    except Exception as e:
        # Log the exception for debugging
        print(f"Error updating tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tenants", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
async def create_new_tenant(tenant: TenantCreate, current_user: User = Depends(get_current_admin_user)):
    print(f"DEBUG: create_new_tenant called with tenant: {tenant.dict()}, current_user: {current_user}")
    
    if len(tenant.admin_username) < 6:
        raise HTTPException(status_code=400, detail="Admin username must be at least 6 characters")

    is_super_admin = current_user.get("is_super_admin", 0)

    parent_id = None
    if not is_super_admin:
        parent_id = current_user.get("tenant_id")
    
    creator_id = current_user.get("id")
    print(f"DEBUG: is_super_admin: {is_super_admin}, parent_id: {parent_id}, creator_id: {creator_id}")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Create Tenant
        new_tenant_id = create_tenant(tenant.name, parent_id=parent_id, created_by=creator_id, conn=conn, cursor=cur)
        
        # Associate Country
        cur.execute("SELECT country_id FROM countries WHERE name = ?", (tenant.country,))
        country_row = cur.fetchone()
        if not country_row:
            raise HTTPException(status_code=400, detail="Country not found")
        country_id = country_row["country_id"]
        cur.execute("INSERT INTO tenant_countries (tenant_id, country_id) VALUES (?, ?)", (new_tenant_id, country_id))

        # Create Admin User for the new Tenant
        existing_user = get_user(tenant.admin_username, tenant_id=new_tenant_id)
        if existing_user:
            raise HTTPException(status_code=409, detail="Admin username already exists for this tenant.")
        
        hashed_password = get_password_hash(tenant.admin_password)
        create_user(
            username=tenant.admin_username,
            hashed_password=hashed_password,
            is_admin=1,
            full_name=tenant.admin_username, # Or a new field if you add it
            tenant_id=new_tenant_id,
            mobile_phone=tenant.admin_mobile_phone,
            email=tenant.admin_email,
            conn=conn,
            cursor=cur
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create tenant or admin user: {e}")
    finally:
        conn.close()

    new_tenant_data = get_tenant_by_id(new_tenant_id)
    if not new_tenant_data:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created tenant.")

    return new_tenant_data

# Countries per-tenant management
class TenantCountriesUpdate(BaseModel):
    country_ids: List[str]

@router.get("/tenants/{tenant_id}/countries")
async def get_tenant_countries(tenant_id: int, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT c.country_id, c.name FROM tenant_countries tc JOIN countries c ON c.country_id = tc.country_id WHERE tc.tenant_id = ? ORDER BY c.name",
            (tenant_id,)
        ).fetchall()
        return [{"country_id": r["country_id"], "name": r["name"]} for r in rows]
    finally:
        conn.close()

@router.put("/tenants/{tenant_id}/countries")
async def set_tenant_countries(tenant_id: int, payload: TenantCountriesUpdate, current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        conn.execute("BEGIN")
        conn.execute("DELETE FROM tenant_countries WHERE tenant_id = ?", (tenant_id,))
        for cid in payload.country_ids:
            conn.execute("INSERT OR IGNORE INTO tenant_countries(tenant_id, country_id) VALUES (?, ?)", (tenant_id, cid))
        conn.commit()
        return {"status": "ok", "count": len(payload.country_ids)}
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to update tenant countries: {e}")
    finally:
        conn.close()

class PaginatedTenantsResponse(BaseModel):
    total_count: int
    tenants: List[TenantOut]

@router.get("/tenants", response_model=PaginatedTenantsResponse)
async def read_tenants(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin_user)
):
    is_super_admin = current_user.get("is_super_admin", 0)
    
    if is_super_admin:
        # Super admin gets all tenants
        total_tenants, tenants = get_all_tenants(skip=skip, limit=limit)
    else:
        # Tenant admin gets their own tenant and its descendants (pagination not yet implemented for hierarchy)
        # For now, return all hierarchy tenants, and frontend will handle pagination if needed
        user_tenant_id = current_user.get("tenant_id")
        tenants_list = get_tenant_hierarchy(user_tenant_id)
        total_tenants = len(tenants_list)
        tenants = tenants_list[skip:skip + limit] # Basic slicing for hierarchy
    
    return {"total_count": total_tenants, "tenants": tenants}

@router.get("/tenants/{tenant_id}", response_model=TenantOut)
async def get_single_tenant(tenant_id: int, current_user: User = Depends(get_current_admin_user)):
    tenant = get_tenant_by_id(tenant_id)
    print(f"DEBUG: get_single_tenant returning: {tenant}")
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.post("/test_openai")
async def test_openai(current_user: User = Depends(get_current_admin_user)):
    # Admin-only quick health check for OpenAI connectivity
    try:
        resp = call_openai_chat("Return exactly: OK")
        return {"status": "ok", "response": resp}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/recreate_superuser")
async def recreate_superuser(current_user: User = Depends(get_current_admin_user)):
    if current_user.get("is_super_admin", 0) != 1 and current_user.get("is_admin", 0) != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    # Find existing superuser in tenant 1
    existing = get_user('superuser', tenant_id=1)
    if existing:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id = ?", (existing["id"],))
            conn.commit()
            conn.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete existing superuser: {e}")

    try:
        # create_user in this codebase expects username + hashed_password OR username+password depending on implementation
        # Use admin create endpoint conventions: supply plaintext and call create_user accordingly
        new_id = create_user(username='superuser', password='test', is_admin=1, full_name='superuser', tenant_id=1, is_super_admin=1)
        return {"status": "ok", "user_id": new_id}
    except TypeError:
        # Fallback: compute hash via get_password_hash path inside admin routes
        from auth_utils import get_password_hash
        hashed = get_password_hash('test')
        new_id = create_user(username='superuser', hashed_password=hashed, is_admin=1, full_name='superuser', tenant_id=1)
        return {"status": "ok", "user_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create superuser: {e}")

# Models management endpoints (admin only)

@router.get("/models")
async def admin_list_models(current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")
    models = get_all_generation_models(tenant_id=tenant_id_filter)
    return models

@router.get("/models/{model_id}")
async def admin_get_model(model_id: int, current_user: User = Depends(get_current_admin_user)):
    # For now, fetch across all tenants. A tenant_id could be added for scoping.
    model = get_generation_model_by_id(model_id, tenant_id=None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.post("/models")
async def admin_create_model(payload: GenerationModelIn, current_user: User = Depends(get_current_admin_user)):
    new_id = create_generation_model(
        model_name=payload.model_name,
        model_api_name=payload.model_api_name,
        generation_method=payload.generation_method,
        is_default=1 if payload.is_default else 0,
        is_active=1 if payload.is_active else 0,
        api_key=payload.api_key,
        tenant_id=payload.tenant_id,
    )
    model = get_generation_model_by_id(new_id, tenant_id=payload.tenant_id or None)
    return model

@router.put("/models/{model_id}")
async def admin_update_model(model_id: int, payload: GenerationModelIn, current_user: User = Depends(get_current_admin_user)):
    update_generation_model(
        model_id=model_id,
        tenant_id=payload.tenant_id if payload.tenant_id is not None else None,
        model_name=payload.model_name,
        model_api_name=payload.model_api_name,
        generation_method=payload.generation_method,
        is_default=1 if payload.is_default else 0,
        is_active=1 if payload.is_active else 0,
        api_key=payload.api_key or "",
    )
    model = get_generation_model_by_id(model_id, tenant_id=payload.tenant_id or None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found after update")
    return model

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_model(model_id: int, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")
    
    db_model = get_generation_model_by_id(model_id, tenant_id=tenant_id_filter)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    delete_generation_model(model_id, tenant_id=tenant_id_filter)
    return

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    full_name: Optional[str] = None
    tenant_id: Optional[int] = None # Make tenant_id optional as it will be derived from country
    mobile_phone: Optional[str] = None
    email: Optional[str] = None # Added email field
    audience_type: Optional[str] = None
    country: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None # For password reset by admin
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    full_name: Optional[str] = None
    tenant_id: Optional[int] = None
    agent_name: Optional[str] = None
    country_name: Optional[str] = None
    role: Optional[str] = None
    audience_type: Optional[str] = None

class PaginatedUsersResponse(BaseModel):
    total_users: int
    users: List[UserOut]

class BillingEventOut(BaseModel):
    id: int
    product_name: Optional[str] = None
    agent_name: Optional[str] = None
    country: Optional[str] = None
    username: Optional[str] = None
    created_at: str
    total_price_cents: Optional[int] = None
    currency: Optional[str] = None

class PaginatedBillingEventsResponse(BaseModel):
    total_count: int
    billing_events: List[BillingEventOut]

class PaginatedGenerationModelsResponse(BaseModel):
    total_count: int
    models: List[GenerationModel]


@router.get("/users", response_model=PaginatedUsersResponse)
async def read_users(
    skip: int = 0,
    limit: int = 10,
    country: Optional[str] = None,
    product_id: Optional[int] = None,
    username: Optional[str] = None,
    phone: Optional[str] = None,
    tenant_id: Optional[int] = None,
    sort_by: Optional[str] = None, # New sort_by parameter
    current_user: User = Depends(get_current_admin_user)
):
    print(f"DEBUG: read_users endpoint called with skip={skip}, limit={limit}, country={country}, product_id={product_id}, username={username}, phone={phone}, tenant_id={tenant_id}, sort_by={sort_by}")
    is_super_admin = current_user.get("is_super_admin", 0)
    
    final_tenant_ids_filter: Optional[List[int]] = None

    if not is_super_admin:
        user_tenant_id = current_user.get("tenant_id")
        if user_tenant_id:
            tenant_hierarchy = get_tenant_hierarchy(user_tenant_id)
            final_tenant_ids_filter = [t['id'] for t in tenant_hierarchy]
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin user has no associated tenant.")

    print(f"DEBUG: final_tenant_ids_filter={final_tenant_ids_filter}")
    try:
        total_users, users = get_all_users(
            tenant_ids=final_tenant_ids_filter, 
            skip=skip, 
            limit=limit, 
            country=country, 
            product_id=product_id,
            username=username,
            phone=phone,
            sort_by=sort_by
        )
        print(f"DEBUG: get_all_users returned total_users={total_users}, users_count={len(users)}")
        print(f"DEBUG: users array before returning to frontend: {users}")
        return {"total_users": total_users, "users": [{'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin']), 'full_name': user['full_name'], 'tenant_id': user['tenant_id'], 'agent_name': user['agent_name'], 'country_name': user['country_name']} for user in users]}
    except Exception as e:
        print(f"ERROR: Exception in read_users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get("/billing_events", response_model=PaginatedBillingEventsResponse)
async def read_billing_events(
    skip: int = 0,
    limit: int = 10,
    country: Optional[str] = None,
    agent_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")

    total_count, billing_events = get_all_billing_events(
        tenant_id=tenant_id_filter,
        skip=skip,
        limit=limit,
        country=country,
        agent_id=agent_id,
        start_date=start_date,
        end_date=end_date
    )
    return {"total_count": total_count, "billing_events": billing_events}

class LookupItem(BaseModel):
    id: Optional[int] = None
    name: str
    name_ar: Optional[str] = None # NEW
    api_name: Optional[str] = None
    is_multilingual: Optional[bool] = False # NEW field
    category: Optional[str] = None # NEW
    category_ar: Optional[str] = None # NEW
    created_by: Optional[int] = None # ADDED
    created_by_username: Optional[str] = None # ADDED

class PropertyTypeCreate(BaseModel):
    name: str
    audience_type: str

class PropertyTypeOut(BaseModel):
    id: int
    name: str
    api_name: str
    audience_type: Optional[str] = None # Made optional

class ModelIn(BaseModel):
    name: str
    display_name: str
    method: str
    provider: str



class GenerationModelCreate(BaseModel):
    model_name: str
    model_api_name: str
    api_key: str

class GenerationModelUpdate(BaseModel):
    model_name: str
    model_api_name: str
    api_key: str

@router.get("/property_types/{audience_type}", response_model=List[PropertyTypeOut])
async def get_property_types(
    audience_type: str, 
    current_user: User = Depends(get_current_admin_user),
    lang: Optional[str] = None
):
    if audience_type not in ["school", "university", "company", "general", "vocational", "community", "question"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    
    properties = get_property_types_by_audience(
        audience_type,
        lang=lang,
        tenant_id=current_user["tenant_id"]
    )
    
    # Simulate is_multilingual flag for demonstration purposes
    # In a real application, this flag would be fetched from the database
    multilingual_properties_api_names = [
        "school_types", "university_majors", "companies", 
        "job_roles", "departments", "university_courses"
    ]
    
    for prop in properties:
        # Ensure api_name exists before checking
        if prop.get("api_name") and prop["api_name"] in multilingual_properties_api_names:
            prop["is_multilingual"] = True
        else:
            prop["is_multilingual"] = False # Explicitly set to False if not in the list or api_name is missing

    return properties

@router.post("/property_types", response_model=PropertyTypeOut, status_code=status.HTTP_201_CREATED)
async def add_property_type(property_type: PropertyTypeCreate, current_user: User = Depends(get_current_admin_user)):
    api_name = property_type.name.lower().replace(" ", "_")
    
    existing_type = get_property_type_by_api_name(api_name)
    if existing_type:
        raise HTTPException(status_code=409, detail=f"Property type with API name '{api_name}' already exists.")

    new_id = create_property_type(
        name=property_type.name,
        api_name=api_name,
        audience_type=property_type.audience_type
    )
    
    return {
        "id": new_id,
        "name": property_type.name,
        "api_name": api_name,
        "audience_type": property_type.audience_type
    }

@router.delete("/property_types/{api_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_property_type(api_name: str, current_user: User = Depends(get_current_admin_user)):
    if not re.match(r'^[a-zA-Z0-9_]+$', api_name):
        raise HTTPException(status_code=400, detail="Invalid property name format.")
    
    existing_type = get_property_type_by_api_name(api_name)
    if not existing_type:
        raise HTTPException(status_code=404, detail="Property type not found.")

    try:
        delete_property_type(api_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete property type: {e}")
    
    return


@router.get("/users", response_model=PaginatedUsersResponse)
async def read_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin_user)
):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user["tenant_id"]
    total_users, users = get_all_users(tenant_id=tenant_id_filter, skip=skip, limit=limit)
    print(f"DEBUG: Raw users from database: {users}")
    return {"total_users": total_users, "users": [{'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin']), 'full_name': user['full_name'], 'agent_name': user['agent_name']} for user in users]}

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, current_user: User = Depends(get_current_admin_user)):
    country_name = (user.country or '').strip()
    if not country_name:
        raise HTTPException(status_code=400, detail="Country is required")

    if len(user.username) < 6:
        raise HTTPException(status_code=400, detail="Username must be at least 6 characters")

    # Determine tenant_id for the new user
    new_user_tenant_id: Optional[int] = None

    is_super_admin = current_user.get("is_super_admin", 0)

    if is_super_admin:
        # Superadmin can explicitly set tenant_id from payload or derive from country
        if user.tenant_id is not None:
            new_user_tenant_id = user.tenant_id
        else:
            # Logic to derive tenant_id from country for superadmin if not provided
            tenant_name = country_name[:3].upper() + "1"
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM tenants WHERE name = ?", (tenant_name,))
                tenant_row = cur.fetchone()
                if tenant_row:
                    new_user_tenant_id = tenant_row["id"]
                else:
                    new_user_tenant_id = create_tenant(tenant_name)
                    cur.execute("SELECT country_id FROM countries WHERE name = ?", (country_name,))
                    country_row = cur.fetchone()
                    if not country_row:
                        raise HTTPException(status_code=400, detail="Country not found")
                    country_id = country_row["country_id"]
                    cur.execute("INSERT INTO tenant_countries (tenant_id, country_id) VALUES (?, ?)", (new_user_tenant_id, country_id))
                    conn.commit()
            finally:
                conn.close()
    else:
        # Regular admin can only create users within their own tenant
        new_user_tenant_id = current_user.get("tenant_id")
        if new_user_tenant_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin user has no associated tenant.")

    # Ensure new_user_tenant_id is not None before proceeding
    if new_user_tenant_id is None:
        raise HTTPException(status_code=500, detail="Failed to determine tenant_id for new user.")

    print(f"DEBUG: create_new_user - Final new_user_tenant_id before create_user: {new_user_tenant_id}")
    hashed_password = get_password_hash(user.password)
    create_user(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=1,
        full_name=user.full_name, # Or a new field if you add it
        tenant_id=new_user_tenant_id,
        mobile_phone=user.mobile_phone,
        email=user.email
    )
    new_user = get_user(user.username, tenant_id=new_user_tenant_id)
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")
    return {'id': new_user['id'], 'username': new_user['username'], 'is_admin': bool(new_user['is_admin']), 'full_name': new_user['full_name'], 'tenant_id': new_user_tenant_id}
@router.put("/users/{user_id}", response_model=UserOut)
async def update_single_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_admin_user)):
    current_user_tenant_id = current_user.get("tenant_id")
    is_super_admin = current_user.get("is_super_admin", 0)

    # Super admin can fetch any user, admin is restricted to their tenant
    tenant_id_filter = None if is_super_admin else current_user_tenant_id

    db_user = get_user_by_id(user_id, tenant_id=tenant_id_filter)
    if not db_user:
        # If admin, maybe the user is in another tenant. For superadmin, it just means not found.
        detail = "User not found or not in your tenant" if not is_super_admin else "User not found"
        raise HTTPException(status_code=404, detail=detail)
    
    update_data = user_update.dict(exclude_unset=True)
    
    password = update_data.pop("password", None)
    if password:
        hashed_password = get_password_hash(password)
        update_user_password(user_id, hashed_password)

    if "is_admin" in update_data:
        update_data["is_admin"] = int(update_data["is_admin"])

    if update_data:
        update_user(user_id, **update_data)
    
    # Fetch the updated user data, again respecting tenancy for admins
    updated_user = get_user_by_id(user_id, tenant_id=tenant_id_filter)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found after update")
    
    return {
        'id': updated_user['id'], 
        'username': updated_user['username'], 
        'is_admin': bool(updated_user['is_admin']), 
        'full_name': updated_user['full_name'],
        'tenant_id': updated_user['tenant_id']
    }

class UserIdsRequest(BaseModel):
    user_ids: List[int]

@router.delete("/users/batch", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_users_endpoint(payload: UserIdsRequest, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None if is_super_admin else current_user.get("tenant_id")

    # Optional: Add more robust checks here to ensure users being deleted belong to the admin's tenant
    # For now, delete_multiple_users in database.py will handle the tenant filtering.

    delete_multiple_users(payload.user_ids, tenant_id=tenant_id_filter)
    return

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_user(user_id: int, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    current_user_tenant_id = current_user.get("tenant_id")

    # Super admin can delete any user. Admin can only delete users in their own tenant.
    user_to_delete = get_user_by_id(user_id, tenant_id=None if is_super_admin else current_user_tenant_id)

    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not in your tenant")

    # Additional check to prevent admin from deleting superadmin
    if 'is_super_admin' in user_to_delete.keys() and user_to_delete['is_super_admin'] and not is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot delete superadmins.")

    delete_user(user_id)
    return

# Endpoints for managing question properties (lookup tables)
@router.get("/properties/{property_type}", response_model=List[LookupItem])
async def get_properties(
    property_type: str,
    lang: Optional[str] = None,
    audience_type: Optional[str] = None, # NEW PARAMETER
    category: Optional[str] = None,      # NEW PARAMETER
    skip: int = 0,                       # NEW PARAMETER
    limit: int = 100,                    # NEW PARAMETER
    current_user: User = Depends(get_current_admin_user)
):
    print(f"DEBUG: get_properties called for property_type: {property_type}, lang: {lang}, audience_type: {audience_type}, category: {category}, skip: {skip}, limit: {limit}")
    
    # Logic for tenant filtering:
    # 1. Superadmin (is_super_admin=1): sees EVERYTHING (global + all tenants).
    # 2. Regular Admin: sees global (tenant_id IS NULL) + their own tenant.
    
    tenant_id_to_pass = current_user["tenant_id"]
    if current_user.get("is_super_admin") == 1:
        tenant_id_to_pass = None # Signal to bypass filter in database.py
    
    items = get_lookup_data_list(
        property_type, 
        lang=lang, 
        audience_type=audience_type, 
        category=category, 
        tenant_id=tenant_id_to_pass,
        skip=skip,
        limit=limit
    ) 
    print(f"DEBUG: get_properties returning {len(items)} items.")
    return items

@router.get("/models")
async def admin_list_models(current_user: User = Depends(get_current_admin_user)):
    return get_all_models()

@router.post("/models")
async def admin_create_model(model: ModelIn, current_user: User = Depends(get_current_admin_user)):
    new_id = create_model(model.name, model.display_name, model.method, model.provider)
    return {"id": new_id, **model.model_dump()}

@router.put("/models/{model_id}")
async def admin_update_model(model_id: int, model: ModelIn, current_user: User = Depends(get_current_admin_user)):
    update_model(model_id, name=model.name, display_name=model.display_name, method=model.method, provider=model.provider)
    row = get_model_by_name(model.name)
    return row or {"id": model_id, **model.model_dump()}

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_model(model_id: int, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")
    
    db_model = get_generation_model_by_id(model_id, tenant_id=tenant_id_filter)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    delete_generation_model(model_id, tenant_id=tenant_id_filter)
    return

@router.get("/generation_models", response_model=PaginatedGenerationModelsResponse)
async def get_generation_models(current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user["tenant_id"]
    total_count, models_list = get_all_generation_models(tenant_id=tenant_id_filter)
    print(f"DEBUG: get_generation_models returning models: {models_list}")
    # Exclude api_key from the response
    return {"total_count": total_count, "models": [{k: v for k, v in model.items() if k != 'api_key'} for model in models_list]}

@router.post("/generation_models", response_model=GenerationModel, status_code=status.HTTP_201_CREATED)
async def create_new_generation_model(model: GenerationModelCreate, current_user: User = Depends(get_current_admin_user)):
    new_id = create_generation_model(
        model_name=model.model_name,
        model_api_name=model.model_api_name,
        generation_method="ai", # Assuming "ai" as a default or common method, adjust if needed
        tenant_id=current_user.get("tenant_id") if not current_user.get("is_super_admin", 0) else None,
        is_default=False,  # Default value
        is_active=True,  # Default value
        api_key=model.api_key
    )
    return {
        "id": new_id,
        "model_name": model.model_name,
        "model_api_name": model.model_api_name,
    }

@router.put("/generation_models/{model_id}", response_model=GenerationModel)
async def update_single_generation_model(model_id: int, model: GenerationModelUpdate, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")
    db_model = get_generation_model_by_id(model_id, tenant_id=tenant_id_filter)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    update_generation_model(
        model_id=model_id,
        tenant_id=tenant_id_filter,
        model_name=model.model_name,
        model_api_name=model.model_api_name,
        generation_method=db_model['generation_method'], # Keep existing value
        is_default=db_model['is_default'], # Keep existing value
        is_active=db_model['is_active'], # Keep existing value
        api_key=model.api_key
    )
    return {
        "id": model_id,
        "model_name": model.model_name,
        "model_api_name": model.model_api_name,
    }

@router.delete("/generation_models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_generation_model(model_id: int, current_user: User = Depends(get_current_admin_user)):
    is_super_admin = current_user.get("is_super_admin", 0)
    tenant_id_filter = None
    if not is_super_admin:
        tenant_id_filter = current_user.get("tenant_id")
    db_model = get_generation_model_by_id(model_id, tenant_id=tenant_id_filter)
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    delete_generation_model(model_id, tenant_id=tenant_id_filter)
    return

@router.get("/generation_models/{model_id}", response_model=GenerationModel)
async def get_single_generation_model(model_id: int, current_user: User = Depends(get_current_admin_user)):
    try:
        is_super_admin = current_user.get("is_super_admin", 0)
        tenant_id_filter = None
        if not is_super_admin:
            tenant_id_filter = current_user.get("tenant_id")
        db_model_row = get_generation_model_by_id(model_id, tenant_id=tenant_id_filter)
        if not db_model_row:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Convert sqlite3.Row to a standard dict before returning
        model_dict = dict(db_model_row)
        
        return model_dict
    except Exception as e:
        import traceback
        print("ERROR in get_single_generation_model:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/products", response_model=List[Product])
async def admin_list_products(current_user: User = Depends(get_current_admin_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        is_super_admin = current_user.get("is_super_admin", 0)
        tenant_id_filter = None
        if not is_super_admin:
            tenant_id_filter = current_user.get("tenant_id")
        
        products = get_all_billing_products(tenant_id=tenant_id_filter, is_active=None) # Admin can see inactive products

        # Fetch generated count and remaining balance for each product
        for product in products:
            audience_type = product.get("audience_type")
            product_tenant_id = product.get("tenant_id") # Can be None for global products

            # Determine the tenant_id to use for balance/generated count lookup
            # If product is global (tenant_id is None), use the current admin's tenant_id
            # # If product is tenant-specific, use that product's tenant_id
            lookup_tenant_id = product_tenant_id if product_tenant_id is not None else tenant_id_filter

            if audience_type is not None:
                # Get total sold count
                if lookup_tenant_id is not None:
                    sql_query_total_sold = "SELECT COUNT(*) FROM billing_events be WHERE be.tenant_id = ? AND be.event_type = 'credit' AND be.product_id = ?"
                    params = (lookup_tenant_id, product["id"])
                else: # This is for superadmin looking at global products
                    sql_query_total_sold = "SELECT COUNT(*) FROM billing_events be WHERE be.event_type = 'credit' AND be.product_id = ?"
                    params = (product["id"],)

                cur.execute(sql_query_total_sold, params)
                total_sold = cur.fetchone()[0] or 0
                product["total_sold"] = total_sold

                # Get remaining balance
                if lookup_tenant_id is not None:
                    cur.execute(
                        "SELECT balance FROM billing_tenant_question_balances WHERE tenant_id = ? AND audience_type = ?",
                        (lookup_tenant_id, audience_type)
                    )
                    remaining_balance = cur.fetchone()
                    product["remaining_balance"] = remaining_balance[0] if remaining_balance else 0
                else:
                    product["remaining_balance"] = 0 # For superadmin and global products, balance is not well-defined
            else:
                product["total_sold"] = 0
                product["remaining_balance"] = 0

        return products
    finally:
        conn.close()

@router.post("/properties/{property_type}", response_model=LookupItem, status_code=status.HTTP_201_CREATED)
async def add_property(property_type: str, item: LookupItem, current_user: User = Depends(get_current_admin_user)):
    print(f"DEBUG: add_property called for property_type: {property_type}, item: {item.dict()}, user_id: {current_user['id']}")
    
    # Determine tenant_id: Superadmins create global properties (tenant_id=None)
    tenant_id_to_save = current_user["tenant_id"]
    if current_user.get("is_super_admin") == 1:
        tenant_id_to_save = None

    # Check if item already exists (case-insensitive) for the target scope
    existing_items = get_lookup_data_list(property_type, tenant_id=tenant_id_to_save) 
    if item.name.lower() in [ei['name'].lower() for ei in existing_items]:
        raise HTTPException(status_code=409, detail=f"{item.name} already exists in {property_type}")

    new_item_id = add_lookup_data(
        property_type,
        item.name,
        name_ar=item.name_ar,
        audience_type=item.audience_type,
        category=item.category,
        category_ar=item.category_ar,
        tenant_id=tenant_id_to_save,
        created_by=current_user["id"]
    )
    return {
        "id": new_item_id,
        "name": item.name,
        "name_ar": item.name_ar, # NEW
        "api_name": item.api_name,
        "audience_type": item.audience_type, # NEW
        "category": item.category, # NEW
        "category_ar": item.category_ar # NEW
    }

@router.put("/properties/{property_type}/{item_id}", response_model=LookupItem)
async def update_property(property_type: str, item_id: int, item: LookupItem, current_user: User = Depends(get_current_admin_user)):
    try:
        # Check if item_id exists
        # For simplicity, we'll assume item_id directly maps to the row ID in the lookup table
        # A more robust solution would involve fetching the item by ID first
        update_lookup_data(
            property_type, 
            item_id, 
            name=item.name,
            name_ar=item.name_ar,
            audience_type=item.audience_type,
            category=item.category,
            category_ar=item.category_ar
        )
        return item
    except HTTPException:
        # Re-raise HTTPException directly
        raise
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full traceback to console/logs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update property: {e}")

@router.delete("/properties/{property_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(property_type: str, item_id: int, current_user: User = Depends(get_current_admin_user)):
    print(f"DEBUG: delete_property called for property_type: {property_type}, item_id: {item_id}")
    delete_lookup_data(property_type, item_id)
    print(f"DEBUG: delete_property database operation completed for item_id: {item_id}")

class AudienceFieldsUpdateRequest(RootModel[dict[str, bool]]):
    pass


# Temporary bootstrap endpoint to create/update a user via app hashing
class BootstrapUser(BaseModel):
    username: str
    password: str
    tenant_id: int
    is_admin: Optional[bool] = True

@router.post("/bootstrap_user")
async def bootstrap_user(user_req: BootstrapUser):
    if os.getenv("BOOTSTRAP_ENABLED", "false").lower() not in ("1", "true", "yes"):
        raise HTTPException(status_code=403, detail="Bootstrap disabled")
    # Check if user exists
    existing = get_user(user_req.username, tenant_id=user_req.tenant_id)
    hashed = get_password_hash(user_req.password)
    if not existing:
        create_user(
            username=user_req.username,
            hashed_password=hashed,
            is_admin=int(user_req.is_admin or False),
            full_name=None,
            tenant_id=user_req.tenant_id,
        )
        created = get_user(user_req.username, tenant_id=user_req.tenant_id)
        return {"status": "created", "id": created["id"], "tenant_id": created["tenant_id"], "is_admin": bool(created["is_admin"]) }
    else:
        # Update password and admin flag
        update_user_password(existing["id"], hashed)
        if user_req.is_admin is not None:
            update_user(existing["id"], is_admin=int(user_req.is_admin))
        updated = get_user(user_req.username, tenant_id=user_req.tenant_id)
        return {"status": "updated", "id": updated["id"], "tenant_id": updated["tenant_id"], "is_admin": bool(updated["is_admin"]) }

@router.put("/audience_fields/{audience_type}")
async def update_audience_fields_endpoint(
    audience_type: str,
    fields_update: AudienceFieldsUpdateRequest,
    current_user: User = Depends(get_current_admin_user)
):
    if audience_type not in ["school", "university", "company", "vocational", "community"]:
        raise HTTPException(status_code=400, detail="Invalid audience type")
    
    try:
        update_audience_fields(audience_type, fields_update.root)
        return {"message": "Audience fields updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update audience fields: {e}")
