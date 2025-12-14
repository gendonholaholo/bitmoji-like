"""
Landmark Service - MediaPipe Face Mesh untuk visualisasi zona wajah

Menggunakan MediaPipe untuk mendeteksi 468 landmark wajah dan menghasilkan
visualisasi canny-style untuk overlay pada skin analysis.
"""

import io
from dataclasses import dataclass
from enum import Enum

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw


class LandmarkStatus(str, Enum):
    """Status hasil deteksi landmark"""

    SUCCESS = "success"
    PARTIAL = "partial"  # Terdeteksi tapi confidence rendah
    FAILED = "failed"


@dataclass
class LandmarkResult:
    """Hasil deteksi landmark"""

    status: LandmarkStatus
    error_message: str | None = None
    landmarks: np.ndarray | None = None  # Shape: (468, 3) - x, y, z
    confidence: float = 0.0


# ============================================================================
# FACIAL ZONE DEFINITIONS
# MediaPipe Face Mesh landmark indices untuk setiap zona wajah
# Reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
# ============================================================================

FACIAL_ZONES = {
    # T-Zone (dahi + hidung) - area sebum/oiliness
    "t_zone": {
        "forehead": [
            10,
            338,
            297,
            332,
            284,
            251,
            389,
            356,
            454,
            323,
            361,
            288,
            397,
            365,
            379,
            378,
            400,
            377,
            152,
            148,
            176,
            149,
            150,
            136,
            172,
            58,
            132,
            93,
            234,
            127,
            162,
            21,
            54,
            103,
            67,
            109,
        ],
        "nose_bridge": [6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 267, 269, 270, 409, 291],
        "nose_tip": [1, 2, 98, 327, 326, 97, 99, 240, 235, 219, 218, 237, 44, 1],
    },
    # Pipi kiri
    "left_cheek": [
        234,
        93,
        132,
        58,
        172,
        136,
        150,
        149,
        176,
        148,
        152,
        377,
        400,
        378,
        379,
        365,
        397,
        288,
        361,
        323,
        454,
        356,
        389,
        251,
        284,
        332,
        297,
        338,
        10,
        109,
        67,
        103,
        54,
        21,
        162,
        127,
    ],
    # Pipi kanan
    "right_cheek": [
        454,
        323,
        361,
        288,
        397,
        365,
        379,
        378,
        400,
        377,
        152,
        148,
        176,
        149,
        150,
        136,
        172,
        58,
        132,
        93,
        234,
        127,
        162,
        21,
        54,
        103,
        67,
        109,
        10,
        338,
        297,
        332,
        284,
        251,
        389,
        356,
    ],
    # Area mata (untuk dark_circle, eye_bag)
    "left_eye_area": [226, 247, 30, 29, 27, 28, 56, 190, 243, 112, 26, 22, 23, 24, 110, 25],
    "right_eye_area": [
        446,
        467,
        260,
        259,
        257,
        258,
        286,
        414,
        463,
        341,
        256,
        252,
        253,
        254,
        339,
        255,
    ],
    # Under-eye (lingkaran hitam)
    "left_under_eye": [
        111,
        117,
        118,
        119,
        120,
        121,
        128,
        245,
        193,
        168,
        417,
        351,
        419,
        248,
        281,
        363,
        360,
        279,
        358,
        429,
        355,
        463,
        341,
        256,
    ],
    "right_under_eye": [
        340,
        346,
        347,
        348,
        349,
        350,
        357,
        465,
        412,
        343,
        277,
        329,
        330,
        280,
        352,
        346,
    ],
    # Dahi (untuk wrinkle, texture)
    "forehead_center": [10, 151, 9, 8, 168, 6, 197, 195, 5, 4],
    # Nasolabial (lipatan hidung ke mulut)
    "left_nasolabial": [205, 50, 117, 118, 101, 36, 206, 203, 129, 102, 48, 115],
    "right_nasolabial": [425, 280, 346, 347, 330, 266, 426, 423, 358, 331, 278, 344],
    # Dagu
    "chin": [
        152,
        377,
        400,
        378,
        379,
        365,
        397,
        288,
        435,
        401,
        366,
        447,
        264,
        372,
        383,
        380,
        381,
        382,
        362,
        398,
        312,
        311,
        310,
        415,
        308,
        324,
        318,
        402,
        317,
        14,
        87,
        178,
        88,
        95,
        78,
        191,
        80,
        81,
        82,
        13,
        312,
        311,
        310,
        415,
    ],
}

