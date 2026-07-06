package com.westChina.common.datasource.utils;

import cn.hutool.core.collection.CollUtil;
import com.baomidou.dynamic.datasource.DynamicRoutingDataSource;
import com.baomidou.dynamic.datasource.creator.DefaultDataSourceCreator;
import com.baomidou.dynamic.datasource.spring.boot.autoconfigure.DataSourceProperty;
import com.baomidou.dynamic.datasource.toolkit.DynamicDataSourceContextHolder;
import com.westChina.common.core.constant.MessageConstant;
import com.westChina.common.core.constant.TenantConstants;
import com.westChina.common.core.exception.ServiceException;
import com.westChina.common.core.utils.IdUtils;
import com.westChina.common.core.utils.StringUtils;
import com.westChina.common.core.utils.SpringUtils;
import com.westChina.common.core.utils.bean.BeanUtils;
import com.westChina.common.message.domain.Message;
import com.westChina.common.message.service.ProducerService;
import com.westChina.tenant.api.domain.source.Source;

import javax.sql.DataSource;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * 源管理工具类
 *
 * @author westChina
 */
public class DSUtils {

    private static final Pattern DB_NAME_PATTERN = Pattern.compile("jdbc:mysql://[^/]+/([^?]+)", Pattern.CASE_INSENSITIVE);
    private static final String SLAVE_INIT_SQL_CLASSPATH = "sql/slave-init.sql";
    private static final String SLAVE_INIT_SQL_WESTSQL = "westsql/slave-init.sql";

    /**
     * 添加一个数据源到数据源库中
     *
     * @param source 数据源对象
     */
    public static void addDs(Source source) {
        if (source == null || StringUtils.isEmpty(source.getSlave())) {
            return;
        }
        String url = source.getUrl();
        if (StringUtils.isEmpty(url) && StringUtils.isNotEmpty(source.getUrlPrepend())) {
            url = source.getUrlPrepend() + StringUtils.defaultString(source.getUrlAppend());
        }
        if (StringUtils.isEmpty(url)) {
            return;
        }
        try {
            DefaultDataSourceCreator dataSourceCreator = SpringUtils.getBean(DefaultDataSourceCreator.class);
            DataSourceProperty dataSourceProperty = new DataSourceProperty();
            BeanUtils.copyProperties(source, dataSourceProperty);
            dataSourceProperty.setUrl(url);
            DataSource dataSource = SpringUtils.getBean(DataSource.class);
            DynamicRoutingDataSource ds = (DynamicRoutingDataSource) dataSource;
            dataSource = dataSourceCreator.createDataSource(dataSourceProperty);
            ds.addDataSource(source.getSlave(), dataSource);
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("数据源添加失败");
        }
    }

    /**
     * 从数据源库中删除一个数据源
     *
     * @param slave 数据源编码
     */
    public static void delDs(String slave) {
        try {
            DynamicRoutingDataSource ds = (DynamicRoutingDataSource) SpringUtils.getBean(DataSource.class);
            ds.removeDataSource(slave);
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("数据源删除失败");
        }
    }

    /**
     * 获取当前数据源库中所有数据源
     */
    public static void getDs() {
        DynamicRoutingDataSource ds = (DynamicRoutingDataSource) SpringUtils.getBean(DataSource.class);
        ds.getDataSources().keySet().forEach(System.out::println);
    }

    /**
     * 获取当前线程数据源名称
     */
    public static String getNowDsName() {
        return DynamicDataSourceContextHolder.peek();
    }

    /**
     * 异步同步数据源到数据源库
     *
     * @param source 数据源对象
     */
    public static void syncDs(Source source) {
        ProducerService producerService = SpringUtils.getBean(ProducerService.class);
        Message message = new Message(IdUtils.randomUUID(), source);
        producerService.sendMsg(message, MessageConstant.EXCHANGE_SOURCE, MessageConstant.ROUTING_KEY_SOURCE);
    }

    /**
     * 测试数据源是否可连接
     *
     * @param source 数据源对象
     */
    public static void testDs(Source source) {
        loadDriver(source);
        try (Connection dbConn = openConnection(source)) {
            // connection ok
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("数据源连接失败！");
        }
    }

    /**
     * 子库连接测试：自动创建数据库、初始化表结构并验证可连接
     */
    public static void testSlaveConnection(Source source) {
        loadDriver(source);
        createDatabaseIfNotExists(source);
        executeSlaveInitScript(source);
        testSlaveDs(source);
    }

    /**
     * 初始化子库：创建数据库并导入子库表结构
     */
    public static void initSlaveDatabase(Source source) {
        loadDriver(source);
        createDatabaseIfNotExists(source);
        executeSlaveInitScript(source);
        testSlaveDs(source);
    }

    /**
     * 测试数据源是否为可连接子库
     *
     * @param source 数据源对象
     */
    public static void testSlaveDs(Source source) {
        String error = "数据源连接失败！";
        loadDriver(source);
        try (Connection dbConn = openConnection(source)) {
            PreparedStatement statement = dbConn.prepareStatement("select table_name from information_schema.tables where table_schema = (select database())");
            ResultSet resultSet = statement.executeQuery();
            List<String> tableNameList = new ArrayList<>();
            while (resultSet.next()) {
                tableNameList.add(resultSet.getString("table_name"));
            }
            List<String> slaveTable = new ArrayList<>(Arrays.asList(TenantConstants.SLAVE_TABLE));
            slaveTable.removeAll(tableNameList);
            if (CollUtil.isNotEmpty(slaveTable)) {
                error = "请连接包含子库数据表信息的数据源！缺少表：" + String.join(", ", slaveTable);
                throw new ServiceException(error);
            }
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException(error);
        }
    }

