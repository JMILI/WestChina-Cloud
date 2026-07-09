package com.westChina.tenant.mapper;

import com.westChina.tenant.domain.Tenant;


/**
 * 租户新增同步创建信息 数据层
 *
 * @author westChina
 */
public interface CreationMapper {

    /**
     * 创建新租户部门
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param tenant 租户管理
     * @return 结果
     */
    public int createDeptByTenantId(Tenant tenant);

    /**
     * 创建新租户岗位
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param tenant 租户管理
     * @return 结果
     */
    public int createPostByTenantId(Tenant tenant);

    /**
     * 创建新租户员工
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param tenant 租户管理
     * @return 结果
     */
    public int createUserByTenantId(Tenant tenant);

    /**
     * 创建新企业衍生角色
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param tenant 租户管理
     * @return 结果
     */
    public int createRoleByTenantId(Tenant tenant);

    /**
     * 创建新租户组织-衍生角色关联
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param tenant 租户管理
     * @return 结果
     */
    public int createOrganizeRoleByTenantId(Tenant tenant);

    /**
     * 统计新租户初始化后的部门数量
     */
    public int countDeptByTenantId(Tenant tenant);

    /**
     * 统计新租户初始化后的岗位数量
     */
    public int countPostByTenantId(Tenant tenant);

    /**
     * 统计新租户初始化后的用户数量
     */
    public int countUserByTenantId(Tenant tenant);

    /**
     * 统计新租户初始化后的角色数量
     */
    public int countRoleByTenantId(Tenant tenant);

    /**
     * 统计新租户初始化后的组织角色关联数量
     */
    public int countOrganizeRoleByTenantId(Tenant tenant);
}