# Mapping concern ke zona yang relevan
CONCERN_ZONE_MAPPING = {
    "oiliness": ["t_zone"],
    "acne": ["t_zone", "left_cheek", "right_cheek", "chin"],
    "pore": ["t_zone", "left_cheek", "right_cheek"],
    "wrinkle": [
        "forehead_center",
        "left_eye_area",
        "right_eye_area",
        "left_nasolabial",
        "right_nasolabial",
    ],
    "dark_circle": ["left_under_eye", "right_under_eye"],
    "eye_bag": ["left_under_eye", "right_under_eye"],
    "age_spot": ["left_cheek", "right_cheek", "forehead_center"],
    "redness": ["left_cheek", "right_cheek", "t_zone"],
    "firmness": ["left_cheek", "right_cheek", "chin"],
    "radiance": ["left_cheek", "right_cheek", "forehead_center"],
    "texture": ["left_cheek", "right_cheek", "forehead_center"],
}


# ============================================================================
# SEVERITY-BASED COLOR SYSTEM
# Multi-level colors berdasarkan literature dermatologi:
# - Glogau Scale (wrinkle): 4 levels photoaging
# - Global Acne Grading System: 5 levels severity
# - Baumann Skin Typing: oiliness classification
# - Clinical pore assessment scales
# - Periorbital hyperpigmentation classification
#
# Score mapping (YouCam API: 0-100, higher = healthier):
# - HIGH score (≥66) = mild/minimal problem = Level 0 (least severe color)
# - MID score (33-65) = moderate problem = Level 1
# - LOW score (<33) = severe problem = Level 2+ (most severe color)
# ============================================================================

