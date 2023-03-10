package com.westChina.system.authority.service;

import com.westChina.system.api.domain.authority.SysRole;

import java.util.List;
import java.util.Set;

/**
 * 角色业务层
 *
 * @author westChina
 */
public interface ISysRoleService {

    /**
     * 根据角色Id查询角色信息集合
     *
     * @param userId       用户Id
     * @param enterpriseId 企业Id
     * @param sourceName   指定数据源名称
     * @return 角色信息集合信息
     */
    public List<SysRole> getRoleListByUserId(Long userId, Long enterpriseId, String sourceName);

    /**
     * 根据条件分页查询角色数据
     *
     * @param role 角色信息
     * @return 角色数据集合信息
     */
    public List<SysRole> selectRoleList(SysRole role);

    /**
     * 查询所有角色
     *
     * @return 角色列表
     */
    public List<SysRole> selectRoleAll();

    /**
     * 通过角色Id查询角色
     *
     * @param role 角色信息 | roleId 角色Id
     * @return 角色对象信息
     */
    public SysRole selectRoleById(SysRole role);

    /**
     * 通过角色Id查询角色使用数量
     *
     * @param role 角色信息 | roleId 角色Id
     * @return 结果
     */
    public int useCountByRoleId(SysRole role);

    /**
     * 新增保存角色信息
     *
     * @param role 角色信息
     * @return 结果
     */
    public int insertRole(SysRole role);

    /**
     * 修改保存角色信息
     *
     * @param role 角色信息
     * @return 结果
     */
    public int updateRole(SysRole role);

    /**
     * 修改角色状态
     *
     * @param role 角色信息 | roleId 角色Id | status 角色状态
     * @return 结果
     */
    public int updateRoleStatus(SysRole role);

    /**
     * 修改数据权限信息
     *
     * @param role 角色信息
     * @return 结果
     */
    public int authDataScope(SysRole role);

    /**
     * 批量删除角色信息
     *
     * @param role 角色信息 | params.Ids 需要删除的角色Ids组
     * @return 结果
     */
    public int deleteRoleByIds(SysRole role);

    /**
     * 查询角色Id存在于数组中的角色信息
     *
     * @param role 角色信息 | params.Ids 需要删除的角色Ids组
     * @return 结果
     */
    public Set<SysRole> checkRoleListByIds(SysRole role);

    /**
     * 校验角色编码是否唯一
     *
     * @param role 角色信息 | roleId   角色Id | roleCode 角色编码
     * @return 结果
     */
    public String checkRoleCodeUnique(SysRole role);

    /**
     * 校验角色名称是否唯一
     *
     * @param role 角色信息 | roleId   角色Id | name 角色名称
     * @return 结果
     */
    public String checkRoleNameUnique(SysRole role);

    /**
     * 校验角色权限是否唯一
     *
     * @param role 角色信息 | roleId  角色Id | roleKey 角色权限
     * @return 结果
     */
    public String checkRoleKeyUnique(SysRole role);

    /**
     * 通过类型和衍生Id查询角色Id与数据范围
     *
     * @param role       角色信息 | type 角色类型 | derive_id 衍生Id | enterpriseId 企业Id
     * @param sourceName 指定源
     * @return 角色Id
     */
    public SysRole selectRoleIdByDeriveIdToSourceName(SysRole role, String sourceName);

    /**
     * 通过类型和衍生Id查询角色Id与数据范围
     *
     * @param role 角色信息 | type 角色类型 | derive_id 衍生Id | enterpriseId 企业Id
     * @return 角色Id
     */
    public SysRole selectRoleIdByDeriveId(SysRole role);
}
