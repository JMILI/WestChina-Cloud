package com.westChina.ct.domain;

import com.westChina.common.core.web.domain.BaseEntity;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;

/**
 * FormHit formHit
 * 搜索关键字（身份证号码OR手机号）查找 formHit和前端对应便于记忆
 *
 * @author jm
 */
public class FormHit extends BaseEntity {

    private static final long serialVersionUID = 9181698429073338706L;

    /**
     * 身份证号
     */
    private String patCardId;

    /**
     * 病人姓名
     */
    private String patName;

    /**
     * 病人手机号码
     */
    private String patPhone;


    public FormHit() {
    }

    public FormHit(Long patId) {
        this.patCardId = patCardId;
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
        return new ToStringBuilder(this, ToStringStyle.MULTI_LINE_STYLE)
                .append("patCardId", getPatCardId())
                .append("patName", getPatName())
                .append("patPhone", getPatPhone())
                .toString();
    }
}