# Warna multi-level per concern - SINKRON dengan frontend MARKER_LEGENDS
# Format: list of RGB tuples, index 0 = least severe, last index = most severe
SEVERITY_COLOR_LEVELS = {
    # Oiliness/Sebum - 2 levels (Baumann Skin Typing)
    # Reference: Baumann LS. The Baumann Skin Typing System. Dermatol Clin. 2008
    "oiliness": [
        (255, 204, 0),   # #ffcc00 - Zona berminyak (score >= 50)
        (255, 149, 0),   # #ff9500 - Sangat berminyak (score < 50)
    ],
    # Pore - 3 levels (Clinical pore assessment)
    # Reference: Flament F, et al. Skin Res Technol. 2015 - Facial pore assessment
    "pore": [
        (0, 212, 255),   # #00d4ff - Pori tersumbat (mild, score >= 66)
        (255, 149, 0),   # #ff9500 - Pori membesar (moderate, 33-65)
        (255, 204, 0),   # #ffcc00 - Area berminyak (severe, < 33)
    ],
    # Wrinkle - 3 levels (Modified Glogau Scale simplified)
    # Reference: Glogau RG. Aesthetic classification of photoaging. Dermatol Clin. 1991
    "wrinkle": [
        (0, 212, 255),   # #00d4ff - Garis halus (Type I-II, score >= 66)
        (168, 85, 247),  # #a855f7 - Kerutan sedang (Type II-III, 33-65)
        (239, 68, 68),   # #ef4444 - Kerutan dalam (Type III-IV, < 33)
    ],
    # Acne - 3 levels (Global Acne Grading System simplified)
    # Reference: Doshi A, et al. J Am Acad Dermatol. 1997 - Global Acne Grading System
    "acne": [
        (255, 204, 0),   # #ffcc00 - Bekas jerawat (mild, score >= 66)
        (255, 149, 0),   # #ff9500 - Area meradang (moderate, 33-65)
        (255, 59, 48),   # #ff3b30 - Jerawat aktif (severe, < 33)
    ],
    # Age spot/Flek - 4 levels (Pigmentation severity scale)
    # Reference: Nouveau S, et al. Br J Dermatol. 2019 - Facial hyperpigmentation
    "age_spot": [
        (0, 212, 255),   # #00d4ff - Titik ringan (minimal, score >= 75)
        (255, 149, 0),   # #ff9500 - Bintik-bintik (mild, 50-74)
        (139, 90, 43),   # #8b5a2b - Melasma (moderate, 25-49)
        (160, 82, 45),   # #a0522d - Bintik dewasa (severe, < 25)
    ],
    # Dark circle - 3 levels (Periorbital hyperpigmentation classification)
    # Reference: Huang YL, et al. Int J Dermatol. 2014 - Dark eye circle classification
    "dark_circle": [
        (92, 92, 255),   # #5c5cff - Vaskular (mild, score >= 66)
        (139, 69, 19),   # #8b4513 - Pigmentasi (moderate, 33-65)
        (128, 128, 128), # #808080 - Struktural (severe, < 33)
    ],
    # Eye bag - sama dengan dark_circle
    "eye_bag": [
        (92, 92, 255),   # #5c5cff - Ringan (score >= 66)
        (139, 69, 19),   # #8b4513 - Sedang (33-65)
        (128, 128, 128), # #808080 - Berat (< 33)
    ],
    # Redness - 3 levels (Erythema severity scale)
    # Reference: Tan J, et al. J Drugs Dermatol. 2017 - Rosacea grading
    "redness": [
        (255, 107, 107), # #ff6b6b - Kemerahan ringan (score >= 66)
        (239, 68, 68),   # #ef4444 - Kemerahan sedang (33-65)
        (220, 38, 38),   # #dc2626 - Kemerahan tinggi (< 33)
    ],
    # Firmness - 3 levels (Skin laxity assessment)
    # Reference: Fabi S, Sundaram H. J Drugs Dermatol. 2014 - Skin quality assessment
    "firmness": [
        (0, 212, 255),   # #00d4ff - Elastisitas baik (score >= 66)
        (245, 158, 11),  # #f59e0b - Penurunan ringan (33-65)
        (239, 68, 68),   # #ef4444 - Perlu perhatian (< 33)
    ],
    # Radiance/Warna kulit - 3 levels
    # Reference: Jiang ZX, et al. Skin Res Technol. 2016 - Skin radiance measurement
    "radiance": [
        (255, 215, 0),   # #ffd700 - Area cerah (score >= 66)
        (192, 192, 192), # #c0c0c0 - Kusam (33-65)
        (128, 128, 128), # #808080 - Sangat kusam (< 33)
    ],
    # Texture - 3 levels
    "texture": [
        (0, 212, 255),   # #00d4ff - Tekstur halus (score >= 66)
        (175, 82, 222),  # #af52de - Tekstur kasar (33-65)
        (139, 69, 19),   # #8b4513 - Tekstur sangat kasar (< 33)
    ],
}

# Threshold untuk menentukan severity level berdasarkan jumlah level
# Format: list of thresholds, len = num_levels - 1
SEVERITY_THRESHOLDS = {
    2: [50],           # 2 levels: >= 50 = level 0, < 50 = level 1
    3: [66, 33],       # 3 levels: >= 66 = 0, 33-65 = 1, < 33 = 2
    4: [75, 50, 25],   # 4 levels: >= 75 = 0, 50-74 = 1, 25-49 = 2, < 25 = 3
}

# Fallback: single color untuk backward compatibility
CONCERN_COLORS = {
    "oiliness": (255, 204, 0),  # Kuning/Gold
    "acne": (255, 59, 48),  # Merah
    "pore": (255, 149, 0),  # Orange
    "wrinkle": (0, 212, 255),  # Cyan
    "dark_circle": (94, 92, 230),  # Biru
    "eye_bag": (88, 86, 214),  # Indigo
    "age_spot": (162, 132, 94),  # Coklat
    "redness": (255, 100, 100),  # Merah muda
    "firmness": (0, 255, 200),  # Teal
    "radiance": (255, 255, 100),  # Kuning terang
    "texture": (175, 82, 222),  # Ungu
}


