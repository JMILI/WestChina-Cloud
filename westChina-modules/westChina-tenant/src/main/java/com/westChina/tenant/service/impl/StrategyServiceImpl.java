package com.westChina.tenant.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.common.core.constant.OrganizeConstants;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.tenant.api.domain.strategy.Strategy;
import com.westChina.tenant.mapper.StrategyMapper;
import com.westChina.tenant.service.IStrategyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 数据源策略 业务层处理
 *
 * @author westChina
 */
@Service
@DS(MASTER)
public class StrategyServiceImpl implements IStrategyService {

    @Autowired
    private StrategyMapper strategyMapper;

    /**
     * 查询数据源策略列表
     *
     * @param strategy 数据源策略
     * @return 数据源策略
     */
    @Override
    public List<Strategy> mainSelectStrategyList(Strategy strategy) {
        return strategyMapper.mainSelectStrategyList(strategy);
    }

    /**
     * 查询数据源策略列表（排除停用）
     *
     * @param strategy 数据源策略
     * @return 数据源策略集合
     */
    @Override
    public List<Strategy> mainSelectStrategyListExclude(Strategy strategy) {
        return strategyMapper.mainSelectStrategyListExclude(strategy);
    }

    /**
     * 查询数据源策略
     *
     * @param strategy 数据源策略
     * @return 数据源策略
     */
    @Override
    public Strategy mainSelectStrategyById(Strategy strategy) {
        return strategyMapper.mainSelectStrategyById(strategy);
    }

    /**
     * 新增数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    @Override
    @Transactional
    @DataScope(ueAlias = "empty")
    public int mainInsertStrategy(Strategy strategy) {
        int rows = strategyMapper.mainInsertStrategy(strategy);
        if (strategy.getValues() != null && strategy.getValues().size() > 0) {
            /* 获取生成雪花Id，并赋值给主键，加入至子表对应外键中 */
            strategy.setStrategyId(strategy.getSnowflakeId());
            strategyMapper.mainBatchSource(strategy);
        }
        return rows;
    }

    /**
     * 修改数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    @Override
    @Transactional
    public int mainUpdateStrategy(Strategy strategy) {
        if (!StringUtils.equals(OrganizeConstants.STATUS_UPDATE_OPERATION, strategy.getUpdateType())) {
            strategyMapper.mainDeleteSourceByStrategyId(strategy);
            if (strategy.getValues() != null && strategy.getValues().size() > 0) {
                strategyMapper.mainBatchSource(strategy);
            }
        }
        return strategyMapper.mainUpdateStrategy(strategy);
    }

    /**
     * 修改数据源策略排序
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    @Override
    public int mainUpdateStrategySort(Strategy strategy) {
        return strategyMapper.mainUpdateStrategySort(strategy);
    }

    /**
     * 批量删除数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    @Override
    @Transactional
    public int mainDeleteStrategyByIds(Strategy strategy) {
        strategyMapper.mainDeleteSourceByStrategyIds(strategy);
        return strategyMapper.mainDeleteStrategyByIds(strategy);
    }
}