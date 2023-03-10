package com.westChina.tenant.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.common.core.constant.TenantConstants;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.common.datasource.utils.DSUtils;
import com.westChina.tenant.api.domain.source.Source;
import com.westChina.tenant.mapper.SourceMapper;
import com.westChina.tenant.service.ISourceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 数据源 业务层处理
 *
 * @author westChina
 */
@Service
@DS(MASTER)
public class SourceServiceImpl implements ISourceService {

    @Autowired
    private SourceMapper sourceMapper;

    /**
     * 查询数据源列表
     *
     * @param source 数据源
     * @return 数据源
     */
    @Override
    public List<Source> mainSelectSourceList(Source source) {
        return sourceMapper.mainSelectSourceList(source);
    }

    /**
     * 根据源Id查询数据源信息
     *
     * @param source 数据源
     * @return 数据源
     */
    @Override
    public Source mainSelectSourceBySourceId(Source source) {
        return sourceMapper.mainSelectSourceBySourceId(source);
    }

    /**
     * 新增数据源
     *
     * @param source 数据源
     * @return 结果
     */
    @Override
    @Transactional
    @DataScope(ueAlias = "empty")
    public int mainInsertSource(Source source) {
        source.setSlave((StringUtils.equals(TenantConstants.SourceType.READ.getCode(), source.getType()) ? TenantConstants.Source.SLAVE.getCode() : TenantConstants.Source.MAIN.getCode()) + source.getSnowflakeId().toString());
        // 将数据新增的的数据源添加到数据源库
        source.setSyncType(TenantConstants.SyncType.ADD.getCode());
        DSUtils.syncDs(source);
        if (source.getType().equals(TenantConstants.SourceType.READ_WRITE.getCode())) {
            Source value = new Source(source.getSnowflakeId());
            value.setSlave(source.getSlave());
            List<Source> values = new ArrayList<>();
            values.add(value);
            source.setValues(values);
            source.setSourceId(source.getSnowflakeId());
            sourceMapper.mainBatchSeparation(source);
        }
        return sourceMapper.mainInsertSource(source);
    }

    /**
     * 修改数据源
     *
     * @param source 数据源 | sourceId 数据源Id | name 数据源名称
     * @return 结果
     */
    @Override
    public int mainUpdateSource(Source source) {
        return sourceMapper.mainUpdateSource(source);
    }

    /**
     * 启用/禁用数据源
     *
     * @param source 数据源 | sourceId 数据源Id | status 状态 | isChange 系统默认
     * @return 结果
     */
    @Override
    public int mainUpdateSourceStatus(Source source) {
        int rows = sourceMapper.mainUpdateSourceStatus(source);
        if (rows > 0) {
            DSUtils.syncDs(source);
        }
        return rows;
    }

    /**
     * 修改数据源排序
     *
     * @param source 数据源
     * @return 结果
     */
    @Override
    public int mainUpdateSourceSort(Source source) {
        return sourceMapper.mainUpdateSourceSort(source);
    }

    /**
     * 删除数据源信息
     *
     * @param source 数据源
     * @return 结果
     */
    @Override
    @Transactional
    public int mainDeleteSourceById(Source source) {
        source.setSyncType(TenantConstants.SyncType.DELETE.getCode());
        DSUtils.syncDs(source);
        sourceMapper.mainDeleteSeparationByValueId(source);
        return sourceMapper.mainDeleteSourceById(source);
    }

    /**
     * 校验数据源是否已应用于策略
     *
     * @param source 数据源
     * @return 结果 (true 已应用 false 未应用)
     */
    @Override
    public boolean mainCheckStrategySourceBySourceId(Source source) {
        return sourceMapper.mainCheckStrategySourceBySourceId(source) > 0;
    }

    /**
     * 校验写数据源是否已设置主从配置
     *
     * @param source 数据源
     * @return 结果 (true 已设置 false 未设置)
     */
    @Override
    public boolean mainCheckSeparationSourceByWriteId(Source source) {
        return sourceMapper.mainCheckSeparationSourceByWriteId(source) > 0;
    }

    /**
     * 校验读数据源是否已应用于主从配置
     *
     * @param source 数据源
     * @return 结果 (true 已应用 false 未应用)
     */
    @Override
    public boolean mainCheckSeparationSourceByReadId(Source source) {
        return sourceMapper.mainCheckSeparationSourceByReadId(source) > 0;
    }
}