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
# UV TINT CONFIGURATION
# Konfigurasi efek UV-like untuk tampilan analisis profesional
# Terinspirasi dari alat analisis kecantikan UV seperti skin analyzers
# ============================================================================

UV_TINT_CONFIG = {
    "color": (0, 160, 170),  # Cyan/teal base color
    "opacity": 0.35,  # 35% opacity untuk mempertahankan detail wajah
    "blend_mode": "overlay",  # Mode blending
}


def _apply_uv_tint(image: Image.Image, config: dict = None) -> Image.Image:
    """
    Terapkan efek UV tint pada gambar untuk tampilan analisis profesional.

    Efek ini memberikan warna cyan/teal yang khas dari alat analisis
    kecantikan UV, membuat gambar terlihat seperti di bawah lampu UV.

    Args:
        image: PIL Image dalam mode RGBA
        config: Optional config dict dengan keys 'color', 'opacity', 'blend_mode'

    Returns:
        PIL Image dengan UV tint applied
    """
    if config is None:
        config = UV_TINT_CONFIG

    color = config.get("color", (0, 160, 170))
    opacity = config.get("opacity", 0.35)

    width, height = image.size

    # Pastikan image dalam mode RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # Buat tint layer dengan opacity
    alpha_value = int(255 * opacity)
    tint_layer = Image.new("RGBA", (width, height), (*color, alpha_value))

    # Blend menggunakan alpha composite
    # Untuk efek yang lebih natural, kita multiply warna
    result = image.copy()
    img_array = np.array(result, dtype=np.float32)
    tint_array = np.array(tint_layer, dtype=np.float32)

    # Blend formula: result = original * (1 - tint_alpha) + tint * tint_alpha
    # Dengan sedikit boost pada channel cyan untuk efek UV
    tint_alpha = tint_array[:, :, 3:4] / 255.0

    # Apply tint dengan preserving luminance
    for i in range(3):  # RGB channels
        img_array[:, :, i] = (
            img_array[:, :, i] * (1 - tint_alpha[:, :, 0] * 0.6)
            + tint_array[:, :, i] * tint_alpha[:, :, 0] * 0.6
        )

    # Boost cyan/blue channels sedikit untuk efek UV
    img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.05, 0, 255)  # Green
    img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 1.08, 0, 255)  # Blue

    result = Image.fromarray(img_array.astype(np.uint8), mode="RGBA")

    return result


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
# VISUALIZATION STYLE MAPPING
# Menentukan tipe visualisasi per concern berdasarkan sifat kondisi kulit:
# - "dots": Kondisi point-based (lesi diskrit) - acne, pore, age_spot
# - "boundary": Kondisi area-based (zona/region) - oiliness, wrinkle, dll
# ============================================================================

