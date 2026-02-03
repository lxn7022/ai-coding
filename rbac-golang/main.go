package main

import (
	"log"
	"rbac-golang/config"
	"rbac-golang/database"
	"rbac-golang/routes"
)

func main() {
	// 加载配置
	cfg := config.GetConfig()

	// 初始化数据库
	if err := database.InitDB(cfg); err != nil {
		log.Fatalf("数据库初始化失败: %v", err)
	}

	// 初始化默认数据
	if err := database.InitDefaultData(); err != nil {
		log.Fatalf("默认数据初始化失败: %v", err)
	}

	// 配置路由
	router := routes.SetupRouter(cfg)

	// 启动服务器
	log.Printf("RBAC权限管理系统启动中，监听端口: %s", cfg.Server.Port)
	log.Printf("API文档地址: http://localhost:%s/api/v1", cfg.Server.Port)
	log.Println("默认管理员账号: admin / admin123")

	if err := router.Run(":" + cfg.Server.Port); err != nil {
		log.Fatalf("服务器启动失败: %v", err)
	}
}
