from pydantic import BaseModel


class ScoreDetail(BaseModel):
    """Individual score detail with mask reference"""

    raw_score: float
    ui_score: int
    output_mask_name: str


class SubcategoryScore(BaseModel):
    """Score with possible subcategories (for pore, wrinkle, etc.)"""

    forehead: ScoreDetail | None = None
    nose: ScoreDetail | None = None
    cheek: ScoreDetail | None = None
    glabellar: ScoreDetail | None = None
    crowfeet: ScoreDetail | None = None
    periocular: ScoreDetail | None = None
    nasolabial: ScoreDetail | None = None
    marionette: ScoreDetail | None = None
    whole: ScoreDetail | None = None


class OverallScore(BaseModel):
    """Overall skin score"""

    score: float


class SkinAnalysisScores(BaseModel):
    """Complete skin analysis scores from score_info.json"""

    # HD Skincare scores
    hd_redness: ScoreDetail | None = None
    hd_oiliness: ScoreDetail | None = None
    hd_age_spot: ScoreDetail | None = None
    hd_radiance: ScoreDetail | None = None
    hd_moisture: ScoreDetail | None = None
    hd_dark_circle: ScoreDetail | None = None
    hd_eye_bag: ScoreDetail | None = None
    hd_droopy_upper_eyelid: ScoreDetail | None = None
    hd_droopy_lower_eyelid: ScoreDetail | None = None
    hd_firmness: ScoreDetail | None = None
    hd_texture: SubcategoryScore | None = None
    hd_acne: SubcategoryScore | None = None
    hd_pore: SubcategoryScore | None = None
    hd_wrinkle: SubcategoryScore | None = None

    # SD Skincare scores
    wrinkle: ScoreDetail | None = None
    droopy_upper_eyelid: ScoreDetail | None = None
    droopy_lower_eyelid: ScoreDetail | None = None
    firmness: ScoreDetail | None = None
    acne: ScoreDetail | None = None
    moisture: ScoreDetail | None = None
    eye_bag: ScoreDetail | None = None
    dark_circle_v2: ScoreDetail | None = None
    age_spot: ScoreDetail | None = None
    radiance: ScoreDetail | None = None
    redness: ScoreDetail | None = None
    oiliness: ScoreDetail | None = None
    pore: ScoreDetail | None = None
    texture: ScoreDetail | None = None

    # Overall metrics
    all: OverallScore
    skin_age: int


class AnalysisResponse(BaseModel):
    """Response for skin analysis request"""

    task_id: str
    status: str = "processing"
    message: str = "Analysis started successfully"


class ResultResponse(BaseModel):
    """Response with complete analysis results"""

    task_id: str
    status: str
    scores: SkinAnalysisScores | None = None
    composite_image: str | None = None  # base64 encoded composite visualization
    masks: dict[str, str] | None = None  # mask_name -> base64 encoded image
    original_image: str | None = None  # base64 encoded original image
    error: str | None = None
    error_message: str | None = None
