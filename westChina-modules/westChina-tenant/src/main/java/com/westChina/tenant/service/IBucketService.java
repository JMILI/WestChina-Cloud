package com.westChina.tenant.service;

import com.westChina.tenant.domain.Bucket;

import java.util.List;

/**
 * 对象存储，存储租户的桶信息 业务层
 * 
 * @author jm
 */
public interface IBucketService {

    /**
     * 查询对象存储，存储租户的桶信息列表
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 对象存储，存储租户的桶信息集合
     */
    public List<Bucket> selectBucketList(Bucket bucket);

    /**
     * 查询对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 对象存储，存储租户的桶信息
     */
    public Bucket selectBucketByBucketId(Bucket bucket);

    /**
     * 新增对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    public int insertBucket(Bucket bucket);

    /**
     * 修改对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    public int updateBucket(Bucket bucket);

    /**
     * 修改对象存储，存储租户的桶信息排序
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    public int updateBucketSort(Bucket bucket);

    /**
     * 删除对象存储，存储租户的桶信息信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 结果
     */
    public int deleteBucketByBucketId(Bucket bucket);

    /**
     * 批量删除对象存储，存储租户的桶信息
     *
     * @param bucket 对象存储，存储租户的桶信息 | params.Ids 需要删除的对象存储，存储租户的桶信息Ids组
     * @return 结果
     */
    public int deleteBucketByBucketIds(Bucket bucket);
    /**
     * 查询对象存储，存储租户的桶信息,根据租户id查询
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 对象存储，存储租户的桶信息
     */
    Bucket selectBucketByBucketTenantId(Bucket bucket);
    /**
     * 根据企业账号 查询该账号所拥有的的minio 桶
     * @param enterpriseName 企业账号，或称租户账号
     * @return Bucket
     */
    Bucket getBucketNameByEnterpriseName(String enterpriseName);
}