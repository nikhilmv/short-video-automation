import asyncio
import os
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.dependencies.auth import get_current_user
from app.models.creation import Creation
from app.models.user import User
from app.schemas.creation import CreationCreateRequest, CreationResponse
from app.services.video_generator import process_story

router = APIRouter(
    prefix="/api/creations",
    tags=["Creations"]
)

STORAGE_DIR = "storage/videos"
os.makedirs(STORAGE_DIR, exist_ok=True)


def generate_video_background(creation_id: int, story_text: str):

    """Background task to run video generation pipeline and update DB status."""
    print("===========================...") 
    print("Background task to run video generation pipeline and update DB status.")
    print("===========================...")
    db = SessionLocal()
    output_filename = f"creation_{creation_id}.mp4"
    output_path = os.path.join(STORAGE_DIR, output_filename)

    try:
        # Update status to processing
        creation = db.get(Creation, creation_id)
        if creation:
            creation.status = "processing"
            db.commit()

        # Run async video generation pipeline with isolated workspace per creation
        print("===========================...") 
        print("Run async video generation pipeline")
        print("===========================...")
        work_dir = os.path.join("output_data", f"job_{creation_id}")
        asyncio.run(process_story(story_text=story_text, output_final=output_path, work_dir=work_dir))

        # Check if output video was created
        creation = db.get(Creation, creation_id)
        if creation and os.path.exists(output_path):
            creation.status = "completed"
            creation.video_url = f"/static/videos/{output_filename}"
            db.commit()
        elif creation:
            creation.status = "failed"
            db.commit()

    except Exception as e:
        print("===========================...")  
        print(f"Error generating video for creation {creation_id}: {e}")
        print("===========================...")  
        db.rollback()
        creation = db.get(Creation, creation_id)
        if creation:
            creation.status = "failed"
            db.commit()
    finally:
        db.close()


@router.post(
    "/generate",
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_stories(
    data: CreationCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("===========================...") 
    print("generate_stories called...")
    print("===========================...")


    # 1. Create a Creation record with 'pending' status
    creation = Creation(
        user_id=current_user.id,
        story_text=data.story_text,
        status="pending"
    )
    db.add(creation)
    db.commit()
    db.refresh(creation)

    # 2. Trigger video generation asynchronously in background
    print("===========================...") 
    print("Trigger video generation asynchronously in background...")
    print("===========================...")
    background_tasks.add_task(
        generate_video_background,
        creation.id,
        data.story_text
    )

    return {
        "success": True,
        "message": "Video generation started",
        "creation": {
            "id": creation.id,
            "story_text": creation.story_text,
            "status": creation.status,
            "video_url": creation.video_url
        }
    }


@router.get("")
@router.get("/")
def get_creations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    creations = db.scalars(
        select(Creation).where(Creation.user_id == current_user.id).order_by(Creation.id.desc())
    ).all()

    creation_list = [
        {
            "id": c.id,
            "story_text": c.story_text,
            "status": c.status,
            "video_url": c.video_url
        }
        for c in creations
    ]
    return {"success": True, "creations": creation_list}


@router.get("/{creation_id}")
def get_creation_by_id(
    creation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    creation = db.scalar(
        select(Creation).where(
            Creation.id == creation_id,
            Creation.user_id == current_user.id
        )
    )
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")

    return {
        "success": True,
        "creation": {
            "id": creation.id,
            "story_text": creation.story_text,
            "status": creation.status,
            "video_url": creation.video_url
        }
    }
