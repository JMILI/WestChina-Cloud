package com.westChina.ct.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.westChina.common.core.annotation.Excel;
import com.westChina.common.core.web.domain.BaseEntity;

/**
 * 病人信息对象 ct_patients
 *
 * @author jm
 */
public class CtPatients extends BaseEntity {

    private static final long serialVersionUID = 1L;

    /** 唯一id，标识病人 */
    private Long patId;

    /** 身份证号 */
    @Excel(name = "身份证号")
    private String patCardId;

    /** 病人姓名 */
    @Excel(name = "病人姓名")
    private String patName;

    /** 病人手机号码 */
    @Excel(name = "病人手机号码")
    private String patPhone;


    public CtPatients() {
    }

    public CtPatients(Long patId) {
        this.patId = patId;
    }

    public void setPatId(Long patId) {
        this.patId = patId;
    }

    public Long getPatId() {
        return patId;
    }

    public void setPatCardId(String patCardId) {
        this.patCardId = patCardId;
    }

    public String getPatCardId() {
        return patCardId;
    }

    public void setPatName(String patName) {
        this.patName = patName;
    }

    public String getPatName() {
        return patName;
    }

    public void setPatPhone(String patPhone) {
        this.patPhone = patPhone;
    }

    public String getPatPhone() {
        return patPhone;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("patId", getPatId())
            .append("patCardId", getPatCardId())
            .append("patName", getPatName())
            .append("patPhone", getPatPhone())
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