package com.westChina.common.datascope.aspect;

import cn.hutool.core.lang.Snowflake;
import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.RandomUtil;
import com.westChina.common.core.constant.AuthorityConstants;
import com.westChina.common.security.utils.SecurityUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.web.domain.BaseEntity;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.system.api.domain.authority.SysRole;
import com.westChina.system.api.domain.organize.SysEnterprise;
import com.westChina.system.api.domain.organize.SysUser;
import com.westChina.system.api.model.LoginUser;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.stereotype.Component;

/**
 * 数据过滤处理
 *
 * @author westChina
 */
@Aspect
@Component
public class DataScopeAspect {

    /** 数据权限过滤关键字 | 查询 */
    public static final String DATA_SCOPE = "dataScope";

    /** 数据权限过滤关键字 | 更新 */
    public static final String UPDATE_SCOPE = "updateScope";

    @Before("@annotation(controllerDataScope)")
    public void doBefore(JoinPoint point, DataScope controllerDataScope) throws Throwable {
        clearDataScope(point);
        handleDataScope(point, controllerDataScope);
    }

    protected void handleDataScope(final JoinPoint joinPoint, DataScope controllerDataScope) {
        // 获取当前的用户
        LoginUser loginUser = SecurityUtils.getLoginUser();
        if (StringUtils.isNotNull(loginUser)) {
            if (StringUtils.isNotNull(loginUser.getSysUser())) {
                dataScopeFilter(joinPoint, loginUser, controllerDataScope);
            }
        }
    }

