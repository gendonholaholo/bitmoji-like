from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.schemas import ResultResponse
from app.services.youcam_service import youcam_service

router = APIRouter(prefix="/api", tags=["skin-analysis"])

# In-memory storage for results (in production, use Redis or database)
results_cache: dict[str, dict] = {}


@router.post("/analyze")
async def analyze_skin(file: UploadFile = File(...)):
    """
    Upload an image and perform complete skin analysis.

    This endpoint now performs the FULL analysis pipeline:
    - BYPASS_YOUCAM=true: Uses mock data + MediaPipe + GPT-4o-mini
    - BYPASS_YOUCAM=false: Uses real YouCam API + MediaPipe + GPT-4o-mini

    Returns complete analysis results (scores, overlays, AI analysis texts)
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read file content
        content = await file.read()

        # Validate file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Perform complete analysis (respects BYPASS_YOUCAM setting)
        result = await youcam_service.analyze_image(
            content, file.filename or "image.jpg", file.content_type
        )

        # Cache the result
        results_cache[result["task_id"]] = result

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        import logging
        import traceback

        logging.error(f"Analysis failed: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/result/{task_id}", response_model=ResultResponse)
async def get_result(task_id: str):
    """
    Get analysis results for a task

    Polls YouCam API and returns results when ready
    """
    try:
        # Check if we've already completed this task
        if task_id in results_cache and results_cache[task_id].get("status") == "completed":
            return JSONResponse(content=results_cache[task_id])

        # Poll the task
        task_result = await youcam_service.poll_task(task_id, max_attempts=1, interval=0)

        task_status = task_result.get("task_status")

        if task_status == "success":  # YouCam v2 API returns 'success' not 'completed'
            # Download and extract results
            zip_url = task_result["results"]["url"]
            scores, masks = await youcam_service.download_and_extract_zip(zip_url, task_id)

            # Generate composite visualization
            import base64

            from app.services.image_processing import create_composite_visualization

            composite_b64 = None

            # Try to generate composite if we have original image cached
            if task_id in results_cache and results_cache[task_id].get("original_image"):
                try:
                    original_b64 = results_cache[task_id]["original_image"]
                    original_bytes = base64.b64decode(original_b64)

                    composite_bytes = create_composite_visualization(original_bytes, masks, scores)
                    composite_b64 = base64.b64encode(composite_bytes).decode("utf-8")
                except Exception as e:
                    print(f"Warning: Failed to create composite: {e}")
                    # Fallback to original image
                    composite_b64 = original_b64

            # Convert masks to base64
            masks_b64 = {
                name: base64.b64encode(content).decode("utf-8") for name, content in masks.items()
            }

            result = {
                "task_id": task_id,
                "status": "completed",
                "scores": scores,
                "composite_image": composite_b64,
                "masks": masks_b64,
                "original_image": None,  # Don't send back to frontend (too large)
            }

            # Cache the result
            results_cache[task_id] = result

            return JSONResponse(content=result)

        elif task_status == "error":  # YouCam v2 API returns 'error' not 'failed'
            error = task_result.get("error", "Unknown error")
            error_msg = task_result.get("error_message", "No error message")
            return ResultResponse(
                task_id=task_id, status="failed", error=error, error_message=error_msg
            )
        else:
            # Still processing
            return ResultResponse(task_id=task_id, status="processing")

    except HTTPException:
        raise
    except Exception:
        # If polling fails, assume still processing
        return ResultResponse(task_id=task_id, status="processing")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "youcam-skin-analysis"}
