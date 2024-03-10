package com.westChina.tenant.service.impl;

import com.baomidou.dynamic.datasource.annotation.DS;
import com.westChina.tenant.domain.Bucket;
import com.westChina.tenant.mapper.BucketMapper;
import com.westChina.tenant.service.IBucketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

import static com.westChina.common.core.constant.TenantConstants.MASTER;

/**
 * 对象存储，存储租户的桶信息 业务层处理
 *
 * @author jm
 */
@Service
@DS(MASTER)
public class BucketServiceImpl implements IBucketService {

    @Autowired
    private BucketMapper bucketMapper;

    /**
     * 查询对象存储，存储租户的桶信息列表
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 对象存储，存储租户的桶信息
     */
    @Override
    public List<Bucket> selectBucketList(Bucket bucket)
    {
        return bucketMapper.selectBucketList(bucket);
    }

    /**
     * 查询对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 对象存储，存储租户的桶信息
     */
    @Override
    public Bucket selectBucketByBucketId(Bucket bucket)
    {
        return bucketMapper.selectBucketByBucketId(bucket);
    }

    /**
     * 新增对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @Override
    public int insertBucket(Bucket bucket)
    {
        return bucketMapper.insertBucket(bucket);
    }

    /**
     * 修改对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @Override
    public int updateBucket(Bucket bucket)
    {
        return bucketMapper.updateBucket(bucket);
    }

    /**
     * 修改对象存储，存储租户的桶信息排序
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @Override
    public int updateBucketSort(Bucket bucket){
        return bucketMapper.updateBucketSort(bucket);
    }

    /**
     * 删除对象存储，存储租户的桶信息信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 结果
     */
    @Override
    public int deleteBucketByBucketId(Bucket bucket)
    {
        return bucketMapper.deleteBucketByBucketId(bucket);
    }

    /**
     * 批量删除对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | params.Ids 需要删除的对象存储，存储租户的桶信息Ids组
     * @return 结果
     */
    @Override
    public int deleteBucketByBucketIds(Bucket bucket)
    {
        return bucketMapper.deleteBucketByBucketIds(bucket);
    }

    @Override
    public Bucket selectBucketByBucketTenantId(Bucket bucket) {
        return bucketMapper.selectBucketByBucketTenantId(bucket);
    }
    /**
     * 根据企业账号 查询该账号所拥有的的minio 桶
     * @param enterpriseName 企业账号，或称租户账号
     * @return Bucket
     */
    @Override
    public Bucket getBucketNameByEnterpriseName(String enterpriseName) {
        return bucketMapper.selectBucketNameByEnterpriseName(enterpriseName);
    }
}