"""AI-powered skin analysis service using OpenAI GPT-4o-mini"""

import json
from typing import TypedDict

import httpx

from app.config import settings


class AIAnalysisResult(TypedDict):
    """Structure for AI-generated analysis"""

    quantitative: str
    precautions: str
    recommendations: list[str]
    root_cause: str
    lifestyle_tips: list[str]
    product_ingredients: list[str]


# Mapping dari key YouCam ke nama Indonesia
CONCERN_NAMES = {
    "oiliness": "Sebum/Minyak",
    "pore": "Pori-Pori",
    "age_spot": "Flek/Bintik Usia",
    "wrinkle": "Keriput",
    "acne": "Jerawat",
    "dark_circle_v2": "Lingkaran Hitam",
    "radiance": "Kecerahan Kulit",
    "texture": "Tekstur Kulit",
    "redness": "Kemerahan/Sensitivitas",
    "firmness": "Kekencangan/Kolagen",
    "moisture": "Kelembaban",
    "eye_bag": "Kantung Mata",
}

SYSTEM_PROMPT = """Anda adalah ahli dermatologi dan skincare profesional. Tugas Anda adalah menganalisis hasil pemindaian kulit wajah dan memberikan analisis yang akurat, informatif, dan actionable dalam Bahasa Indonesia formal.

ATURAN PENTING:
1. Gunakan Bahasa Indonesia formal dan direct
2. Berikan analisis berdasarkan data score yang diberikan (0-100, semakin tinggi semakin baik)
3. Jangan memberikan diagnosis medis spesifik
4. Fokus pada edukasi dan rekomendasi perawatan yang aman
5. Selalu rekomendasikan konsultasi dermatolog untuk kondisi serius

FORMAT OUTPUT (JSON):
{
    "quantitative": "Deskripsi kondisi kulit berdasarkan data (2-3 kalimat)",
    "precautions": "Hal-hal yang perlu diwaspadai (2-3 kalimat)",
    "recommendations": ["Rekomendasi 1", "Rekomendasi 2", "Rekomendasi 3"],
    "root_cause": "Penyebab utama kondisi ini (1-2 kalimat)",
    "lifestyle_tips": ["Tips gaya hidup 1", "Tips gaya hidup 2", "Tips gaya hidup 3"],
    "product_ingredients": ["Bahan aktif 1", "Bahan aktif 2", "Bahan aktif 3"]
}
"""


def format_scores_for_prompt(scores: dict) -> str:
    """Format YouCam scores into readable text for GPT prompt"""
    lines = []

    # Overall score and skin age
    if "all" in scores:
        all_score = scores["all"].get("score", 0)
        lines.append(f"- Skor Kesehatan Kulit Keseluruhan: {all_score:.1f}/100")

    if "skin_age" in scores:
        lines.append(f"- Usia Kulit (AI): {scores['skin_age']} tahun")

    lines.append("")
    lines.append("Skor Per Kategori (menggunakan raw_score, 0-100):")

    # Individual scores - use raw_score
    for key, name in CONCERN_NAMES.items():
        if key in scores and isinstance(scores[key], dict):
            raw_score = scores[key].get("raw_score", 0)
            lines.append(f"- {name}: {raw_score:.1f}/100")

    return "\n".join(lines)


def create_concern_prompt(concern_key: str, scores: dict) -> str:
    """Create prompt for specific concern analysis"""
    concern_name = CONCERN_NAMES.get(concern_key, concern_key)
    score_data = scores.get(concern_key, {})
    raw_score = score_data.get("raw_score", 50) if isinstance(score_data, dict) else 50

    # Get all scores context
    all_scores_text = format_scores_for_prompt(scores)

    prompt = f"""Analisis kondisi kulit untuk kategori: {concern_name}

DATA PEMINDAIAN KULIT:
{all_scores_text}

FOKUS ANALISIS: {concern_name} (Score: {raw_score:.1f}/100)

Berikan analisis lengkap untuk kategori {concern_name} dengan mempertimbangkan konteks score lainnya.
Ingat: Score lebih tinggi = kondisi lebih baik.

Berikan response dalam format JSON yang valid."""

    return prompt


class AIAnalysisService:
    """Service for generating AI-powered skin analysis using GPT-4o-mini"""

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.enabled = settings.ai_analysis_enabled and self.api_key is not None
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_analysis(self, concern_key: str, scores: dict) -> AIAnalysisResult | None:
        """
        Generate AI analysis for a specific concern.

        Args:
            concern_key: The YouCam concern key (e.g., 'acne', 'oiliness')
            scores: Complete scores dict from YouCam

        Returns:
            AIAnalysisResult dict or None if failed
        """
        if not self.enabled:
            return None

        try:
            prompt = create_concern_prompt(concern_key, scores)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                        "response_format": {"type": "json_object"},
                    },
                )

                if response.status_code != 200:
                    print(f"OpenAI API error: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON response
                analysis = json.loads(content)

                # Validate required fields
                return {
                    "quantitative": analysis.get("quantitative", ""),
                    "precautions": analysis.get("precautions", ""),
                    "recommendations": analysis.get("recommendations", []),
                    "root_cause": analysis.get("root_cause", ""),
                    "lifestyle_tips": analysis.get("lifestyle_tips", []),
                    "product_ingredients": analysis.get("product_ingredients", []),
                }

        except Exception as e:
            print(f"AI analysis error for {concern_key}: {e}")
            return None

    async def generate_all_analyses(self, scores: dict) -> dict[str, AIAnalysisResult]:
        """
        Generate AI analyses for all available concerns.
        No fallback - returns raw results for development debugging.

        Args:
            scores: Complete scores dict from YouCam

        Returns:
            Dict mapping concern keys to analysis results (empty if disabled)
        """
        import asyncio

        results = {}
        concern_keys = [k for k in CONCERN_NAMES.keys() if k in scores]

        if not self.enabled:
            # AI disabled - return empty dict (no fallback)
            print(
                "AI Analysis is disabled. Set AI_ANALYSIS_ENABLED=true and provide OPENAI_API_KEY."
            )
            return results

        # Generate AI analyses in parallel
        async def process_concern(key: str):
            ai_result = await self.generate_analysis(key, scores)
            # No fallback - return raw result (could be None)
            return key, ai_result

        # Execute all analyses in parallel
        tasks = [process_concern(key) for key in concern_keys]
        completed = await asyncio.gather(*tasks)

        for key, analysis in completed:
            if analysis is not None:
                results[key] = analysis
            # If analysis is None, key won't be in results (no fallback)

        return results


# Singleton instance
ai_analysis_service = AIAnalysisService()