VISUALIZATION_STYLE_MAPPING = {
    # Point-based concerns → DOT visualization
    # Kondisi yang manifest sebagai spot/titik individual
    "acne": "dots",  # Papul, pustul, komedo adalah lesi diskrit
    "pore": "dots",  # Pori adalah bukaan folikel individual
    "age_spot": "dots",  # Bintik hiperpigmentasi adalah spot diskrit
    # Area-based concerns → BOUNDARY visualization
    # Kondisi yang mempengaruhi zona/region kulit
    "oiliness": "boundary",  # T-zone oiliness adalah AREA
    "wrinkle": "boundary",  # Kerutan adalah fitur LINEAR
    "dark_circle": "boundary",  # Lingkaran hitam adalah AREA bawah mata
    "eye_bag": "boundary",  # Kantung mata adalah region
    "redness": "boundary",  # Kemerahan menyebar di area
    "firmness": "boundary",  # Properti regional kulit
    "radiance": "boundary",  # Properti regional kulit
    "texture": "boundary",  # Properti regional kulit
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
# UPDATED: Warna dioptimalkan untuk kontras dengan UV tint cyan/teal
# Menggunakan pink/coral/magenta untuk concerns yang terlihat jelas di UV
SEVERITY_COLOR_LEVELS = {
    # Oiliness/Sebum - 2 levels (Baumann Skin Typing)
    # Reference: Baumann LS. The Baumann Skin Typing System. Dermatol Clin. 2008
    # UV-optimized: Pink/coral kontras dengan cyan background
    "oiliness": [
        (255, 180, 120),  # #ffb478 - Zona berminyak (score >= 50) - light coral
        (255, 120, 150),  # #ff7896 - Sangat berminyak (score < 50) - pink/coral
    ],
    # Pore - 3 levels (Clinical pore assessment)
    # Reference: Flament F, et al. Skin Res Technol. 2015 - Facial pore assessment
    # UV-optimized: Light cyan → orange → pink progression
    "pore": [
        (120, 220, 255),  # #78dcff - Pori tersumbat (mild, score >= 66) - light cyan
        (255, 180, 140),  # #ffb48c - Pori membesar (moderate, 33-65) - peach
        (255, 100, 130),  # #ff6482 - Area berminyak (severe, < 33) - coral pink
    ],
    # Wrinkle - 3 levels (Modified Glogau Scale simplified)
    # Reference: Glogau RG. Aesthetic classification of photoaging. Dermatol Clin. 1991
    # UV-optimized: Cyan → magenta → red-pink
    "wrinkle": [
        (100, 200, 255),  # #64c8ff - Garis halus (Type I-II, score >= 66) - sky blue
        (200, 100, 220),  # #c864dc - Kerutan sedang (Type II-III, 33-65) - magenta
        (255, 80, 120),  # #ff5078 - Kerutan dalam (Type III-IV, < 33) - hot pink
    ],
    # Acne - 3 levels (Global Acne Grading System simplified)
    # Reference: Doshi A, et al. J Am Acad Dermatol. 1997 - Global Acne Grading System
    # UV-optimized: Pink spectrum untuk visibility tinggi
    "acne": [
        (255, 200, 180),  # #ffc8b4 - Bekas jerawat (mild, score >= 66) - light peach
        (255, 140, 160),  # #ff8ca0 - Area meradang (moderate, 33-65) - salmon pink
        (255, 80, 100),  # #ff5064 - Jerawat aktif (severe, < 33) - coral red
    ],
    # Age spot/Flek - 4 levels (Pigmentation severity scale)
    # Reference: Nouveau S, et al. Br J Dermatol. 2019 - Facial hyperpigmentation
    # UV-optimized: Cyan → peach → coral → deep pink
    "age_spot": [
        (140, 220, 255),  # #8cdcff - Titik ringan (minimal, score >= 75) - light cyan
        (255, 180, 150),  # #ffb496 - Bintik-bintik (mild, 50-74) - peach
        (255, 130, 130),  # #ff8282 - Melasma (moderate, 25-49) - salmon
        (255, 90, 120),  # #ff5a78 - Bintik dewasa (severe, < 25) - coral pink
    ],
    # Dark circle - 3 levels (Periorbital hyperpigmentation classification)
    # Reference: Huang YL, et al. Int J Dermatol. 2014 - Dark eye circle classification
    # UV-optimized: Blue → purple → magenta
    "dark_circle": [
        (130, 150, 255),  # #8296ff - Vaskular (mild, score >= 66) - periwinkle
        (180, 100, 200),  # #b464c8 - Pigmentasi (moderate, 33-65) - orchid
        (220, 80, 160),  # #dc50a0 - Struktural (severe, < 33) - deep pink
    ],
    # Eye bag - sama dengan dark_circle
    "eye_bag": [
        (130, 150, 255),  # #8296ff - Ringan (score >= 66) - periwinkle
        (180, 100, 200),  # #b464c8 - Sedang (33-65) - orchid
        (220, 80, 160),  # #dc50a0 - Berat (< 33) - deep pink
    ],
    # Redness - 3 levels (Erythema severity scale)
    # Reference: Tan J, et al. J Drugs Dermatol. 2017 - Rosacea grading
    # UV-optimized: Pink/red tones yang kontras dengan cyan
    "redness": [
        (255, 150, 170),  # #ff96aa - Kemerahan ringan (score >= 66) - light pink
        (255, 100, 130),  # #ff6482 - Kemerahan sedang (33-65) - coral
        (255, 60, 100),  # #ff3c64 - Kemerahan tinggi (< 33) - hot pink/red
    ],
    # Firmness - 3 levels (Skin laxity assessment)
    # Reference: Fabi S, Sundaram H. J Drugs Dermatol. 2014 - Skin quality assessment
    # UV-optimized: Cyan → peach → pink
    "firmness": [
        (100, 220, 240),  # #64dcf0 - Elastisitas baik (score >= 66) - aqua
        (255, 180, 140),  # #ffb48c - Penurunan ringan (33-65) - peach
        (255, 100, 140),  # #ff648c - Perlu perhatian (< 33) - coral pink
    ],
    # Radiance/Warna kulit - 3 levels
    # Reference: Jiang ZX, et al. Skin Res Technol. 2016 - Skin radiance measurement
    # UV-optimized: Light tones → neutral → pink-gray
    "radiance": [
        (255, 240, 180),  # #fff0b4 - Area cerah (score >= 66) - cream yellow
        (200, 180, 200),  # #c8b4c8 - Kusam (33-65) - lavender gray
        (180, 140, 180),  # #b48cb4 - Sangat kusam (< 33) - dusty pink
    ],
    # Texture - 3 levels
    # UV-optimized: Cyan → purple → magenta
    "texture": [
        (120, 200, 255),  # #78c8ff - Tekstur halus (score >= 66) - sky blue
        (180, 120, 220),  # #b478dc - Tekstur kasar (33-65) - purple
        (255, 100, 160),  # #ff64a0 - Tekstur sangat kasar (< 33) - hot pink
    ],
}

# Threshold untuk menentukan severity level berdasarkan jumlah level
# Format: list of thresholds, len = num_levels - 1
SEVERITY_THRESHOLDS = {
    2: [50],  # 2 levels: >= 50 = level 0, < 50 = level 1
    3: [66, 33],  # 3 levels: >= 66 = 0, 33-65 = 1, < 33 = 2
    4: [75, 50, 25],  # 4 levels: >= 75 = 0, 50-74 = 1, 25-49 = 2, < 25 = 3
}

# Fallback: single color untuk backward compatibility
# UPDATED: Warna dioptimalkan untuk UV tint (pink/coral tones)
CONCERN_COLORS = {
    "oiliness": (255, 150, 135),  # Coral - kontras dengan cyan
    "acne": (255, 110, 130),  # Pink coral
    "pore": (255, 140, 165),  # Salmon pink
    "wrinkle": (200, 100, 220),  # Magenta - kontras dengan cyan
    "dark_circle": (180, 100, 200),  # Orchid
    "eye_bag": (180, 100, 200),  # Orchid - sama dengan dark_circle
    "age_spot": (255, 150, 150),  # Salmon - kontras dengan cyan
    "redness": (255, 100, 130),  # Coral pink
    "firmness": (255, 140, 165),  # Salmon pink
    "radiance": (200, 180, 200),  # Lavender gray
    "texture": (180, 120, 220),  # Purple
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


def calculate_dot_radius(width: int, height: int, severity_level: int, num_levels: int) -> int:
    """
    Hitung radius dot berdasarkan ukuran gambar dan severity level.

    Args:
        width: Lebar gambar dalam pixel
        height: Tinggi gambar dalam pixel
        severity_level: Level severity (0 = mild, higher = more severe)
        num_levels: Total jumlah level untuk concern ini

    Returns:
        Radius dot dalam pixel

    Formula:
        base_radius = 0.5% dari dimensi terkecil gambar (min 3px)
        severity_multiplier = 1.0 (mild) hingga 2.0 (severe)
    """
    # Base radius: 0.5% dari dimensi terkecil, minimum 3px
    base_radius = max(3, int(min(width, height) * 0.005))

    # Severity multiplier: mild=1.0, moderate=1.5, severe=2.0
    if num_levels <= 1:
        multiplier = 1.0
    else:
        # Linear interpolation dari 1.0 ke 2.0 berdasarkan severity
        multiplier = 1.0 + (severity_level / (num_levels - 1)) * 1.0

    return int(base_radius * multiplier)


def get_dot_alpha(severity_level: int, num_levels: int) -> int:
    """
    Hitung alpha (opacity) dot berdasarkan severity level.

    Args:
        severity_level: Level severity (0 = mild, higher = more severe)
        num_levels: Total jumlah level untuk concern ini

    Returns:
        Alpha value (0-255)

    Mapping:
        - Mild (level 0): alpha 180
        - Moderate: alpha 210
        - Severe (max level): alpha 255
    """
    if num_levels <= 1:
        return 220

    # Linear interpolation dari 180 ke 255
    alpha_range = 255 - 180  # 75
    alpha = 180 + int((severity_level / (num_levels - 1)) * alpha_range)
    return min(255, alpha)


def draw_severity_dots(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    color: tuple[int, int, int],
    width: int,
    height: int,
    severity_level: int,
    num_levels: int,
) -> None:
    """
    Gambar dots pada titik-titik landmark dengan ukuran berdasarkan severity.

    Args:
        draw: PIL ImageDraw object
        points: List of (x, y) koordinat landmark
        color: RGB tuple warna dot
        width: Lebar gambar
        height: Tinggi gambar
        severity_level: Level severity untuk sizing
        num_levels: Total jumlah level
    """
    radius = calculate_dot_radius(width, height, severity_level, num_levels)
    alpha = get_dot_alpha(severity_level, num_levels)

    for x, y in points:
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill=(*color, alpha),
        )


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

        # Apply UV tint untuk efek analisis profesional (cyan/teal base)
        original_with_uv = _apply_uv_tint(original)

        if landmark_result.status == LandmarkStatus.FAILED:
            # Fallback: gunakan mask saja jika ada (dengan UV tint)
            if mask_bytes:
                status["fallback_used"] = True
                status["visualization_source"] = "mask_only"
                return self._apply_mask_only(original_with_uv, mask_bytes, concern_key, score), status
            else:
                # Return UV-tinted image dengan status failed
                output = io.BytesIO()
                original_with_uv.convert("RGB").save(output, format="JPEG", quality=95)
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

            # Tentukan visualization style berdasarkan concern type
            viz_style = VISUALIZATION_STYLE_MAPPING.get(concern_key, "boundary")
            num_levels = len(SEVERITY_COLOR_LEVELS.get(concern_key, [None]))
            current_severity = severity_level if severity_level is not None else 0

            if viz_style == "dots":
                # DOT visualization untuk point-based concerns (acne, pore, age_spot)
                # Hanya gambar dots, tanpa lines
                draw_severity_dots(
                    draw=draw,
                    points=points,
                    color=color,
                    width=width,
                    height=height,
                    severity_level=current_severity,
                    num_levels=num_levels,
                )
            elif style == "canny":
                # BOUNDARY visualization dengan canny style: outline dengan dots
                draw.line(points + [points[0]], fill=(*color, 200), width=2)

                # Draw small dots pada setiap landmark
                for x, y in points:
                    draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=(*color, 255))
            else:
                # Filled style: polygon semi-transparan
                draw.polygon(points, fill=(*color, 60), outline=(*color, 180))

        # Tambahkan intensity dots jika ada mask (using severity color)
        if mask_bytes:
            overlay = self._add_intensity_dots(overlay, mask_bytes, landmarks, color)

        # Composite overlay dengan UV-tinted original
        result = Image.alpha_composite(original_with_uv, overlay)

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
        """Tambahkan intensity dots berdasarkan mask dengan dynamic sizing."""
        draw = ImageDraw.Draw(overlay)
        width, height = overlay.size

        # Base radius berdasarkan ukuran gambar (konsisten dengan draw_severity_dots)
        base_radius = max(2, int(min(width, height) * 0.004))

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
                        # Ukuran dot berdasarkan intensity (scaled by base_radius)
                        intensity_multiplier = 1.0 + (intensity / 255.0)
                        radius = max(base_radius, int(base_radius * intensity_multiplier))
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
