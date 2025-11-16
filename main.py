import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Lead, Offer, Click, User, Product

app = FastAPI(title="Affiliate Marketing Funnel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Affiliate Funnel Backend Running"}

# Public API
class LeadIn(BaseModel):
    name: str
    email: EmailStr
    source: Optional[str] = "landing"

class LeadOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    source: Optional[str]

@app.post("/api/leads", response_model=LeadOut)
async def create_lead(lead: LeadIn):
    try:
        lead_obj = Lead(**lead.model_dump())
        inserted_id = create_document("lead", lead_obj)
        return {"id": inserted_id, **lead_obj.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/offers", response_model=List[Offer])
async def list_offers():
    try:
        docs = get_documents("offer", {"active": True}, limit=50)
        # Convert Mongo _id to string and map into Offer model
        offers = []
        for d in docs:
            d.pop("_id", None)
            offers.append(Offer(**d))
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/redirect/{slug}")
async def redirect_offer(slug: str, request: Request, lead_id: Optional[str] = None):
    # find offer
    try:
        offer_doc = db["offer"].find_one({"slug": slug, "active": True})
        if not offer_doc:
            raise HTTPException(status_code=404, detail="Offer not found")
        # log click
        click = Click(
            slug=slug,
            lead_id=lead_id,
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        create_document("click", click)
        return {"url": offer_doc.get("url")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin helper endpoints to seed data (simple, not secured for demo)
class OfferIn(BaseModel):
    slug: str
    title: str
    url: str
    description: Optional[str] = None
    active: bool = True

@app.post("/api/admin/offers")
async def create_offer(offer: OfferIn):
    try:
        offer_obj = Offer(**offer.model_dump())
        inserted_id = create_document("offer", offer_obj)
        return {"id": inserted_id, **offer_obj.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
