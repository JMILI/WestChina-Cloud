package com.westChina.system.authority.service;

import com.westChina.system.api.domain.authority.SysMenu;
import com.westChina.system.api.domain.authority.SysRole;
import com.westChina.system.api.domain.authority.SysSystem;
import com.westChina.system.api.domain.authority.SystemMenu;
import com.westChina.system.utils.vo.TreeSelect;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 权限管理 业务层
 *
 * @author westChina
 */
public interface ISysAuthorityService {

    /**
     * 根据企业Id获取模块-菜单集合 | 租管级
     *
     * @param enterpriseId 企业Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectLessorMenuScope(Long enterpriseId);

    /**
     * 根据企业Id获取模块-菜单选择 | 半选 | 全选 | 租管级
     *
     * @param enterpriseId 企业Id
     * @param sourceName   指定源
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectLessorMenuRange(Long enterpriseId, String sourceName);

    /**
     * 根据租户Id查询角色信息集合 | 租户级
     *
     * @param enterpriseId 企业Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByTenantId(Long enterpriseId);

    /**
     * 根据企业Id获取模块-菜单集合 | 租户级
     *
     * @param role 角色信息 | enterpriseId 租户Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectTenantMenuScope(SysRole role);

    /**
     * 根据企业Id获取模块-菜单选择 | 半选 | 全选 | 租户级
     *
     * @param role 角色信息 | enterpriseId 租户Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectTenantMenuRange(SysRole role);

    /**
     * 根据租户Id查询角色信息集合 | 企业级
     *
     * @param role 角色信息 | enterpriseId 租户Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByEnterpriseId(SysRole role);

    /**
     * 根据企业Id获取模块-菜单集合 | 企业级
     *
     * @param role 角色信息 | enterpriseId 租户Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectEnterpriseMenuScope(SysRole role);

    /**
     * 根据企业Id获取模块-菜单选择 | 半选 | 全选 | 企业级
     *
     * @param role 角色信息 | enterpriseId 企业Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectEnterpriseMenuRange(SysRole role);

    /**
     * 根据部门Id查询角色信息集合 | 部门级
     *
     * @param role 角色信息 | params.deptId 部门Id | enterpriseId 租户Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByDeptId(SysRole role);

    /**
     * 根据部门Id获取模块-菜单集合 | 部门级
     *
     * @param role 角色信息 | params.deptId 部门Id | enterpriseId 租户Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectDeptMenuScope(SysRole role);

    /**
     * 根据部门Id获取模块-菜单选择 | 半选 | 全选 | 部门级
     *
     * @param role 角色信息 | params.deptId 部门Id | enterpriseId 企业Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectDeptMenuRange(SysRole role);

    /**
     * 根据岗位Id查询角色信息集合 | 岗位级
     *
     * @param role 角色信息 | params.postId 岗位Id | enterpriseId 租户Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByPostId(SysRole role);

    /**
     * 根据岗位Id获取模块-菜单集合 | 岗位级
     *
     * @param role 角色信息 | params.postId 岗位Id | enterpriseId 租户Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectPostMenuScope(SysRole role);

    /**
     * 根据岗位Id获取模块-菜单选择 | 半选 | 全选 | 岗位级
     *
     * @param role 角色信息 | params.postId 岗位Id | enterpriseId 企业Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectPostMenuRange(SysRole role);

    /**
     * 根据用户Id查询角色信息集合 | 用户级
     *
     * @param role 角色信息 | params.userId 用户Id | enterpriseId 租户Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByUserId(SysRole role);


    /**
     * 根据用户Id获取模块-菜单集合 | 用户级
     *
     * @param role 角色信息 | params.userId 用户Id | enterpriseId 租户Id
     * @return 模块-菜单集合
     */
    public List<TreeSelect> selectUserMenuScope(SysRole role);

