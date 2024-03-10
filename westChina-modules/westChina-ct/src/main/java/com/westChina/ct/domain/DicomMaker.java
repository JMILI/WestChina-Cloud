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
    private String makerImageAddress;

    /** 备注 */
    @Excel(name = "备注")
    private String makerDescription;

    /** 用来存储图像元数据，临时用 */
    private String makerImage;

    /** 列值 */
    private Integer makerColumns;

    /** 行值 */
    private Integer makerRows;

    /** 列像素间距 */
    private Double makerColumnPixelSpacing;

    /** 行像素间距 */
    private Double makerRowPixelSpacing;

    /** 转换系数，用于像素到CT值的转换 */
    private Integer makerSlope;

    /** 截距，用于像素到CT值的转换 */
    private Integer makerIntercept;

    /** 窗位 */
    private Integer makerWindowCenter;

    /** 窗宽 */
    private Integer makerWindowWidth;

    /** 是否时dicom p10格式文件 */
    private Long makerIsDicom;

    /** 缩放比例 */
    private Double makerScale;


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

    public void setMakerImageAddress(String makerImageAddress) {
        this.makerImageAddress = makerImageAddress;
    }

    public String getMakerImageAddress() {
        return makerImageAddress;
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

    public void setMakerColumns(Integer makerColumns) {
        this.makerColumns = makerColumns;
    }

    public Integer getMakerColumns() {
        return makerColumns;
    }

    public void setMakerRows(Integer makerRows) {
        this.makerRows = makerRows;
    }

    public Integer getMakerRows() {
        return makerRows;
    }

    public void setMakerColumnPixelSpacing(Double makerColumnPixelSpacing) {
        this.makerColumnPixelSpacing = makerColumnPixelSpacing;
    }

    public Double getMakerColumnPixelSpacing() {
        return makerColumnPixelSpacing;
    }

    public void setMakerRowPixelSpacing(Double makerRowPixelSpacing) {
        this.makerRowPixelSpacing = makerRowPixelSpacing;
    }

    public Double getMakerRowPixelSpacing() {
        return makerRowPixelSpacing;
    }

    public void setMakerSlope(Integer makerSlope) {
        this.makerSlope = makerSlope;
    }

    public Integer getMakerSlope() {
        return makerSlope;
    }

    public void setMakerIntercept(Integer makerIntercept) {
        this.makerIntercept = makerIntercept;
    }

    public Integer getMakerIntercept() {
        return makerIntercept;
    }

    public void setMakerWindowCenter(Integer makerWindowCenter) {
        this.makerWindowCenter = makerWindowCenter;
    }

    public Integer getMakerWindowCenter() {
        return makerWindowCenter;
    }

    public void setMakerWindowWidth(Integer makerWindowWidth) {
        this.makerWindowWidth = makerWindowWidth;
    }

    public Integer getMakerWindowWidth() {
        return makerWindowWidth;
    }

    public void setMakerIsDicom(Long makerIsDicom) {
        this.makerIsDicom = makerIsDicom;
    }

    public Long getMakerIsDicom() {
        return makerIsDicom;
    }

    public void setMakerScale(Double makerScale) {
        this.makerScale = makerScale;
    }

    public Double getMakerScale() {
        return makerScale;
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
                .append("makerImageAddress", getMakerImageAddress())
                .append("makerDescription", getMakerDescription())
                .append("makerImage", getMakerImage())
                .append("makerColumns", getMakerColumns())
                .append("makerRows", getMakerRows())
                .append("makerColumnPixelSpacing", getMakerColumnPixelSpacing())
                .append("makerRowPixelSpacing", getMakerRowPixelSpacing())
                .append("makerSlope", getMakerSlope())
                .append("makerIntercept", getMakerIntercept())
                .append("makerWindowCenter", getMakerWindowCenter())
                .append("makerWindowWidth", getMakerWindowWidth())
                .append("makerIsDicom", getMakerIsDicom())
                .append("makerScale", getMakerScale())
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