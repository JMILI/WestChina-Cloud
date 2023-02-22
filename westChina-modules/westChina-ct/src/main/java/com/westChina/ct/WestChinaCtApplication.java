package com.westChina.ct;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import com.westChina.common.security.annotation.EnableCustomConfig;
import com.westChina.common.security.annotation.EnableRyFeignClients;
import com.westChina.common.swagger.annotation.EnableCustomSwagger2;

/**
 * 文件服务
 * 
 * @author westChina
 */

@EnableCustomConfig
@EnableCustomSwagger2
@EnableRyFeignClients
@SpringBootApplication
public class WestChinaCtApplication
{
    public static void main(String[] args)
    {
        SpringApplication.run(WestChinaCtApplication.class, args);
        System.out.println("(♥◠‿◠)ﾉﾞ  ct模块启动成功   ლ(´ڡ`ლ)ﾞ  \n" +
                " .-------.       ____     __        \n" +
                " |  _ _   \\      \\   \\   /  /    \n" +
                " | ( ' )  |       \\  _. /  '       \n" +
                " |(_ o _) /        _( )_ .'         \n" +
                " | (_,_).' __  ___(_ o _)'          \n" +
                " |  |\\ \\  |  ||   |(_,_)'         \n" +
                " |  | \\ `'   /|   `-'  /           \n" +
                " |  |  \\    /  \\      /           \n" +
                " ''-'   `'-'    `-..-'              ");
    }
}