    /**
     * 根据用户Id获取模块-菜单选择 | 半选 | 全选 | 用户级
     *
     * @param role 角色信息 | params.userId 用户Id | enterpriseId 企业Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectUserMenuRange(SysRole role);

    /**
     * 根据角色Id查询角色信息集合 | 角色级
     *
     * @param role 角色信息 | roleId 角色Id | enterpriseId 企业Id
     * @return 角色信息集合
     */
    public List<SysRole> selectRoleListByRoleId(SysRole role);

    /**
     * 根据角色Id获取模块-菜单选择 | 半选 | 全选 | 角色级
     *
     * @param role 角色信息 | params.userId 用户Id | enterpriseId 企业Id
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> selectRoleMenuRange(SysRole role);

    /**
     * 根据角色Id获取部门-岗位选择 | 角色级
     *
     * @param role 角色信息 | roleId 角色Id
     * @return 角色信息
     */
    public SysRole selectRoleDataRange(SysRole role);

    /**
     * 根据角色信息更新模块-菜单集合
     *
     * @param role       角色信息 | roleId 角色Id | enterpriseId 租户Id | dataScope 数据范围 | params.wholeIds 全选 | params.halfIds 半选
     * @param sourceName 指定源
     */
    public void updateMenuScopeToSourceName(SysRole role, String sourceName);

    /**
     * 根据角色信息更新模块-菜单集合
     *
     * @param role 角色信息 | roleId 角色Id | enterpriseId 租户Id | dataScope 数据范围 | params.wholeIds 全选 | params.halfIds 半选
     */
    public void updateMenuScope(SysRole role);

    /**
     * 根据用户Id查询角色信息集合
     *
     * @param enterpriseId  企业Id
     * @param roles         角色信息集合
     * @param isAdminTenant 是否租管租户
     * @param hasNormal     有无普通角色权限（true -> 初始权限集合由全部更替为普通角色和）
     * @param hasStatus     有无状态 （true -> status must normal）
     * @return map集合 | halfIds 半选模块-菜单 | wholeIds 全选模块-菜单
     */
    public Map<String, Set<SystemMenu>> assembleSystemMenuSet(Long enterpriseId, List<SysRole> roles, boolean isAdminTenant, boolean hasNormal, boolean hasStatus);

    /**
     * 装配菜单集合
     *
     * @param enterpriseId  企业Id
     * @param roles         角色信息集合
     * @param isAdminTenant 是否租管租户
     * @param hasNormal     有无普通角色权限（true -> 初始权限集合由全部更替为普通角色和）
     * @param hasStatus     有无状态 （true -> status must normal）
     * @return 菜单集合
     */
    public Set<SysMenu> selectMenuSet(Long enterpriseId, List<SysRole> roles, boolean isAdminTenant, boolean hasNormal, boolean hasStatus);

    /**
     * 装配模块集合
     *
     * @param enterpriseId  企业Id
     * @param roles         角色信息集合
     * @param isAdminTenant 是否租管租户
     * @param hasNormal     有无普通角色权限（true -> 初始权限集合由全部更替为普通角色和）
     * @param hasStatus     有无状态 （true -> status must normal）
     * @return 模块集合
     */
    public Set<SysSystem> selectSystemSet(Long enterpriseId, List<SysRole> roles, boolean isAdminTenant, boolean hasNormal, boolean hasStatus);

    /**
     * 根据角色Id查询角色权限
     *
     * @param enterpriseId 企业Id
     * @param roleId       角色Id
     * @return 角色集合
     */
    public SysRole getRoleAuthorityByRoleId(Long enterpriseId, Long roleId);

    /**
     * 查询角色权限集合
     *
     * @param enterpriseId 企业Id
     * @param roleIds      角色Ids
     * @return 角色集合
     */
    public List<SysRole> getRoleAuthority(Long enterpriseId, Set<Long> roleIds);

    /**
     * 查询指定源角色权限集合
     *
     * @param enterpriseId 企业Id
     * @param roleIds      角色Ids
     * @return 角色集合
     */
    public List<SysRole> getRoleAuthorityBySourceName(Long enterpriseId, Set<Long> roleIds, String sourceName);
}
