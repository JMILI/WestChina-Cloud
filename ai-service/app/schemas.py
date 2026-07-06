from typing import Annotated, Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DetectLesionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

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


class DetectLesionResponse(BaseModel):
    bodyPart: str
    studyUid: str
    seriesUid: str
    engine: str
    gpuAvailable: bool
    disclaimer: str
    lesions: List[Lesion]
    meta: Dict[str, Any] = Field(default_factory=dict)
