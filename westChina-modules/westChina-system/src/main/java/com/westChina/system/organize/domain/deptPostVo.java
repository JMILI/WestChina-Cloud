package com.westChina.system.organize.domain;

import com.westChina.common.core.web.domain.BaseEntity;
import java.util.List;

/**
 * 部门-岗位数组装结构
 *
 * @author westChina
 */
public class deptPostVo extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** Id */
    private Long Uid;

    /** 父Id（岗位父Id为归属部门） */
    private Long FUid;

    /** 名称 */
    private String name;

    /** 状态 */
    private String status;

    /** 类型（0 部门 1 岗位） */
    private String type;

    /** 子部门/岗位 */
    private List<deptPostVo> children;

    public deptPostVo() {

    }

    public deptPostVo(Long Uid, Long FUid, String name, String status, String type) {
        this.Uid = Uid;
        this.FUid = FUid;
        this.name = name;
        this.status = status;
        this.type = type;
    }

    public Long getUid() {
        return Uid;
    }

    public void setUid(Long uid) {
        Uid = uid;
    }

    public Long getFUid() {
        return FUid;
    }

    public void setFUid(Long FUid) {
        this.FUid = FUid;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public List<deptPostVo> getChildren() {
        return children;
    }

    public void setChildren(List<deptPostVo> children) {
        this.children = children;
    }
}
