package com.westChina.ct.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.westChina.common.core.annotation.Excel;
import com.westChina.common.core.web.domain.BaseEntity;

/**
 * 病人标记过的dicom图像对象 dicom_maker
 *
 * @author westChina
 */
public class DicomMaker extends BaseEntity {

    private static final long serialVersionUID = 1L;

    /** id */
    private Long dicomMakerId;

    /** 单张图像instanceID */
    @Excel(name = "单张图像instanceID")
    private String instanceUid;

    /** 研究id */
    @Excel(name = "研究id")
    private String studyUid;

    /** 序列UId */
    @Excel(name = "序列UId")
    private String seriesUid;

    /** ct拍摄时间 */
    @Excel(name = "ct拍摄时间")
    private String studyDate;

    /** 身份证号 */
    @Excel(name = "身份证号")
    private String patCardId;

    /** 病人姓名 */
    @Excel(name = "病人姓名")
    private String patientName;

    /** 标记医生 */
    @Excel(name = "标记医生")
    private String makerDoctor;

    /** 医院名 */
    @Excel(name = "医院名")
    private String makerEnterpriseName;

    /** 标记时间 */
    @Excel(name = "标记时间")
    private String makerTime;

    /** 标记图像地址 */
    @Excel(name = "标记图像地址")
    private String markerImageAddress;

    /** 备注 */
    @Excel(name = "备注")
    private String makerDescription;

    /** 用来存储图像元数据，临时用 */
    private String makerImage;


    public DicomMaker() {
    }

    public DicomMaker(Long dicomMakerId) {
        this.dicomMakerId = dicomMakerId;
    }

    public void setDicomMakerId(Long dicomMakerId) {
        this.dicomMakerId = dicomMakerId;
    }

    public Long getDicomMakerId() {
        return dicomMakerId;
    }

    public void setInstanceUid(String instanceUid) {
        this.instanceUid = instanceUid;
    }

    public String getInstanceUid() {
        return instanceUid;
    }

    public void setStudyUid(String studyUid) {
        this.studyUid = studyUid;
    }

    public String getStudyUid() {
        return studyUid;
    }

    public void setSeriesUid(String seriesUid) {
        this.seriesUid = seriesUid;
    }

    public String getSeriesUid() {
        return seriesUid;
    }

    public void setStudyDate(String studyDate) {
        this.studyDate = studyDate;
    }

    public String getStudyDate() {
        return studyDate;
    }

    public void setPatCardId(String patCardId) {
        this.patCardId = patCardId;
    }

    public String getPatCardId() {
        return patCardId;
    }

    public void setPatientName(String patientName) {
        this.patientName = patientName;
    }

    public String getPatientName() {
        return patientName;
    }

    public void setMakerDoctor(String makerDoctor) {
        this.makerDoctor = makerDoctor;
    }

    public String getMakerDoctor() {
        return makerDoctor;
    }

    public void setMakerEnterpriseName(String makerEnterpriseName) {
        this.makerEnterpriseName = makerEnterpriseName;
    }

    public String getMakerEnterpriseName() {
        return makerEnterpriseName;
    }

    public void setMakerTime(String makerTime) {
        this.makerTime = makerTime;
    }

    public String getMakerTime() {
        return makerTime;
    }

    public void setMarkerImageAddress(String markerImageAddress) {
        this.markerImageAddress = markerImageAddress;
    }

    public String getMarkerImageAddress() {
        return markerImageAddress;
    }

    public void setMakerDescription(String makerDescription) {
        this.makerDescription = makerDescription;
    }

    public String getMakerDescription() {
        return makerDescription;
    }

    public void setMakerImage(String makerImage) {
        this.makerImage = makerImage;
    }

    public String getMakerImage() {
        return makerImage;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("dicomMakerId", getDicomMakerId())
            .append("instanceUid", getInstanceUid())
            .append("studyUid", getStudyUid())
            .append("seriesUid", getSeriesUid())
            .append("studyDate", getStudyDate())
            .append("patCardId", getPatCardId())
            .append("patientName", getPatientName())
            .append("makerDoctor", getMakerDoctor())
            .append("makerEnterpriseName", getMakerEnterpriseName())
            .append("makerTime", getMakerTime())
            .append("markerImageAddress", getMarkerImageAddress())
            .append("makerDescription", getMakerDescription())
            .append("makerImage", getMakerImage())
            .append("sort", getSort())
            .append("createBy", getCreateBy())
            .append("createName", getCreateName())
            .append("createTime", getCreateTime())
            .append("updateBy", getUpdateBy())
            .append("updateName", getUpdateName())
            .append("updateTime", getUpdateTime())
            .append("remark", getRemark())
            .toString();
    }
}