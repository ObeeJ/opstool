package database

import (
	"fmt"
	"opstool/internal/config"
	"opstool/internal/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type DB struct {
	*gorm.DB
}

func Connect(cfg *config.Config) (*DB, error) {
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=disable TimeZone=Asia/Shanghai",
		cfg.Database.Host, cfg.Database.User, cfg.Database.Password, cfg.Database.DBName, cfg.Database.Port)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	return &DB{db}, nil
}

func (db *DB) InitSchema() error {
	// AutoMigrate will create tables, missing columns, and missing indexes
	// It will not change existing column types or delete unused columns
	return db.AutoMigrate(&models.Task{}, &models.Alert{})
}
