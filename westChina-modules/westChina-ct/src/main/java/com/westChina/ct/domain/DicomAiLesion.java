package com.westChina.ct.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.westChina.common.core.annotation.Excel;
import com.westChina.common.core.web.domain.BaseEntity;

/**
 * AI识别病灶结果序列对象 dicom_ai_lesion
 */
public class DicomAiLesion extends BaseEntity {

    private static final long serialVersionUID = 1L;

    private Long dicomAiLesionId;

    private Long sourceDicomId;

    @Excel(name = "研究id")
    private String studyUid;

    @Excel(name = "序列UId")
    private String seriesUid;

    @Excel(name = "ct拍摄时间")
    private String studyDate;

    @Excel(name = "身份证号")
    private String patCardId;

    @Excel(name = "病人姓名")
    private String patientName;

    @Excel(name = "检查部位")
    private String bodyPart;

    @Excel(name = "识别医生")
    private String detectDoctor;

    @Excel(name = "医院名")
    private String detectEnterpriseName;

    @Excel(name = "识别时间")
    private String detectTime;

    @Excel(name = "AI序列路径")
    private String aiSeriesPath;

    private Integer imageCount;

    private Integer lesionCount;

    private String lesionsJson;

    private String engine;

    private String disclaimer;

    private String description;

    /** 识别模式：series 全序列 / single 当前层 */
    private String detectMode;

    /** 标记层 SOP Instance UID */
    private String instanceUid;

    /** 原始序列层索引（0-based） */
    private Integer sourceSliceIndex;

    public DicomAiLesion() {
    }

    public DicomAiLesion(Long dicomAiLesionId) {
        this.dicomAiLesionId = dicomAiLesionId;
    }

    public Long getDicomAiLesionId() {
        return dicomAiLesionId;
    }

    public void setDicomAiLesionId(Long dicomAiLesionId) {
        this.dicomAiLesionId = dicomAiLesionId;
    }

    public Long getSourceDicomId() {
        return sourceDicomId;
    }

    public void setSourceDicomId(Long sourceDicomId) {
        this.sourceDicomId = sourceDicomId;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getSeriesUid() {
        return seriesUid;
    }

    public void setSeriesUid(String seriesUid) {
        this.seriesUid = seriesUid;
    }

    public String getStudyDate() {
        return studyDate;
    }

    public void setStudyDate(String studyDate) {
        this.studyDate = studyDate;
    }

    public String getPatCardId() {
        return patCardId;
    }

    public void setPatCardId(String patCardId) {
        this.patCardId = patCardId;
    }

    public String getPatientName() {
        return patientName;
    }

    public void setPatientName(String patientName) {
        this.patientName = patientName;
    }

    public String getBodyPart() {
        return bodyPart;
    }

    public void setBodyPart(String bodyPart) {
        this.bodyPart = bodyPart;
    }

    public String getDetectDoctor() {
        return detectDoctor;
    }

    public void setDetectDoctor(String detectDoctor) {
        this.detectDoctor = detectDoctor;
    }

    public String getDetectEnterpriseName() {
        return detectEnterpriseName;
    }

    public void setDetectEnterpriseName(String detectEnterpriseName) {
        this.detectEnterpriseName = detectEnterpriseName;
    }

    public String getDetectTime() {
        return detectTime;
    }

    public void setDetectTime(String detectTime) {
        this.detectTime = detectTime;
    }

    public String getAiSeriesPath() {
        return aiSeriesPath;
    }

    public void setAiSeriesPath(String aiSeriesPath) {
        this.aiSeriesPath = aiSeriesPath;
    }

    public Integer getImageCount() {
        return imageCount;
    }

    public void setImageCount(Integer imageCount) {
        this.imageCount = imageCount;
    }

    public Integer getLesionCount() {
        return lesionCount;
    }

    public void setLesionCount(Integer lesionCount) {
        this.lesionCount = lesionCount;
    }

    public String getLesionsJson() {
        return lesionsJson;
    }

    public void setLesionsJson(String lesionsJson) {
        this.lesionsJson = lesionsJson;
    }

    public String getEngine() {
        return engine;
    }

    public void setEngine(String engine) {
        this.engine = engine;
    }

    public String getDisclaimer() {
        return disclaimer;
    }

    public void setDisclaimer(String disclaimer) {
        this.disclaimer = disclaimer;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getDetectMode() {
        return detectMode;
    }

    public void setDetectMode(String detectMode) {
        this.detectMode = detectMode;
    }

    public String getInstanceUid() {
        return instanceUid;
    }

    public void setInstanceUid(String instanceUid) {
        this.instanceUid = instanceUid;
    }

    public Integer getSourceSliceIndex() {
        return sourceSliceIndex;
    }

    public void setSourceSliceIndex(Integer sourceSliceIndex) {
        this.sourceSliceIndex = sourceSliceIndex;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
            .append("dicomAiLesionId", getDicomAiLesionId())
            .append("sourceDicomId", getSourceDicomId())
            .append("studyUid", getStudyUid())
            .append("seriesUid", getSeriesUid())
            .append("patCardId", getPatCardId())
            .append("aiSeriesPath", getAiSeriesPath())
            .append("imageCount", getImageCount())
            .append("lesionCount", getLesionCount())
            .toString();
    }
}
