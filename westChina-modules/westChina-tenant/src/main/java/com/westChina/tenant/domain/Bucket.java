package com.westChina.tenant.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.westChina.common.core.annotation.Excel;
import com.westChina.common.core.web.domain.BaseEntity;

/**
 * 对象存储，存储租户的桶信息对象 xy_tenant_bucket
 *
 * @author jm
 */
public class Bucket extends BaseEntity {

    private static final long serialVersionUID = 1L;

    /**
     * 桶Id
     */
    private Long bucketId;

    /**
     * 桶名
     */
    @Excel(name = "桶名")
    private String bucketName;

    /**
     * 桶所属的租户
     */
    @Excel(name = "桶所属的租户")
    private Long bucketTenantId;

    /**
     * 桶所属的租户名
     */
    @Excel(name = "桶所属的租户名")
    private String bucketTenantName;

    /**
     * 状态（0正常 1停用）
     */
    @Excel(name = "状态", readConverterExp = "0=正常,1=停用")
    private String status;

    /**
     * 删除标志
     */
    private Long delFlag;


    public Bucket() {
    }

    public Bucket(Long bucketId) {
        this.bucketId = bucketId;
    }

    public void setBucketId(Long bucketId) {
        this.bucketId = bucketId;
    }

    public Long getBucketId() {
        return bucketId;
    }

    public void setBucketName(String bucketName) {
        this.bucketName = bucketName;
    }

    public String getBucketName() {
        return bucketName;
    }

    public void setBucketTenantId(Long bucketTenantId) {
        this.bucketTenantId = bucketTenantId;
    }

    public Long getBucketTenantId() {
        return bucketTenantId;
    }

    public void setBucketTenantName(String bucketTenantName) {
        this.bucketTenantName = bucketTenantName;
    }

    public String getBucketTenantName() {
        return bucketTenantName;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getStatus() {
        return status;
    }

    @Override
    public Long getDelFlag() {
        return delFlag;
    }

    @Override
    public void setDelFlag(Long delFlag) {
        this.delFlag = delFlag;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
                .append("bucketId", getBucketId())
                .append("bucketName", getBucketName())
                .append("bucketTenantId", getBucketTenantId())
                .append("bucketTenantName", getBucketTenantName())
                .append("sort", getSort())
                .append("status", getStatus())
                .append("createBy", getCreateBy())
                .append("createName", getCreateName())
                .append("createTime", getCreateTime())
                .append("updateBy", getUpdateBy())
                .append("updateName", getUpdateName())
                .append("updateTime", getUpdateTime())
                .append("delFlag", getDelFlag())
                .toString();
    }
}