    private static void loadDriver(Source source) {
        try {
            Class.forName(source.getDriverClassName());
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("数据源驱动加载失败！");
        }
    }

    private static Connection openConnection(Source source) throws Exception {
        return DriverManager.getConnection(source.getUrlPrepend() + source.getUrlAppend(), source.getUsername(), source.getPassword());
    }

    private static String parseDatabaseName(Source source) {
        Matcher matcher = DB_NAME_PATTERN.matcher(source.getUrlPrepend());
        if (!matcher.find()) {
            throw new ServiceException("连接地址格式错误，请使用 jdbc:mysql://host:port/数据库名");
        }
        String databaseName = matcher.group(1).trim();
        if (StringUtils.isEmpty(databaseName)) {
            throw new ServiceException("连接地址中缺少数据库名");
        }
        return databaseName;
    }

    private static String buildServerJdbcUrl(Source source) {
        String databaseName = parseDatabaseName(source);
        return source.getUrlPrepend().replace("/" + databaseName, "/") + StringUtils.defaultString(source.getUrlAppend());
    }

    private static void createDatabaseIfNotExists(Source source) {
        String databaseName = parseDatabaseName(source);
        String serverUrl = buildServerJdbcUrl(source);
        String sql = "CREATE DATABASE IF NOT EXISTS `" + databaseName + "` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci";
        try (Connection connection = DriverManager.getConnection(serverUrl, source.getUsername(), source.getPassword());
             Statement statement = connection.createStatement()) {
            statement.execute(sql);
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("创建数据库失败：" + databaseName);
        }
    }

    private static void executeSlaveInitScript(Source source) {
        try (Connection connection = openConnection(source);
             Statement statement = connection.createStatement()) {
            for (String sql : loadSlaveInitStatements()) {
                if (shouldSkipInitStatement(sql)) {
                    continue;
                }
                statement.execute(sql);
            }
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("初始化子库表结构失败！");
        }
    }

    private static boolean shouldSkipInitStatement(String sql) {
        String normalized = sql.trim().toUpperCase();
        return normalized.startsWith("DROP DATABASE")
                || normalized.startsWith("CREATE DATABASE")
                || normalized.startsWith("USE ");
    }

    private static List<String> loadSlaveInitStatements() {
        InputStream inputStream = openSlaveInitStream();
        if (inputStream == null) {
            throw new ServiceException("未找到子库初始化脚本：" + SLAVE_INIT_SQL_WESTSQL + " 或 classpath:" + SLAVE_INIT_SQL_CLASSPATH);
        }
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8))) {
            String script = reader.lines().collect(Collectors.joining("\n"));
            script = script.replaceAll("(?m)^--.*$", "");
            List<String> statements = new ArrayList<>();
            for (String part : script.split(";")) {
                String sql = part.trim();
                if (StringUtils.isNotEmpty(sql)) {
                    statements.add(sql);
                }
            }
            return statements;
        } catch (Exception e) {
            e.printStackTrace();
            throw new ServiceException("读取子库初始化脚本失败！");
        }
    }

    /**
     * 优先读取 westsql/slave-init.sql（开发环境），回退 classpath（打包后）。
     */
    private static InputStream openSlaveInitStream() {
        String projectRoot = System.getProperty("westchina.project.root", System.getenv("WESTCHINA_PROJECT_ROOT"));
        if (StringUtils.isNotEmpty(projectRoot)) {
            java.nio.file.Path westsql = java.nio.file.Paths.get(projectRoot, SLAVE_INIT_SQL_WESTSQL);
            if (java.nio.file.Files.isRegularFile(westsql)) {
                try {
                    return java.nio.file.Files.newInputStream(westsql);
                } catch (Exception ignored) {
                    // fallback to classpath
                }
            }
        }
        String userDir = System.getProperty("user.dir", "");
        if (StringUtils.isNotEmpty(userDir)) {
            java.nio.file.Path westsql = java.nio.file.Paths.get(userDir, SLAVE_INIT_SQL_WESTSQL);
            if (java.nio.file.Files.isRegularFile(westsql)) {
                try {
                    return java.nio.file.Files.newInputStream(westsql);
                } catch (Exception ignored) {
                    // fallback
                }
            }
            java.nio.file.Path parentWestsql = java.nio.file.Paths.get(userDir).getParent();
            if (parentWestsql != null) {
                java.nio.file.Path repoWestsql = parentWestsql.resolve(SLAVE_INIT_SQL_WESTSQL);
                if (java.nio.file.Files.isRegularFile(repoWestsql)) {
                    try {
                        return java.nio.file.Files.newInputStream(repoWestsql);
                    } catch (Exception ignored) {
                        // fallback
                    }
                }
            }
        }
        return DSUtils.class.getClassLoader().getResourceAsStream(SLAVE_INIT_SQL_CLASSPATH);
    }
}
