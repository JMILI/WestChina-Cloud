package com.westChina.tenant.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.tenant.api.domain.source.Source;
import com.westChina.tenant.mapper.SourceMapper;
import com.westChina.tenant.service.ISeparationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 数据源 业务层处理
 *
 * @author westChina
 */
@Service
@DS(MASTER)
public class SeparationServiceImpl implements ISeparationService {

    @Autowired
    private SourceMapper sourceMapper;

    /**
     * 查询 只读 数据源集合
     *
     * @param source 数据源
     * @return 数据源集合
     */
    @Override
    public List<Source> mainSelectContainReadList(Source source) {
        return sourceMapper.mainSelectContainReadList(source);
    }

    /**
     * 查询 含写 数据源集合
     *
     * @param source 数据源
     * @return 数据源集合
     */
    @Override
    public List<Source> mainSelectContainWriteList(Source source) {
        return sourceMapper.mainSelectContainWriteList(source);
    }

    /**
     * 根据Id查询数据源及其分离策略
     *
     * @param source 数据源
     * @return 数据源
     */
    @Override
    public Source mainSelectSeparationById(Source source) {
        return sourceMapper.mainSelectSeparationById(source);
    }

    /**
     * 修改数据源
     *
     * @param source 数据源
     * @return 结果
     */
    @Override
    @Transactional
    public int mainUpdateSeparation(Source source) {
        int k= sourceMapper.mainDeleteSeparationBySourceId(source);
        if (source.getValues() != null && source.getValues().size() > 0) {
            sourceMapper.mainBatchSeparation(source);
        }
        return k;
    }
}