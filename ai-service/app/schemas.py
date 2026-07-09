from typing import Annotated, Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DetectLesionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    taskId: str | None = None
    bucket: str
    studyUid: str
    seriesUid: str
    dicomCtPath: str | None = None
    imageCount: int = Field(ge=1)
    bodyPart: str = ""
    currentSliceIndex: int = 0
    detectEngine: str = "scheme-a"
    detectMode: Annotated[
        str,
        Field(default="series", validation_alias=AliasChoices("detectMode", "detect_mode")),
    ] = "series"
    singleSlice: Annotated[
        bool,
        Field(default=False, validation_alias=AliasChoices("singleSlice", "single_slice")),
    ] = False
    sliceIndex: int | None = None
    # 方案 B 子引擎选择：auto(自动优先级) / monai(强制MONAI) / nndet(强制nnDetection)
    detectSubEngine: Annotated[
        str,
        Field(
            default="auto",
            validation_alias=AliasChoices("detectSubEngine", "detect_sub_engine"),
        ),
    ] = "auto"
    # 可选：配对增强 CT 序列（用于 ΔHU 分析，7-P2-01）
    enhancedSeriesUid: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("enhancedSeriesUid", "enhanced_series_uid"),
        ),
    ] = None
    enhancedImageCount: Annotated[
        int | None,
        Field(
            default=None,
            ge=1,
            validation_alias=AliasChoices("enhancedImageCount", "enhanced_image_count"),
        ),
    ] = None


class Bbox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Lesion(BaseModel):
    id: str
    label: str
    type: str
    confidence: float
    sliceIndex: int
    bbox: Bbox
    contour: Optional[List[Dict[str, float]]] = None
    diameterMm: float
    longAxisMm: float
    shortAxisMm: float
    areaMm2: float
    volumeMm3: Optional[float] = None
    hu: Optional[float] = None
    huMin: Optional[float] = None
    huMax: Optional[float] = None
    huMean: Optional[float] = None
    subType: Optional[str] = None
    markerType: Optional[str] = None
    colorKey: Optional[str] = None
    detectionConfidence: Optional[float] = None
    classificationConfidence: Optional[float] = None
    source: Optional[str] = None
    lobeLabel: Optional[str] = None
    positionHint: Optional[str] = None
    lobulationHint: Optional[str] = None
    spiculationHint: Optional[str] = None
    cavitationHint: Optional[str] = None
    morphology: Optional[Dict[str, Any]] = None
    detectionClass: Optional[str] = None
    detectionClassLabel: Optional[str] = None
    pleuralDistanceMm: Optional[float] = None
    pleuralHint: Optional[str] = None
    dlModelClass: Optional[str] = None
    deltaHu: Optional[float] = None
    enhancementHint: Optional[str] = None


class DetectLesionResponse(BaseModel):
    bodyPart: str
    studyUid: str
    seriesUid: str
    engine: str
    gpuAvailable: bool
    disclaimer: str
    lesions: List[Lesion]
    meta: Dict[str, Any] = Field(default_factory=dict)
