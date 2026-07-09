package com.westChina.tenant.service.impl;

import cn.hutool.core.util.IdUtil;
import com.baomidou.dynamic.datasource.annotation.DS;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.westChina.common.core.constant.AuthorityConstants;
import com.westChina.common.core.exception.ServiceException;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.security.utils.SecurityUtils;
import com.westChina.system.api.domain.authority.SysRole;
import com.westChina.system.api.domain.organize.SysDept;
import com.westChina.system.api.domain.organize.SysPost;
import com.westChina.system.api.domain.organize.SysUser;
import com.westChina.tenant.domain.Tenant;
import com.westChina.tenant.mapper.CreationMapper;
import com.westChina.tenant.service.ICreationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

/**
 * 数据源 业务层处理
 *
 * @author westChina
 */
@Service
public class CreationServiceImpl implements ICreationService {

    @Autowired
    private CreationMapper creationMapper;

    /**
     * 租户新增-创建组织信息
     *
     * @param tenant 租户信息
     * @return 结果
     */
    @Override
    @DS("#tenant.sourceName")
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public int organizeCreation(Tenant tenant) {
        int d, p, u;
        Long deptId = IdUtil.getSnowflake(0, 0).nextId();
        Long postId = IdUtil.getSnowflake(0, 0).nextId();
        Long userId = IdUtil.getSnowflake(0, 0).nextId();
        Map<String, Object> params = tenant.getParams();
        // 1.建立新租户初始部门信息
        SysDept dept = params.containsKey("dept") ? new ObjectMapper().convertValue(params.get("dept"), SysDept.class) : new SysDept(deptId);
        if (params.containsKey("dept")) {
            dept.setDeptId(deptId);
        }
        params.put("dept", dept);
        // 2.建立新租户初始岗位信息
        SysPost post = params.containsKey("post") ? new ObjectMapper().convertValue(params.get("post"), SysPost.class) : new SysPost(postId, deptId);
        if (params.containsKey("post")) {
            post.setPostId(postId);
            post.setDeptId(deptId);
        }
        params.put("post", post);
        // 3.建立新租户初始用户信息
        SysUser user = params.containsKey("user") ? new ObjectMapper().convertValue(params.get("user"), SysUser.class) : new SysUser(userId, postId, deptId);
        if (StringUtils.isNotEmpty(user.getPassword())) {
            user.setPassword(SecurityUtils.encryptPassword(user.getPassword()));
        }
        if (params.containsKey("user")) {
            user.setUserId(userId);
            user.setPostId(postId);
            user.setDeptId(deptId);
        }
        params.put("user", user);
        d = creationMapper.createDeptByTenantId(tenant);
        p = creationMapper.createPostByTenantId(tenant);
        u = creationMapper.createUserByTenantId(tenant);
        verifyOrganizeSeedData(tenant);
        return d + p + u;
    }

    /**
     * 租户新增-创建衍生角色 && 屏蔽指定模块&&菜单
     *
     * @param tenant 租户信息
     * @return 结果
     */
    @Override
    @DS("#tenant.sourceName")
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public int deriveRoleCreation(Tenant tenant) {
        int r, or;
        Long deriveAdministratorId = IdUtil.getSnowflake(0, 0).nextId();
        Long deriveTenantId = IdUtil.getSnowflake(0, 0).nextId();
        Map<String, Object> params = tenant.getParams();
        // 1.建立新租户初始租管衍生角色信息
        SysRole deriveAdministrator = params.containsKey("role") ? (SysRole) params.get("role") : new SysRole(deriveAdministratorId);
        deriveAdministrator.setType(AuthorityConstants.RoleType.DERIVE_TENANT.getCode());
        deriveAdministrator.setName("租户衍生:" + deriveAdministratorId);
        if (!params.containsKey("role")) {
            params.put("role", deriveAdministrator);
        }
        // 2.建立新租户初始租户衍生角色信息
        SysRole deriveTenant = new SysRole(deriveTenantId);
        deriveTenant.setType(AuthorityConstants.RoleType.DERIVE_ENTERPRISE.getCode());
        deriveTenant.setName("企业衍生:" + deriveTenantId);
        params.put("deriveRole", deriveTenant);
        r = creationMapper.createRoleByTenantId(tenant);
        or = creationMapper.createOrganizeRoleByTenantId(tenant);
        verifyRoleSeedData(tenant);
        return r + or;
    }

    private void verifyOrganizeSeedData(Tenant tenant) {
        int deptCount = creationMapper.countDeptByTenantId(tenant);
        int postCount = creationMapper.countPostByTenantId(tenant);
        int userCount = creationMapper.countUserByTenantId(tenant);
        if (deptCount < 1 || postCount < 1 || userCount < 1) {
            throw new ServiceException("新租户初始化失败：部门/岗位/管理员账号未正确创建");
        }
    }

    private void verifyRoleSeedData(Tenant tenant) {
        int roleCount = creationMapper.countRoleByTenantId(tenant);
        int organizeRoleCount = creationMapper.countOrganizeRoleByTenantId(tenant);
        if (roleCount < 2 || organizeRoleCount < 2) {
            throw new ServiceException("新租户初始化失败：角色/组织角色关联未正确创建");
        }
    }
}