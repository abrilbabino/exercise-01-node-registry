"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

# TODO: Implement your FastAPI app here
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List

from . import models, schemas
from .database import engine, get_db

# Create the database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Node Registry API")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Returns the service health, database connection status,
    and the count of active nodes.
    """
    try:
        # Perform a simple query to check DB connectivity
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Requirement: nodes_count is the number of active nodes (status = "active")
    active_count = db.query(models.Node).filter(models.Node.status == "active").count()

    return {
        "status": "ok",
        "db": db_status,
        "nodes_count": active_count
    }

@app.post("/api/nodes", response_model=schemas.NodeResponse, status_code=status.HTTP_201_CREATED)
def register_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    """
    Registers a new node in the system.
    Returns 409 if the name already exists.
    """
    db_node = models.Node(**node.model_dump())
    try:
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Node name already exists"
        )

@app.get("/api/nodes", response_model=List[schemas.NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    """
    Returns a list of all nodes, including inactive ones.
    """
    return db.query(models.Node).all()

@app.get("/api/nodes/{name}", response_model=schemas.NodeResponse)
def get_node(name: str, db: Session = Depends(get_db)):
    """
    Retrieves a single node by its unique name.
    Returns 404 if not found.
    """
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node

@app.put("/api/nodes/{name}", response_model=schemas.NodeResponse)
def update_node(name: str, node_update: schemas.NodeUpdate, db: Session = Depends(get_db)):
    """
    Updates node fields (host, port).
    Returns the updated node or 404 if not found.
    """
    db_node = db.query(models.Node).filter(models.Node.name == name).first()
    if not db_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    # Update only fields provided in the request
    update_data = node_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_node, key, value)

    db.commit()
    db.refresh(db_node)
    return db_node

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(get_db)):
    """
    Performs a soft-delete by setting the node status to 'inactive'.
    Returns 204 on success or 404 if not found.
    """
    db_node = db.query(models.Node).filter(models.Node.name == name).first()
    if not db_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    # Requirement: Soft-delete behavior (status = inactive)
    db_node.status = "inactive"
    db.commit()
    return None