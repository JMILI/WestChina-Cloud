package com.westChina.system.api.utilTool;

import com.westChina.common.core.web.domain.BaseEntity;

import java.util.HashMap;
import java.util.Map;

/**
 * 万能通用组件
 *
 * @author westChina
 */
public class SysSearch extends BaseEntity {

    /**
     * 请求参数
     */
    private Map<String, Object> search;

    public Map<String, Object> getSearch() {
        if (search == null) {
            search = new HashMap<>();
        }
        return search;
    }

    public void setSearch(Map<String, Object> search) {
        this.search = search;
    }
}
