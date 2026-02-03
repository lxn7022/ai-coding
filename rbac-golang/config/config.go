package config

import (
	"os"
	"time"
)

// Config 应用配置
type Config struct {
	Server   ServerConfig
	Database DatabaseConfig
	JWT      JWTConfig
}

// ServerConfig 服务器配置
type ServerConfig struct {
	Port string
	Mode string // debug, release, test
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Driver string
	DSN    string
}

// JWTConfig JWT配置
type JWTConfig struct {
	Secret     string
	ExpireTime time.Duration
}

// GetConfig 获取配置
func GetConfig() *Config {
	return &Config{
		Server: ServerConfig{
			Port: getEnv("SERVER_PORT", "8080"),
			Mode: getEnv("GIN_MODE", "debug"),
		},
		Database: DatabaseConfig{
			Driver: getEnv("DB_DRIVER", "sqlite"),
			DSN:    getEnv("DB_DSN", "rbac.db"),
		},
		JWT: JWTConfig{
			Secret:     getEnv("JWT_SECRET", "rbac-secret-key-change-in-production"),
			ExpireTime: 24 * time.Hour,
		},
	}
}

// getEnv 获取环境变量，如果不存在则返回默认值
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
