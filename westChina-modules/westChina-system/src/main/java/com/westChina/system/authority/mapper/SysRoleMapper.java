package com.westChina.system.authority.mapper;

import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.system.api.domain.authority.SysRole;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Set;

/**
 * 角色表 数据层
 *
 * @author westChina
 */
public interface SysRoleMapper {

    /**
     * 根据角色Id查询角色权限
     *
     * @param roleId       角色Id
     * @param enterpriseId 企业Id
     * @return 角色信息集合信息
     */
    public SysRole getRoleAuthorityByRoleId(@Param("enterpriseId") Long enterpriseId, @Param("roleId") Long roleId);

    /**
     * 查询角色权限集合
     *
     * @param roleIds      角色Ids
     * @param enterpriseId 企业Id
     * @return 角色信息集合信息
     */
    public List<SysRole> getRoleAuthority(@Param("enterpriseId") Long enterpriseId, @Param("roleIds") Set<Long> roleIds);

    /**
     * 根据角色Id查询角色信息集合
     *
     * @param userId       用户Id
     * @param enterpriseId 企业Id
     * @return 角色信息集合信息
     */
    public List<SysRole> getRoleListByUserId(@Param("userId") Long userId, @Param("enterpriseId") Long enterpriseId);

    /**
     * 根据衍生来源Id&角色类型查询指定衍生角色
     *
     * @param role 角色信息 | type 角色类型 | deriveId 衍生来源Id | enterpriseId 租户Id
     * @return 角色Id
     */
    public Long selectDeriveRoleByEnterpriseId(SysRole role);

    /**
     * 查询所有角色 | exclude 衍生角色
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | null
     * @return 角色列表
     */
    @DataScope(eAlias = "r")
    public List<SysRole> selectRoleAll(SysRole role);

    /**
     * 根据用户Id查询角色
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | params.userName 用户名
     * @return 角色列表
     */
    @DataScope(eAlias = "r")
    public List<SysRole> selectRolesByUserName(SysRole role);

    /**
     * 根据条件分页查询角色数据
     * 访问控制 r 租户查询
     *
     * @param role 角色信息
     * @return 角色数据集合信息
     */
    @DataScope(eAlias = "r")
    public List<SysRole> selectRoleList(SysRole role);

    /**
     * 通过角色Id查询角色
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | roleId 角色Id
     * @return 角色对象信息
     */
    @DataScope(eAlias = "r")
    public SysRole selectRoleById(SysRole role);

    /**
     * 新增角色信息
     *
     * @param role 角色信息
     * @return 结果
     */
    public int insertRole(SysRole role);

    /**
     * 修改角色信息
     *
     * @param role 角色信息
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int updateRole(SysRole role);

    /**
     * 修改角色状态
     *
     * @param role 角色信息 | roleId 角色Id | status 角色状态
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int updateRoleStatus(SysRole role);

    /**
     * 修改角色数据范围
     *
     * @param role 角色信息 | roleId 角色Id | dataScope 数据范围
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int updateRoleDataScope(SysRole role);

    /**
     * 依据角色类型 && 衍生Id 删除角色信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param role 角色信息 | type 角色类型 | deriveId 衍生Id
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int deleteRoleByDeriveId(SysRole role);

    /**
     * 依据角色类型 && 衍生Ids 批量删除角色信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param role 角色信息 | type 角色类型 | params.Ids 需要删除的衍生Ids组
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int deleteRoleByDeriveIds(SysRole role);

    /**
     * 批量删除角色信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param role 角色信息 | params.Ids 需要删除的角色Ids组
     * @return 结果
     */
    @DataScope(ueAlias = "empty")
    public int deleteRoleByIds(SysRole role);

    /**
     * 查询角色Id存在于数组中的角色信息
     *
     * @param role 角色信息 | params.Ids 需要删除的角色Ids组
     * @return 结果
     */
    @DataScope(eAlias = "r")
    public Set<SysRole> checkRoleListByIds(SysRole role);

    /**
     * 校验角色编码是否唯一
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | roleCode 角色编码
     * @return 角色信息
     */
    @DataScope(eAlias = "r")
    public SysRole checkRoleCodeUnique(SysRole role);

    /**
     * 校验角色名称是否唯一
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | name 角色名称
     * @return 角色信息
     */
    @DataScope(eAlias = "r")
    public SysRole checkRoleNameUnique(SysRole role);

    /**
     * 校验角色权限是否唯一
     * 访问控制 r 租户查询
     *
     * @param role 角色信息 | roleKey 角色权限
     * @return 角色信息
     */
    @DataScope(eAlias = "r")
    public SysRole checkRoleKeyUnique(SysRole role);

    /**
     * 通过类型和衍生Id查询角色Id与数据范围
     *
     * @param role 角色信息 | type 角色类型 | derive_id 衍生Id | enterpriseId 企业Id
     * @return 角色Id
     */
    public SysRole selectRoleIdByDeriveId(SysRole role);
}