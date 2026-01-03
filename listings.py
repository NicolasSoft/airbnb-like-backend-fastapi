from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import models
from app.schemas import schemas

router = APIRouter()

# Criar anúncio (somente host)
@router.post("/", response_model=schemas.ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing_in: schemas.ListingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not current_user.is_host:
        raise HTTPException(status_code=403, detail="Only hosts can create listings")

    listing = models.Listing(
        title=listing_in.title,
        description=listing_in.description,
        price_per_night=listing_in.price_per_night,
        location=listing_in.location,
        host_id=current_user.id,
    )

    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


# Listar anúncios com filtros
@router.get("/", response_model=List[schemas.ListingOut])
def list_listings(
    db: Session = Depends(get_db),
    location: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    query = db.query(models.Listing)

    if location:
        query = query.filter(models.Listing.location.ilike(f"%{location}%"))
    if min_price is not None:
        query = query.filter(models.Listing.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(models.Listing.price_per_night <= max_price)

    return query.all()


# Detalhes de um anúncio
@router.get("/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


# Atualizar anúncio (somente dono)
@router.put("/{listing_id}", response_model=schemas.ListingOut)
def update_listing(
    listing_id: int,
    listing_in: schemas.ListingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in listing_in.dict().items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)
    return listing


# Deletar anúncio
@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.host_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(listing)
    db.commit()
