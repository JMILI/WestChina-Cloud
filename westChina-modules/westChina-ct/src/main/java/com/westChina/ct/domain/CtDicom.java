package com.westChina.ct.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.westChina.common.core.annotation.Excel;
import com.westChina.common.core.web.domain.BaseEntity;

/**
 * 病人dicom存储记录对象 ct_dicom
 *
 * @author westChina
 */
public class CtDicom extends BaseEntity {

    private static final long serialVersionUID = 1L;

    /**
     * id
     */
    private Long dicomId;

    /**
     * 身份证号
     */
    @Excel(name = "身份证号")
    private String patCardId;

    /**
     * ct拍摄时间
     */
    @Excel(name = "ct拍摄时间")
    private String dicomCtTime;

    /**
     * 研究UId
     */
    @Excel(name = "研究UId")
    private String dicomCtStudyUid;

    /**
     * 序列UId
     */
    @Excel(name = "序列UId")
    private String dicomCtSeriesUid;

    /**
     * 检查的身体部位
     */
    @Excel(name = "检查的身体部位")
    private String dicomCtBody;

    /**
     * 序列第一张的存储地址
     */
    @Excel(name = "序列第一张的存储地址")
    private String dicomCtPath;

    /**
     * 一个序列的dicom数量
     */
    @Excel(name = "一个序列的dicom数量")
    private Long dicomCtCount;

    /**
     * 备注
     */
    @Excel(name = "备注")
    private String dicomCtDescription;


    public CtDicom() {
    }

    public CtDicom(Long dicomId) {
        this.dicomId = dicomId;
    }

    public void setDicomId(Long dicomId) {
        this.dicomId = dicomId;
    }

    public Long getDicomId() {
        return dicomId;
    }

    public void setPatCardId(String patCardId) {
        this.patCardId = patCardId;
    }

    public String getPatCardId() {
        return patCardId;
    }

    public void setDicomCtTime(String dicomCtTime) {
        this.dicomCtTime = dicomCtTime;
    }

    public String getDicomCtTime() {
        return dicomCtTime;
    }

    public void setDicomCtStudyUid(String dicomCtStudyUid) {
        this.dicomCtStudyUid = dicomCtStudyUid;
    }

    public String getDicomCtStudyUid() {
        return dicomCtStudyUid;
    }

    public void setDicomCtSeriesUid(String dicomCtSeriesUid) {
        this.dicomCtSeriesUid = dicomCtSeriesUid;
    }

    public String getDicomCtSeriesUid() {
        return dicomCtSeriesUid;
    }

    public void setDicomCtBody(String dicomCtBody) {
        this.dicomCtBody = dicomCtBody;
    }

    public String getDicomCtBody() {
        return dicomCtBody;
    }

    public void setDicomCtPath(String dicomCtPath) {
        this.dicomCtPath = dicomCtPath;
    }

    public String getDicomCtPath() {
        return dicomCtPath;
    }

    public void setDicomCtCount(Long dicomCtCount) {
        this.dicomCtCount = dicomCtCount;
    }

    public Long getDicomCtCount() {
        return dicomCtCount;
    }

    public void setDicomCtDescription(String dicomCtDescription) {
        this.dicomCtDescription = dicomCtDescription;
    }

    public String getDicomCtDescription() {
        return dicomCtDescription;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
                .append("dicomId", getDicomId())
                .append("patCardId", getPatCardId())
                .append("dicomCtTime", getDicomCtTime())
                .append("dicomCtStudyUid", getDicomCtStudyUid())
                .append("dicomCtSeriesUid", getDicomCtSeriesUid())
                .append("dicomCtBody", getDicomCtBody())
                .append("dicomCtPath", getDicomCtPath())
                .append("dicomCtCount", getDicomCtCount())
                .append("dicomCtDescription", getDicomCtDescription())
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