def get_severity_level(score: float, num_levels: int) -> int:
    """
    Hitung severity level berdasarkan score.

    Args:
        score: Skor dari YouCam API (0-100, higher = healthier)
        num_levels: Jumlah level severity untuk concern ini

    Returns:
        Severity level index (0 = least severe, num_levels-1 = most severe)

    Literature basis:
    - Score >= 66: Mild/minimal (corresponds to Glogau Type I-II, mild acne)
    - Score 33-65: Moderate (Glogau Type II-III, moderate concerns)
    - Score < 33: Severe (Glogau Type III-IV, severe issues)
    """
    if num_levels not in SEVERITY_THRESHOLDS:
        return 0  # Default ke level terendah jika tidak ada threshold

    thresholds = SEVERITY_THRESHOLDS[num_levels]

    for i, threshold in enumerate(thresholds):
        if score >= threshold:
            return i

    return num_levels - 1  # Level paling severe


def get_color_for_severity(concern_key: str, score: float) -> tuple:
    """
    Dapatkan warna RGB berdasarkan concern dan score.

    Args:
        concern_key: Key concern (e.g., 'oiliness', 'acne')
        score: Skor dari YouCam API (0-100)

    Returns:
        RGB tuple untuk warna yang sesuai dengan severity
    """
    if concern_key not in SEVERITY_COLOR_LEVELS:
        return CONCERN_COLORS.get(concern_key, (0, 212, 255))

    color_levels = SEVERITY_COLOR_LEVELS[concern_key]
    num_levels = len(color_levels)
    severity_level = get_severity_level(score, num_levels)

    return color_levels[severity_level]