    /**
     * 数据范围过滤
     *
     * @param joinPoint           切点
     * @param loginUser           用户信息
     * @param controllerDataScope 切片数据
     */
    public static void dataScopeFilter(JoinPoint joinPoint, LoginUser loginUser, DataScope controllerDataScope) {
        SysEnterprise enterprise = loginUser.getSysEnterprise();
        SysUser user = loginUser.getSysUser();

        String deptAlias = controllerDataScope.deptAlias();
        String postAlias = controllerDataScope.postAlias();
        String userAlias = controllerDataScope.userAlias();

        /* 租户的别名 | 控制 enterpriseId */
        /* 租户的别名 | 控制 enterpriseId (包含 enterpriseId = 0 的数据) */
        /* 租户更新控制的别名 | 控制 enterpriseId (empty 无前缀更新 | other 有前缀更新) */
        /* 租户更新控制的别名 | 控制 enterpriseId (包含 enterpriseId = 0 的数据) (empty 无前缀更新 | other 有前缀更新) */
        String eAlias = controllerDataScope.eAlias();
        String edAlias = controllerDataScope.edAlias();
        String ueAlias = controllerDataScope.ueAlias();
        String uedAlias = controllerDataScope.uedAlias();

        /* 系统的别名 | 控制 systemId */
        /* 系统的别名 | 控制 systemId (包含 enterpriseId = 0 的数据) */
        /* 系统更新控制的别名 | 控制 systemId (empty 无前缀更新 | other 有前缀更新) */
        String SYAlias = controllerDataScope.SYAlias();
        String SYdAlias = controllerDataScope.SYdAlias();
        String uSYAlias = controllerDataScope.uSYAlias();

        /* 站点的别名 | 控制 siteId */
        /* 站点的别名 | 控制 siteId (包含 siteId = 0 的数据) */
        /* 站点更新控制的别名 | 控制 siteId (empty 无前缀更新 | other 有前缀更新) */
        String SIAlias = controllerDataScope.SIAlias();
        String SIdAlias = controllerDataScope.SIdAlias();
        String uSIAlias = controllerDataScope.uSIAlias();

        /* 库的别名 | 控制 libraryId */
        /* 库的别名 | 控制 libraryId (包含 libraryId = 0 的数据) */
        /* 库更新控制的别名 | 控制 libraryId (empty 无前缀更新 | other 有前缀更新) */
        String LIAlias = controllerDataScope.LIAlias();
        String LIdAlias = controllerDataScope.LIdAlias();
        String uLIAlias = controllerDataScope.uLIAlias();

        //默认只获取第一个参数
        Object params = joinPoint.getArgs()[0];
        StringBuilder sqlString = new StringBuilder();
        StringBuilder upSqlString = new StringBuilder();

        // 如果是超级管理员，则不过滤数据
        if (StringUtils.isNotBlank(deptAlias) || StringUtils.isNotBlank(postAlias) || StringUtils.isNotBlank(userAlias)) {
            if (!user.isAdmin()) {
                for (SysRole role : user.getRoles()) {
                    String dataScope = role.getDataScope();
                    // 1.全部数据权限
                    if (StringUtils.equals(AuthorityConstants.DataScope.ALL.getCode(), dataScope)) {
                        sqlString = new StringBuilder();
                        break;
                    }
                    // 2.自定数据权限
                    else if (StringUtils.equals(AuthorityConstants.DataScope.CUSTOM.getCode(), dataScope) && (StringUtils.isNotBlank(deptAlias) || StringUtils.isNotBlank(postAlias))) {
                        if (StringUtils.isNotBlank(deptAlias) && StringUtils.isNotBlank(postAlias)) {
                            sqlString.append(StringUtils.format(
                                    " OR ( {}.dept_id IN ( SELECT dept_post_id FROM sys_role_dept_post WHERE role_id = {} ) OR {}.post_id IN ( SELECT dept_post_id FROM sys_role_dept_post WHERE role_id = {} ) ) ", deptAlias,
                                    role.getRoleId(), postAlias, role.getRoleId()));
                        } else if (StringUtils.isNotBlank(deptAlias)) {
                            sqlString.append(StringUtils.format(
                                    " OR {}.dept_id IN ( SELECT dept_post_id FROM sys_role_dept_post WHERE role_id = {} ) ", deptAlias,
                                    role.getRoleId(), postAlias, role.getRoleId()));
                        } else if (StringUtils.isNotBlank(postAlias)) {
                            sqlString.append(StringUtils.format(
                                    " OR {}.post_id IN ( SELECT dept_post_id FROM sys_role_dept_post WHERE role_id = {} ) ", deptAlias,
                                    role.getRoleId(), postAlias, role.getRoleId()));
                        }
                    }
                    // 3.本部门数据权限
                    else if (StringUtils.equals(AuthorityConstants.DataScope.DEPT.getCode(), dataScope) && StringUtils.isNotBlank(deptAlias)) {
                        sqlString.append(StringUtils.format(" OR {}.dept_id = {} ", deptAlias, user.getDeptId()));
                    }
                    // 4.本部门及以下数据权限
                    else if (StringUtils.equals(AuthorityConstants.DataScope.DEPT_AND_CHILD.getCode(), dataScope) && StringUtils.isNotBlank(deptAlias)) {
                        sqlString.append(StringUtils.format(
                                " OR {}.dept_id IN ( SELECT dept_id FROM sys_dept WHERE dept_id = {} or find_in_set( {} , ancestors ) ) ",
                                deptAlias, user.getDeptId(), user.getDeptId()));
                    }
                    // 5.本岗位数据权限
                    else if (StringUtils.equals(AuthorityConstants.DataScope.POST.getCode(), dataScope) && StringUtils.isNotBlank(postAlias)) {
                        sqlString.append(StringUtils.format(" OR {}.post_id = {} ", postAlias, user.getPostId()));
                    }
                    // 6.仅本人数据权限
                    else if (StringUtils.equals(AuthorityConstants.DataScope.SELF.getCode(), dataScope)) {
                        if (StringUtils.isNotBlank(userAlias)) {
                            sqlString.append(StringUtils.format(" OR {}.user_id = {} ", userAlias, user.getUserId()));
                        }
                    }
                }

                // 权限表的租户控制
                if (StringUtils.isNotBlank(eAlias)) {
                    if (StringUtils.isNotBlank(deptAlias)) {
                        sqlString.append(StringUtils.format(" AND {}.tenant_id = {} ", deptAlias, enterprise.getEnterpriseId()));
                    }
                    if (StringUtils.isNotBlank(postAlias)) {
                        sqlString.append(StringUtils.format(" AND {}.tenant_id = {} ", postAlias, enterprise.getEnterpriseId()));
                    }
                    if (StringUtils.isNotBlank(userAlias)) {
                        sqlString.append(StringUtils.format(" AND {}.tenant_id = {} ", userAlias, enterprise.getEnterpriseId()));
                    }
                } else {
                    if (StringUtils.isNotBlank(deptAlias)) {
                        sqlString.append(StringUtils.format(" AND ( {}.tenant_id = {} or {}.tenant_id = 0 ) ", deptAlias, enterprise.getEnterpriseId(), deptAlias));
                    }
                    if (StringUtils.isNotBlank(postAlias)) {
                        sqlString.append(StringUtils.format(" AND ( {}.tenant_id = {} or {}.tenant_id = 0 ) ", postAlias, enterprise.getEnterpriseId(), postAlias));
                    }
                    if (StringUtils.isNotBlank(userAlias)) {
                        sqlString.append(StringUtils.format(" AND ( {}.tenant_id = {} or {}.tenant_id = 0 ) ", userAlias, enterprise.getEnterpriseId(), userAlias));
                    }
                }
            }
        }
        // 租户级数据查询|更新分离模式
        if (StringUtils.isNotBlank(eAlias)) {
            sqlString.append(StringUtils.format(" AND {}.tenant_id = {} AND {}.del_flag = 0 ", eAlias, enterprise.getEnterpriseId(), eAlias));
        } else if (StringUtils.isNotBlank(edAlias)) {
            sqlString.append(StringUtils.format(" AND ( {}.tenant_id = {} or {}.tenant_id = 0 ) AND {}.del_flag = 0 ", edAlias, enterprise.getEnterpriseId(), edAlias, edAlias));
        } else if (StringUtils.isNotBlank(ueAlias)) {
            if (ueAlias.equals("empty")) {
                upSqlString.append(StringUtils.format(" AND tenant_id = {} AND del_flag = 0 ", enterprise.getEnterpriseId()));
            } else {
                upSqlString.append(StringUtils.format(" AND {}.tenant_id = {} AND {}.del_flag = 0 ", ueAlias, enterprise.getEnterpriseId(), ueAlias));
            }
        } else if (StringUtils.isNotBlank(uedAlias)) {
            if (uedAlias.equals("empty")) {
                upSqlString.append(StringUtils.format(" AND ( tenant_id = {} or tenant_id = 0 ) AND del_flag = 0 ", enterprise.getEnterpriseId()));
            } else {
                upSqlString.append(StringUtils.format(" AND ( {}.tenant_id = {} or {}.tenant_id = 0 ) AND {}.del_flag = 0 ", uedAlias, enterprise.getEnterpriseId(), uedAlias, uedAlias));
            }
        } else {
            //当无复杂查询控制时，阻断查询进行，保证数据安全
            sqlString.append(" AND  1 = 0 ");
            upSqlString.append(" AND  1 = 0 ");
        }

        if (StringUtils.isNotNull(params) && params instanceof BaseEntity) {
            BaseEntity baseEntity = (BaseEntity) params;

            // 系统级数据查询|更新分离模式
            if (StringUtils.isNotBlank(SYAlias)) {
                sqlString.append(StringUtils.format(" AND {}.system_id = {} ", SYAlias, baseEntity.getSystemId()));
            } else if (StringUtils.isNotBlank(SYdAlias)) {
                sqlString.append(StringUtils.format(" AND ( {}.system_id = {} or {}.system_id = 0 ) ", SYdAlias, baseEntity.getSystemId(), SYdAlias));
            } else if (StringUtils.isNotBlank(uSYAlias)) {
                if (uSYAlias.equals("empty")) {
                    upSqlString.append(StringUtils.format(" AND system_id = {} ", baseEntity.getSystemId()));
                } else {
                    upSqlString.append(StringUtils.format(" AND {}.system_id = {} ", uSYAlias, baseEntity.getSystemId()));
                }
            }

            // 站点级数据查询|更新分离模式
            if (StringUtils.isNotBlank(SIAlias)) {
                sqlString.append(StringUtils.format(" AND {}.site_id = {} ", SIAlias, baseEntity.getSiteId()));
            } else if (StringUtils.isNotBlank(SIdAlias)) {
                sqlString.append(StringUtils.format(" AND ( {}.site_id = {} or {}.site_id = 0 ) ", SIdAlias, baseEntity.getSiteId(), SIdAlias));
            } else if (StringUtils.isNotBlank(uSIAlias)) {
                if (uSIAlias.equals("empty")) {
                    upSqlString.append(StringUtils.format(" AND site_id = {} ", baseEntity.getSiteId()));
                } else {
                    upSqlString.append(StringUtils.format(" AND {}.site_id = {} ", uSIAlias, baseEntity.getSiteId()));
                }
            }

            // 库级数据查询|更新分离模式
            if (StringUtils.isNotBlank(LIAlias)) {
                sqlString.append(StringUtils.format(" AND {}.library_id = {} ", LIAlias, baseEntity.getLibraryId()));
            } else if (StringUtils.isNotBlank(LIdAlias)) {
                sqlString.append(StringUtils.format(" AND ( {}.library_id = {} or {}.library_id = 0 ) ", LIdAlias, baseEntity.getLibraryId(), LIdAlias));
            } else if (StringUtils.isNotBlank(uLIAlias)) {
                if (uLIAlias.equals("empty")) {
                    upSqlString.append(StringUtils.format(" AND library_id = {} ", baseEntity.getLibraryId()));
                } else {
                    upSqlString.append(StringUtils.format(" AND {}.library_id = {} ", uLIAlias, baseEntity.getLibraryId()));
                }
            }
        }

        if (StringUtils.isNotBlank(sqlString.toString()) || StringUtils.isNotBlank(upSqlString.toString())) {
            if (StringUtils.isNotNull(params) && params instanceof BaseEntity) {
                BaseEntity baseEntity = (BaseEntity) params;
                baseEntity.setEnterpriseId(enterprise.getEnterpriseId());
                if (StringUtils.isNotBlank(sqlString.toString())) {
                    baseEntity.getParams().put(DATA_SCOPE, " AND (" + sqlString.substring(4) + ")");
                }
                if (StringUtils.isNotBlank(upSqlString.toString())) {
                    //雪花ID生成
                    Snowflake snowflake = IdUtil.getSnowflake(RandomUtil.randomInt(1, 31), 1);
                    Long id = snowflake.nextId();
                    baseEntity.setSnowflakeId(id);
                    baseEntity.setCreateBy(user.getUserId());
                    baseEntity.setCreateDeptBy(user.getDeptId());
                    baseEntity.setCreatePostBy(user.getPostId());
                    baseEntity.setCreateIP(loginUser.getIpaddr());
                    baseEntity.setUpdateBy(user.getUserId());
                    baseEntity.setUpdateDeptBy(user.getDeptId());
                    baseEntity.setUpdatePostBy(user.getPostId());
                    baseEntity.setUpdateIP(loginUser.getIpaddr());
                    baseEntity.getParams().put(UPDATE_SCOPE, " AND (" + upSqlString.substring(4) + ")");
                }
            }
        }
    }

    /**
     * 拼接权限sql前先清空params.dataScope参数防止注入
     */
    private void clearDataScope(final JoinPoint joinPoint) {
        Object params = joinPoint.getArgs()[0];
        if (StringUtils.isNotNull(params) && params instanceof BaseEntity) {
            BaseEntity baseEntity = (BaseEntity) params;
            baseEntity.getParams().put(DATA_SCOPE, "");
            baseEntity.getParams().put(UPDATE_SCOPE, "");
        }
    }
}