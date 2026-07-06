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
    ai_log_path: str = os.getenv("AI_LOG_PATH", "../deploymentServer/logs/ai-service.log")

    # CPU 全序列：超过该层数时均匀降采样（GPU 可用时不限制）
    series_max_slices_cpu: int = int(os.getenv("SERIES_MAX_SLICES_CPU", "128"))


settings = Settings()