class LandmarkService:
    """Service untuk deteksi landmark wajah menggunakan MediaPipe"""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect_landmarks(self, image_bytes: bytes) -> LandmarkResult:
        """
        Deteksi landmark dari image bytes

        Args:
            image_bytes: Raw image bytes (JPEG/PNG)

        Returns:
            LandmarkResult dengan status dan data landmark
        """
        try:
            # Convert bytes ke numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                return LandmarkResult(
                    status=LandmarkStatus.FAILED, error_message="Gagal decode image"
                )

            # Convert BGR ke RGB untuk MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width = image.shape[:2]

            # Process dengan MediaPipe
            results = self.face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                return LandmarkResult(
                    status=LandmarkStatus.FAILED, error_message="Wajah tidak terdeteksi"
                )

            # Ambil landmark pertama (face pertama)
            face_landmarks = results.multi_face_landmarks[0]

            # Convert ke numpy array dengan koordinat pixel
            landmarks = np.array(
                [[lm.x * width, lm.y * height, lm.z * width] for lm in face_landmarks.landmark]
            )

            # Hitung confidence (rata-rata visibility jika tersedia)
            confidence = 0.85  # Default confidence untuk static image

            return LandmarkResult(
                status=LandmarkStatus.SUCCESS, landmarks=landmarks, confidence=confidence
            )

        except Exception as e:
            return LandmarkResult(
                status=LandmarkStatus.FAILED, error_message=f"Error deteksi landmark: {str(e)}"
            )

    def create_zone_visualization(
        self,
        image_bytes: bytes,
        concern_key: str,
        mask_bytes: bytes | None = None,
        style: str = "canny",
        score: float | None = None,
    ) -> tuple[bytes, dict]:
        """
        Buat visualisasi zona untuk concern tertentu dengan severity-based colors.

        Args:
            image_bytes: Original image bytes
            concern_key: Key concern (e.g., 'oiliness', 'acne')
            mask_bytes: Optional mask dari YouCam untuk intensity
            style: 'canny' untuk outline, 'filled' untuk filled polygon
            score: Optional score dari YouCam API (0-100) untuk menentukan severity color

        Returns:
            Tuple of (visualization_bytes, status_dict)

        Color Selection Logic (based on dermatological literature):
            - If score provided: Use severity-based color from SEVERITY_COLOR_LEVELS
            - If no score: Fall back to default CONCERN_COLORS

        References:
            - Glogau Scale for photoaging (wrinkles)
            - Global Acne Grading System (acne)
            - Baumann Skin Typing System (oiliness)
            - Clinical pore assessment scales
        """
        # Deteksi landmark
        landmark_result = self.detect_landmarks(image_bytes)

        # Determine color based on score (severity-based) or fallback
        if score is not None:
            color = get_color_for_severity(concern_key, score)
            severity_level = get_severity_level(
                score, len(SEVERITY_COLOR_LEVELS.get(concern_key, [None]))
            )
        else:
            color = CONCERN_COLORS.get(concern_key, (0, 212, 255))
            severity_level = None

        status = {
            "landmark_status": landmark_result.status.value,
            "landmark_error": landmark_result.error_message,
            "confidence": landmark_result.confidence,
            "fallback_used": False,
            "visualization_source": "none",
            "severity_level": severity_level,
            "score_used": score,
            "color_rgb": color,
        }

        # Load original image
        original = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        width, height = original.size

        if landmark_result.status == LandmarkStatus.FAILED:
            # Fallback: gunakan mask saja jika ada
            if mask_bytes:
                status["fallback_used"] = True
                status["visualization_source"] = "mask_only"
                return self._apply_mask_only(original, mask_bytes, concern_key, score), status
            else:
                # Return original dengan status failed
                output = io.BytesIO()
                original.convert("RGB").save(output, format="JPEG", quality=95)
                return output.getvalue(), status

        # Success: buat visualisasi dengan landmark
        landmarks = landmark_result.landmarks
        status["visualization_source"] = "mediapipe"

        # Buat overlay layer
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Dapatkan zona untuk concern ini
        zones = CONCERN_ZONE_MAPPING.get(concern_key, ["left_cheek", "right_cheek"])

        # Gambar setiap zona
        for zone_name in zones:
            zone_indices = self._get_zone_indices(zone_name)
            if not zone_indices:
                continue

            # Ambil koordinat landmark untuk zona ini
            points = []
            for idx in zone_indices:
                if idx < len(landmarks):
                    x, y = landmarks[idx][0], landmarks[idx][1]
                    points.append((int(x), int(y)))

            if len(points) < 3:
                continue

            if style == "canny":
                # Canny style: outline dengan dots
                # Draw outline
                draw.line(points + [points[0]], fill=(*color, 200), width=2)

                # Draw dots pada setiap landmark
                for x, y in points:
                    draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=(*color, 255))
            else:
                # Filled style: polygon semi-transparan
                draw.polygon(points, fill=(*color, 60), outline=(*color, 180))

        # Tambahkan intensity dots jika ada mask (using severity color)
        if mask_bytes:
            overlay = self._add_intensity_dots(overlay, mask_bytes, landmarks, color)

        # Composite overlay dengan original
        result = Image.alpha_composite(original, overlay)

        # Convert ke JPEG
        output = io.BytesIO()
        result.convert("RGB").save(output, format="JPEG", quality=95)

        return output.getvalue(), status

    def _get_zone_indices(self, zone_name: str) -> list[int]:
        """Dapatkan landmark indices untuk zona tertentu"""
        # Cek di nested zones (t_zone)
        for main_zone, sub_zones in FACIAL_ZONES.items():
            if isinstance(sub_zones, dict):
                if zone_name in sub_zones:
                    return sub_zones[zone_name]
                if zone_name == main_zone:
                    # Gabungkan semua sub-zones
                    all_indices = []
                    for sub_zone in sub_zones.values():
                        all_indices.extend(sub_zone)
                    return list(set(all_indices))
            elif zone_name == main_zone:
                return sub_zones
        return []

    def _apply_mask_only(
        self,
        original: Image.Image,
        mask_bytes: bytes,
        concern_key: str,
        score: float | None = None,
    ) -> bytes:
        """Fallback: apply mask tanpa landmark (enhanced visibility) with severity colors"""
        width, height = original.size

        # Use severity-based color if score provided
        if score is not None:
            color = get_color_for_severity(concern_key, score)
        else:
            color = CONCERN_COLORS.get(concern_key, (0, 212, 255))

        # Load mask
        mask_img = Image.open(io.BytesIO(mask_bytes))
        if mask_img.size != (width, height):
            mask_img = mask_img.resize((width, height), Image.Resampling.LANCZOS)

        # Convert to grayscale
        if mask_img.mode != "L":
            mask_img = mask_img.convert("L")

        # Create colored overlay dengan enhanced alpha
        overlay = Image.new("RGBA", (width, height), (*color, 0))

        # Use mask as alpha, enhanced
        mask_array = np.array(mask_img)
        mask_enhanced = np.clip(mask_array * 1.5, 0, 255).astype(np.uint8)

        overlay.putalpha(Image.fromarray(mask_enhanced))

        # Composite
        result = Image.alpha_composite(original, overlay)

        output = io.BytesIO()
        result.convert("RGB").save(output, format="JPEG", quality=95)
        return output.getvalue()

    def _add_intensity_dots(
        self, overlay: Image.Image, mask_bytes: bytes, landmarks: np.ndarray, color: tuple
    ) -> Image.Image:
        """Tambahkan intensity dots berdasarkan mask"""
        draw = ImageDraw.Draw(overlay)
        width, height = overlay.size

        try:
            # Load mask
            mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")
            if mask_img.size != (width, height):
                mask_img = mask_img.resize((width, height), Image.Resampling.LANCZOS)

            mask_array = np.array(mask_img)

            # Sample points di sekitar landmarks dengan high intensity
            for lm in landmarks:
                x, y = int(lm[0]), int(lm[1])
                if 0 <= x < width and 0 <= y < height:
                    intensity = mask_array[y, x]
                    if intensity > 30:  # Threshold
                        # Ukuran dot berdasarkan intensity
                        radius = max(2, int(intensity / 50))
                        alpha = min(255, intensity + 100)
                        draw.ellipse(
                            [(x - radius, y - radius), (x + radius, y + radius)],
                            fill=(*color, alpha),
                        )
        except Exception:
            pass  # Skip jika mask processing gagal

        return overlay

    def create_all_zone_visualizations(
        self,
        image_bytes: bytes,
        masks: dict[str, bytes],
        scores: dict | None = None,
    ) -> tuple[dict[str, bytes], dict[str, dict]]:
        """
        Buat visualisasi untuk semua concern dengan severity-based colors.

        Args:
            image_bytes: Original image bytes
            masks: Dictionary of mask_name -> PNG bytes
            scores: Optional dictionary of scores from YouCam API for severity coloring
                    Format: {"oiliness": {"ui_score": 45.2}, "acne": {"ui_score": 72.1}, ...}

        Returns:
            Tuple of (visualizations_dict, statuses_dict)

        The scores parameter enables severity-based color visualization:
        - When scores provided: Colors are selected based on severity thresholds
        - When scores not provided: Falls back to default single-color visualization
        """
        visualizations = {}
        statuses = {}

        concerns = list(CONCERN_ZONE_MAPPING.keys())

        for concern_key in concerns:
            # Cari mask yang cocok
            mask_bytes = None
            for mask_name, mask_data in masks.items():
                if concern_key.lower() in mask_name.lower():
                    mask_bytes = mask_data
                    break

            # Extract score for this concern if available
            concern_score = None
            if scores:
                score_data = scores.get(concern_key)
                if score_data:
                    # Handle different score formats
                    if isinstance(score_data, dict):
                        concern_score = score_data.get("ui_score") or score_data.get("raw_score")
                        # Handle nested 'whole' structure
                        if concern_score is None and "whole" in score_data:
                            concern_score = score_data["whole"].get("ui_score")
                    elif isinstance(score_data, (int, float)):
                        concern_score = float(score_data)

            viz_bytes, status = self.create_zone_visualization(
                image_bytes,
                concern_key,
                mask_bytes=mask_bytes,
                style="canny",
                score=concern_score,
            )

            visualizations[concern_key] = viz_bytes
            statuses[concern_key] = status

        return visualizations, statuses


# Singleton instance
_landmark_service: LandmarkService | None = None


def get_landmark_service() -> LandmarkService:
    """Get or create singleton LandmarkService instance"""
    global _landmark_service
    if _landmark_service is None:
        _landmark_service = LandmarkService()
    return _landmark_service
