package com.westChina.common.security.utils;

import java.util.Collection;
import java.util.List;

import com.westChina.common.core.constant.CacheConstants;
import com.westChina.common.core.utils.SpringUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.redis.service.RedisService;
import com.westChina.system.api.domain.dict.SysDictData;

/**
 * 字典工具类
 *
 * @author ruoyi
 */
public class DictUtils
{
    /**
     * 设置字典缓存
     *
     * @param key 参数键
     * @param dictDatas 字典数据列表
     */
    public static void setDictCache(String key, List<SysDictData> dictDatas)
    {
        SpringUtils.getBean(RedisService.class).setCacheObject(getCacheKey(key), dictDatas);
    }

    /**
     * 获取字典缓存
     *
     * @param key 参数键
     * @return dictDatas 字典数据列表
     */
    public static List<SysDictData> getDictCache(String key)
    {
        Object cacheObj = SpringUtils.getBean(RedisService.class).getCacheObject(getCacheKey(key));
        if (StringUtils.isNotNull(cacheObj))
        {
            List<SysDictData> dictDatas = StringUtils.cast(cacheObj);
            return dictDatas;
        }
        return null;
    }

    /**
     * 删除指定字典缓存
     * 
     * @param key 字典键
     */
    public static void removeDictCache(String key)
    {
        SpringUtils.getBean(RedisService.class).deleteObject(getCacheKey(key));
    }

    /**
     * 清空字典缓存
     */
    public static void clearDictCache()
    {
        Collection<String> keys = SpringUtils.getBean(RedisService.class).keys(CacheConstants.SYS_DICT_KEY + "*");
        SpringUtils.getBean(RedisService.class).deleteObject(keys);
    }

    /**
     * 设置cache key
     *
     * @param configKey 参数键
     * @return 缓存键key
     */
    public static String getCacheKey(String configKey)
    {
        return CacheConstants.SYS_DICT_KEY + configKey;
    }
}
