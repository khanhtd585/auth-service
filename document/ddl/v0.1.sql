-- Schema: auth (optional)  
CREATE DATABASE IF NOT EXISTS `auth` CHARACTER SET = 'utf8mb4' COLLATE = 'utf8mb4_bin';  
USE `auth`;  

-- Table: users  
CREATE TABLE IF NOT EXISTS `users` (  
  `id` CHAR(36) NOT NULL PRIMARY KEY,  
  `email` VARCHAR(255) UNIQUE,  
  `user_name` VARCHAR(255),  
  `status` ENUM('active','disabled','banned','pending') NOT NULL DEFAULT 'pending',  
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),  
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),  
  `last_login_at` DATETIME(3),  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;  

-- Table: user_credentials  
-- Stores password hashes (or other credential types). Keep secret fields hashed/encrypted.  
CREATE TABLE IF NOT EXISTS `user_credentials` (  
  `id` CHAR(36) NOT NULL PRIMARY KEY,  
  `user_id` CHAR(36) NOT NULL,  
  `hash` TEXT NOT NULL,  
  `algorithm` VARCHAR(128) NOT NULL, -- e.g. "argon2id$v=19$m=65536,t=3,p=4"  
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),  
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),  
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,  
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,  
  INDEX `idx_user_credentials_user_id` (`user_id`)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;  
