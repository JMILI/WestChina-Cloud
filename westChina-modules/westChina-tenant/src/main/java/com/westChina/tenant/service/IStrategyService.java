package com.westChina.tenant.service;

import java.util.List;

import com.westChina.tenant.api.domain.strategy.Strategy;

/**
 * 数据源策略 业务层
 *
 * @author westChina
 */
public interface IStrategyService {

    /**
     * 查询数据源策略列表
     *
     * @param strategy 数据源策略
     * @return 数据源策略集合
     */
    public List<Strategy> mainSelectStrategyList(Strategy strategy);

    /**
     * 查询数据源策略列表（排除停用）
     *
     * @param strategy 数据源策略
     * @return 数据源策略集合
     */
    public List<Strategy> mainSelectStrategyListExclude(Strategy strategy);

    /**
     * 查询数据源策略
     *
     * @param strategy 数据源策略
     * @return 数据源策略
     */
    public Strategy mainSelectStrategyById(Strategy strategy);

    /**
     * 新增数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    public int mainInsertStrategy(Strategy strategy);

    /**
     * 修改数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    public int mainUpdateStrategy(Strategy strategy);

    /**
     * 修改数据源策略排序
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    public int mainUpdateStrategySort(Strategy strategy);

    /**
     * 批量删除数据源策略
     *
     * @param strategy 数据源策略
     * @return 结果
     */
    public int mainDeleteStrategyByIds(Strategy strategy);
}