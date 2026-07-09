import os


class Settings:
    host: str = os.getenv("AI_HOST", "0.0.0.0")
    port: int = int(os.getenv("AI_PORT", "9810"))

    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "admin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "admin123456")
    minio_secure: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"

    # 结节检测参数
    min_nodule_mm: float = float(os.getenv("MIN_NODULE_MM", "3"))
    max_nodule_mm: float = float(os.getenv("MAX_NODULE_MM", "30"))
    max_lesions: int = int(os.getenv("MAX_LESIONS", "12"))

    # 方案 A：候选区域筛选参数 — 双通道（GGO + 实性）
    ggo_hu_min: float = float(os.getenv("GGO_HU_MIN", "-750"))
    ggo_hu_max: float = float(os.getenv("GGO_HU_MAX", "-100"))
    solid_hu_min: float = float(os.getenv("SOLID_HU_MIN", "30"))
    solid_hu_max: float = float(os.getenv("SOLID_HU_MAX", "150"))
    volume_min_mm3: float = float(os.getenv("VOLUME_MIN_MM3", "15"))
    volume_max_mm3: float = float(os.getenv("VOLUME_MAX_MM3", "5000"))
    solidity_min: float = float(os.getenv("SOLIDITY_MIN", "0.7"))
    # 肺mask膨胀半径（体素），捕获胸膜下结节
    lung_dilate_radius: int = int(os.getenv("LUNG_DILATE_RADIUS", "1"))

    # P2: 血管/肺门抑制
    hilar_suppress_enabled: bool = os.getenv("HILAR_SUPPRESS_ENABLED", "true").lower() == "true"
    continuity_enabled: bool = os.getenv("CONTINUITY_ENABLED", "true").lower() == "true"
    continuity_min_slices: int = int(os.getenv("CONTINUITY_MIN_SLICES", "2"))

    # 日志
    ai_log_json: bool = os.getenv("AI_LOG_JSON", "true").lower() == "true"
    ai_log_path: str = os.getenv("AI_LOG_PATH", "")  # 默认见 log_paths.ai_log_file()

    # CPU 全序列：超过该层数时均匀降采样（GPU 可用时不限制）
    series_max_slices_cpu: int = int(os.getenv("SERIES_MAX_SLICES_CPU", "128"))

    # scheme-b 融合分析（肺分割 + MONAI）最长等待时间（秒），默认 2 小时
    fusion_timeout_sec: int = int(os.getenv("AI_FUSION_TIMEOUT_SEC", "7200"))

    # 方案 B P1：融合过滤与降采样
    scheme_b_vessel_iou_max: float = float(os.getenv("SCHEME_B_VESSEL_IOU_MAX", "0.35"))
    scheme_b_solidity_min: float = float(os.getenv("SCHEME_B_SOLIDITY_MIN", "0.55"))
    scheme_b_ggo_solidity_min: float = float(os.getenv("SCHEME_B_GGO_SOLIDITY_MIN", "0.35"))
    scheme_b_sphericity_min: float = float(os.getenv("SCHEME_B_SPHERICITY_MIN", "0.35"))
    scheme_b_hu_stddev_max: float = float(os.getenv("SCHEME_B_HU_STDDEV_MAX", "80"))
    scheme_b_ggo_hu_stddev_max: float = float(os.getenv("SCHEME_B_GGO_HU_STDDEV_MAX", "120"))
    scheme_b_hilar_downweight_enabled: bool = (
        os.getenv("SCHEME_B_HILAR_DOWNWEIGHT", "true").lower() == "true"
    )
    scheme_b_hilar_conf_factor: float = float(os.getenv("SCHEME_B_HILAR_CONF_FACTOR", "0.6"))
    scheme_b_low_conf_min: float = float(os.getenv("SCHEME_B_LOW_CONF_MIN", "0.01"))
    scheme_b_low_conf_max: float = float(os.getenv("SCHEME_B_LOW_CONF_MAX", "0.05"))
    scheme_b_monai_max_z: int = int(os.getenv("SCHEME_B_MONAI_MAX_Z", "150"))
    scheme_b_hu_quality_gate: bool = os.getenv("SCHEME_B_HU_QUALITY_GATE", "true").lower() == "true"
    # 方案 B 性能优化默认：跳过血管 TS、关闭 GGO 启发式、关闭 watershed
    scheme_b_skip_vessel_seg: bool = os.getenv("SCHEME_B_SKIP_VESSEL_SEG", "true").lower() in (
        "1", "true", "yes",
    )
    scheme_b_watershed_contour: bool = os.getenv("SCHEME_B_WATERSHED_CONTOUR", "false").lower() in (
        "1", "true", "yes",
    )

    # 方案 B P2：体数据缓存与 GGO 后端
    scheme_b_volume_cache: bool = os.getenv("SCHEME_B_VOLUME_CACHE", "true").lower() == "true"
    scheme_b_cache_dir: str = os.getenv("SCHEME_B_CACHE_DIR", "")
    scheme_b_cache_ttl_sec: int = int(os.getenv("SCHEME_B_CACHE_TTL_SEC", str(7 * 24 * 3600)))
    scheme_b_ggo_backend: str = os.getenv("SCHEME_B_GGO_BACKEND", "off")
    ggo_model_dir: str = os.getenv("GGO_MODEL_DIR", "")

    # 方案 B 合规文案
    scheme_b_disclaimer: str = os.getenv(
        "AI_DISCLAIMER_SCHEME_B",
        "AI 辅助结果仅供临床参考，不能替代医生诊断。"
        "平扫 CT 密度与形态分类仅供参考，不能作为确诊依据；最终诊断需结合病理、增强扫描与临床随访。",
    )


settings = Settings()


def _finalize_settings() -> None:
    from .log_paths import ai_cache_dir, ai_log_file, ensure_ai_dirs

    ensure_ai_dirs()
    if not settings.ai_log_path.strip():
        settings.ai_log_path = str(ai_log_file())
    if not settings.scheme_b_cache_dir.strip():
        settings.scheme_b_cache_dir = str(ai_cache_dir())


_finalize_settings()
