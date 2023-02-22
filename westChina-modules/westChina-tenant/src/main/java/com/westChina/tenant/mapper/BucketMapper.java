package com.westChina.tenant.mapper;

import com.westChina.common.datascope.annotation.DataScope;
import com.westChina.tenant.domain.Bucket;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 对象存储，存储租户的桶信息 数据层
 *
 * @author jm
 */
public interface BucketMapper {

    /**
     * 查询对象存储，存储租户的桶信息列表
     * 访问控制 e 租户查询
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 对象存储，存储租户的桶信息集合
     */
    @DataScope( eAlias = "e" )
    public List<Bucket> selectBucketList(Bucket bucket);

    /**
     * 查询对象存储，存储租户的桶信息
     * 访问控制 e 租户查询
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 对象存储，存储租户的桶信息
     */
    @DataScope( eAlias = "e" )
    public Bucket selectBucketByBucketId(Bucket bucket);

    /**
     * 新增对象存储，存储租户的桶信息
    * 访问控制 empty 租户更新（无前缀）
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int insertBucket(Bucket bucket);

    /**
     * 修改对象存储，存储租户的桶信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateBucket(Bucket bucket);

    /**
     * 修改对象存储，存储租户的桶信息排序
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param bucket 对象存储，存储租户的桶信息
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int updateBucketSort(Bucket bucket);

    /**
     * 删除对象存储，存储租户的桶信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteBucketByBucketId(Bucket bucket);

    /**
     * 批量删除对象存储，存储租户的桶信息
     * 访问控制 empty 租户更新（无前缀）
     *
     * @param bucket 对象存储，存储租户的桶信息 | params.Ids 需要删除的对象存储，存储租户的桶信息Ids组
     * @return 结果
     */
    @DataScope( ueAlias = "empty" )
    public int deleteBucketByBucketIds(Bucket bucket);
    /**
     * 查询对象存储，存储租户的桶信息
     * 访问控制 e 租户查询
     *
     * @param bucket 对象存储，存储租户的桶信息 | bucketId 对象存储，存储租户的桶信息Id
     * @return 对象存储，存储租户的桶信息
     */
    @DataScope( eAlias = "e" )
    Bucket selectBucketByBucketTenantId(Bucket bucket);

    /**
     * 根据企业账号 查询该账号所拥有的的minio 桶
     * @param enterpriseName 企业账号，或称租户账号
     * @return
     */
    @DataScope( eAlias = "e" )
    Bucket selectBucketNameByEnterpriseName(@Param("enterpriseName") String enterpriseName);
}