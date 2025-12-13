import asyncio
import base64
import json
import os
import zipfile
from io import BytesIO

import httpx

from app.config import settings


class YouCamService:
    """Service for interacting with YouCam Skin Analysis API"""

    def __init__(self):
        self.base_url = settings.youcam_base_url
        self.api_key = settings.youcam_api_key

        # For v2 API, only Authorization header with API Key is required
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """
        Step 1: Upload file to YouCam and get file_id

        Returns:
            file_id for use in analysis task
        """
        file_size = len(file_content)

        # Request presigned upload URL
        payload = {
            "files": [
                {"content_type": content_type, "file_name": file_name, "file_size": file_size}
            ]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get presigned URL
            response = await client.post(
                f"{self.base_url}/file/skin-analysis", headers=self.headers, json=payload
            )
            response.raise_for_status()
            result = response.json()

            if result["status"] != 200:
                raise Exception(f"Failed to get upload URL: {result}")

            file_data = result["data"]["files"][0]
            file_id = file_data["file_id"]
            upload_request = file_data["requests"][0]

            # Upload file to presigned URL
            upload_headers = upload_request["headers"]
            upload_url = upload_request["url"]

            upload_response = await client.request(
                method=upload_request["method"],
                url=upload_url,
                headers=upload_headers,
                content=file_content,
            )
            upload_response.raise_for_status()

            return file_id

    async def submit_task(self, file_id: str, src_file_url: str | None = None) -> str:
        """
        Step 2: Submit skin analysis task

        Returns:
            task_id for polling results
        """
        # All 14 available actions from YouCam API v2.0 documentation
        # Mapped to Indonesian UI: Laporan Permukaan + Laporan Mendalam
        dst_actions = [
            "acne",               # Jerawat
            "dark_circle_v2",     # Lingkaran Hitam
            "droopy_upper_eyelid",
            "firmness",           # Serat Kolagen
            "oiliness",           # Sebum
            "radiance",           # Warna Kulit
            "age_spot",           # Flek, Titik UV, Pigmen
            "wrinkle",            # Keriput
            "redness",            # Sensitivitas PL
            "texture",            # Tekstur
            "moisture",           # Kelembaban
            "eye_bag",            # Kantung Mata
            "droopy_lower_eyelid",
            "pore",               # Pori-Pori, Komedo
        ]

        payload = {
            "src_file_id": file_id,
            "dst_actions": dst_actions,
        }

        if src_file_url:
            payload["src_file_url"] = src_file_url

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/task/skin-analysis", headers=self.headers, json=payload
            )

            # Log detailed error information for debugging
            if response.status_code != 200:
                print(f"ERROR: YouCam API returned status {response.status_code}")
                print(f"Request URL: {self.base_url}/task/skin-analysis")
                print(f"Request payload: {json.dumps(payload, indent=2)}")
                print(f"Response body: {response.text}")
                print(f"Response headers: {dict(response.headers)}")

            response.raise_for_status()
            result = response.json()

            if result["status"] != 200:
                raise Exception(f"Failed to submit task: {result}")

            return result["data"]["task_id"]

    async def poll_task(self, task_id: str, max_attempts: int = 60, interval: int = 2) -> dict:
        """
        Step 3: Poll task status until complete

        Returns:
            Task result with status and results URL
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _attempt in range(max_attempts):
                response = await client.get(
                    f"{self.base_url}/task/skin-analysis/{task_id}",
                    headers=self.headers,  # Use full headers including Secret Key
                )
                response.raise_for_status()
                result = response.json()

                if result["status"] != 200:
                    raise Exception(f"Failed to poll task: {result}")

                data = result["data"]
                task_status = data.get("task_status")

                if task_status == "success":  # YouCam v2 API returns 'success' not 'completed'
                    return data
                elif task_status == "error":  # YouCam v2 API returns 'error' not 'failed'
                    error = data.get("error", "Unknown error")
                    error_msg = data.get("error_message", "No error message")
                    raise Exception(f"Task failed: {error} - {error_msg}")

                # Wait before next poll
                await asyncio.sleep(interval)

            raise Exception(f"Task polling timeout after {max_attempts * interval} seconds")

    async def download_and_extract_zip(
        self, zip_url: str, task_id: str
    ) -> tuple[dict, dict[str, bytes]]:
        """
        Step 4: Download and extract ZIP file

        Returns:
            Tuple of (score_info dict, masks dict)
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(zip_url)
            response.raise_for_status()

            # Extract ZIP in memory
            zip_data = BytesIO(response.content)
            scores = None
            masks = {}

            with zipfile.ZipFile(zip_data) as zf:
                # Read score_info.json
                score_file = "skinanalysisResult/score_info.json"
                if score_file in zf.namelist():
                    with zf.open(score_file) as f:
                        scores = json.load(f)

                # Extract all PNG masks
                for name in zf.namelist():
                    if name.endswith(".png") and "skinanalysisResult/" in name:
                        mask_name = os.path.basename(name)
                        with zf.open(name) as f:
                            masks[mask_name] = f.read()

            if scores is None:
                raise Exception("score_info.json not found in ZIP")

            return scores, masks

    async def analyze_image(self, image_content: bytes, file_name: str, content_type: str) -> dict:
        """
        Complete pipeline: upload -> submit -> poll -> extract -> generate composite

        Returns:
            Dict with scores, composite_image, masks (base64), and task_id
        """
        # Step 1: Upload file
        file_id = await self.upload_file(image_content, file_name, content_type)

        # Step 2: Submit analysis task
        task_id = await self.submit_task(file_id)

        # Step 3: Poll for completion
        task_result = await self.poll_task(task_id)

        # Step 4: Download and extract results
        zip_url = task_result["results"]["url"]
        scores, masks = await self.download_and_extract_zip(zip_url, task_id)

        # Step 5: Generate composite visualization
        from app.services.image_processing import (
            create_all_concern_overlays,
            create_composite_visualization,
            create_landmark_enhanced_overlays,
        )

        try:
            composite_bytes = create_composite_visualization(
                image_content,
                masks,
                scores
            )
            composite_b64 = base64.b64encode(composite_bytes).decode("utf-8")
        except Exception as e:
            print(f"Warning: Failed to create composite: {e}")
            # Fallback to original image if composite fails
            composite_b64 = base64.b64encode(image_content).decode("utf-8")

        # Step 5b: Generate per-concern overlay images with landmark enhancement
        concern_overlays_b64 = {}
        landmark_statuses = {}
        try:
            # Gunakan landmark-enhanced overlays (MediaPipe + YouCam mask)
            concern_overlays, landmark_statuses = create_landmark_enhanced_overlays(
                image_content, masks
            )
            concern_overlays_b64 = {
                name: base64.b64encode(content).decode("utf-8")
                for name, content in concern_overlays.items()
            }
        except Exception as e:
            print(f"Warning: Failed to create landmark-enhanced overlays: {e}")
            # Fallback ke overlay biasa tanpa landmark
            try:
                concern_overlays = create_all_concern_overlays(image_content, masks)
                concern_overlays_b64 = {
                    name: base64.b64encode(content).decode("utf-8")
                    for name, content in concern_overlays.items()
                }
                landmark_statuses = {"_global": {"landmark_status": "failed", "fallback_used": True}}
            except Exception as e2:
                print(f"Warning: Fallback overlay creation also failed: {e2}")

        # Convert masks to base64 for JSON response
        masks_b64 = {
            name: base64.b64encode(content).decode("utf-8") for name, content in masks.items()
        }

        # Convert original image to base64
        original_b64 = base64.b64encode(image_content).decode("utf-8")

        # Step 6: Generate AI-powered analysis texts (no fallback for development)
        from app.services.ai_analysis_service import ai_analysis_service

        analysis_texts = {}
        try:
            analysis_texts = await ai_analysis_service.generate_all_analyses(scores)
        except Exception as e:
            # No fallback - let error propagate for debugging
            print(f"ERROR: Failed to generate AI analysis texts: {e}")
            raise e

        return {
            "task_id": task_id,
            "status": "completed",
            "scores": scores,
            "composite_image": composite_b64,  # Composite visualization
            "concern_overlays": concern_overlays_b64,  # Per-concern overlay images (landmark-enhanced)
            "masks": masks_b64,
            "original_image": original_b64,
            "analysis_texts": analysis_texts,  # Dynamic Indonesian analysis texts
            "landmark_statuses": landmark_statuses,  # Status deteksi landmark per concern
        }


# Singleton instance
youcam_service = YouCamService()
