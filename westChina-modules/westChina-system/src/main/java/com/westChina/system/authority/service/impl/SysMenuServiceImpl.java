package com.westChina.system.authority.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.common.core.constant.AuthorityConstants;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.utils.multiTenancy.SortUtils;
import com.westChina.common.core.utils.multiTenancy.TreeUtils;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.common.redis.utils.AuthorityUtils;
import com.westChina.common.security.utils.SecurityUtils;
import com.westChina.system.api.domain.authority.SysMenu;
import com.westChina.system.api.domain.authority.SysRole;
import com.westChina.system.api.domain.authority.SystemMenu;
import com.westChina.system.api.utilTool.SysSearch;
import com.westChina.system.authority.mapper.SysMenuMapper;
import com.westChina.system.authority.service.ISysAuthorityService;
import com.westChina.system.authority.service.ISysMenuService;
import com.westChina.system.role.mapper.SysRoleSystemMenuMapper;
import com.westChina.system.utils.route.RouteUtils;
import com.westChina.system.utils.route.RouterVo;
import com.westChina.system.utils.vo.TreeSelect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import static com.westChina.common.core.constant.TenantConstants.ISOLATE;
import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 菜单 业务层处理
 *
 * @author westChina
 */
@Service
@DS(MASTER)
public class SysMenuServiceImpl implements ISysMenuService {

    @Autowired
    private SysMenuMapper menuMapper;

    @Autowired
    private SysRoleSystemMenuMapper roleSystemMenuMapper;

    @Autowired
    private ISysAuthorityService authorityService;

    /**
     * 根据用户Id查询菜单路由
     *
     * @param menu 菜单信息 | systemId 系统Id
     * @return 菜单列表
     */
    @Override
    public List<SysMenu> getRoutes(SysMenu menu) {
        Set<SysMenu> menuSet = AuthorityUtils.getRouteCache(SecurityUtils.getEnterpriseId(), menu.getSystemId());
        Set<SysMenu> rangeSet;
        // 管理员显示所有菜单信息
        if (SecurityUtils.isAdminUser()) {
            rangeSet = authorityService.selectMenuSet(SecurityUtils.getEnterpriseId(), authorityService.selectRoleListByTenantId(SecurityUtils.getEnterpriseId()), SecurityUtils.isAdminTenant(), false, true);
        } else {
            SysRole role = new SysRole();
            role.getParams().put("userId", SecurityUtils.getUserId());
            rangeSet = authorityService.selectMenuSet(SecurityUtils.getEnterpriseId(), authorityService.selectRoleListByUserId(role), SecurityUtils.isAdminTenant(), true, true);
        }
        menuSet.retainAll(rangeSet);
        return TreeUtils.buildTree(SortUtils.sortSetToList(menuSet), "menuId", "parentId", "children", AuthorityConstants.MENU_TOP_NODE, true);
    }

    /**
     * 查询模块-菜单信息列表
     *
     * @param menu 菜单信息
     * @return 模块-菜单信息集合
     */
    @Override
    public List<TreeSelect> mainSelectSystemMenuList(SysMenu menu) {
        Set<SystemMenu> menuSet = new HashSet<>();
        Map<String, Set<SystemMenu>> map;
        if (SecurityUtils.isAdminUser()) {
            map = authorityService.assembleSystemMenuSet(SecurityUtils.getEnterpriseId(), authorityService.selectRoleListByTenantId(SecurityUtils.getEnterpriseId()), SecurityUtils.isAdminTenant(), false, true);
        } else {
            SysRole role = new SysRole();
            role.getParams().put("userId", SecurityUtils.getUserId());
            map = authorityService.assembleSystemMenuSet(SecurityUtils.getEnterpriseId(), authorityService.selectRoleListByUserId(role), SecurityUtils.isAdminTenant(), true, true);
        }
        menuSet.addAll(map.get("halfIds"));
        menuSet.addAll(map.get("wholeIds"));
        menu.getParams().put("insideIds", menuSet);
        List<SystemMenu> systemMenus = TreeUtils.buildTree(SortUtils.sortSetToList(menuMapper.mainSelectSystemMenuList(menu)), "Uid", "FUid", "children", AuthorityConstants.SYSTEM_TOP_NODE, false);
        return systemMenus.stream().map(TreeSelect::new).collect(Collectors.toList());
    }

    /**
     * 根据菜单Id查询信息
     *
     * @param menu 菜单信息 | menuId 菜单Id
     * @return 菜单信息
     */
    @Override
    public SysMenu mainSelectMenuById(SysMenu menu) {
        return menuMapper.mainSelectMenuById(menu);
    }

    /**
     * 新增保存菜单信息
     *
     * @param menu 菜单信息
     * @return 结果
     */
    @Override
    @DataScope(uedAlias = "empty")
    public int mainInsertMenu(SysMenu menu) {
        if (StringUtils.equals(AuthorityConstants.IsCommon.YES.getCode(), menu.getIsCommon()) && SecurityUtils.isAdminTenant()) {
            menu.setEnterpriseId(AuthorityConstants.COMMON_ENTERPRISE);
        }
        return menuMapper.mainInsertMenu(menu);
    }

    /**
     * 修改保存菜单信息
     *
     * @param menu 菜单信息
     * @return 结果
     */
    @Override
    @DataScope(uedAlias = "empty")
    public int mainUpdateMenu(SysMenu menu) {
        if (StringUtils.equals(AuthorityConstants.IsCommon.YES.getCode(), menu.getIsCommon()) && SecurityUtils.isAdminTenant()) {
            menu.setEnterpriseId(AuthorityConstants.COMMON_ENTERPRISE);
        }
        return menuMapper.mainUpdateMenu(menu);
    }

    /**
     * 删除菜单管理信息
     *
     * @param menu 菜单信息 | menuId 菜单Id
     * @return 结果
     */
    @Override
    public int mainDeleteMenuById(SysMenu menu) {
        return menuMapper.mainDeleteMenuById(menu);
    }

    /**
     * 校验菜单名称是否唯一
     *
     * @param menu 菜单信息 | menuId 菜单Id | parentId 父级菜单Id | menuName 菜单名称
     * @return 结果
     */
    @Override
    public boolean mainCheckMenuNameUnique(SysMenu menu) {
        if (StringUtils.isNull(menu.getMenuId())) {
            menu.setMenuId(-1L);
        }
        SysMenu info = menuMapper.mainCheckMenuNameUnique(menu);
        return !StringUtils.isNotNull(info) || info.getMenuId().longValue() == menu.getMenuId().longValue();
    }

    /**
     * 校验是否存在菜单子节点
     *
     * @param menu 菜单信息 | menuId 菜单Id
     * @return 结果
     */
    @Override
    public boolean mainHasChildByMenuId(SysMenu menu) {
        int result = menuMapper.mainHasChildByMenuId(menu);
        return result > 0;
    }

    /**
     * 校验菜单是否存在角色
     *
     * @param menu 菜单信息 | menuId 菜单Id
     * @return 结果
     */
    @Override
    @DS(ISOLATE)
    public boolean mainCheckMenuExistRole(SysMenu menu) {
        SysSearch search = new SysSearch();
        search.getSearch().put("systemMenuId", menu.getMenuId());
        int result = roleSystemMenuMapper.checkSystemMenuExistRole(search);//@param search 万用组件 | systemMenuId 系统-菜单Id
        return result > 0;
    }

    /**
     * 构建前端路由所需要的菜单
     *
     * @param menus 菜单列表
     * @return 路由列表
     */
    @Override
    public List<RouterVo> buildMenus(List<SysMenu> menus) {
        return RouteUtils.buildMenus(menus);
    }
}