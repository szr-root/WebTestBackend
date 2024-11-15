from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '用户id',
    `username` VARCHAR(32) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(128) NOT NULL  COMMENT '密码',
    `nickname` VARCHAR(32) NOT NULL  COMMENT '用户昵称',
    `email` VARCHAR(255) NOT NULL  COMMENT '邮箱' DEFAULT '',
    `mobile` VARCHAR(128)   COMMENT '手机号' DEFAULT '',
    `is_active` BOOL NOT NULL  COMMENT '是否激活' DEFAULT 1,
    `is_superuser` BOOL NOT NULL  COMMENT '是否是超级管理员' DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='用户表';
CREATE TABLE IF NOT EXISTS `test_project` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '项目id',
    `name` VARCHAR(32) NOT NULL  COMMENT '项目名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL COMMENT '项目负责人',
    CONSTRAINT `fk_test_pro_users_e0824dce` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='测试表';
CREATE TABLE IF NOT EXISTS `project_module` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '模块id',
    `name` VARCHAR(32) NOT NULL  COMMENT '模块名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `project_id` INT NOT NULL COMMENT '所属项目',
    CONSTRAINT `fk_project__test_pro_6a25756e` FOREIGN KEY (`project_id`) REFERENCES `test_project` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='项目模块表';
CREATE TABLE IF NOT EXISTS `test_env` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '环境id',
    `name` VARCHAR(32) NOT NULL  COMMENT '环境名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `host` VARCHAR(255) NOT NULL  COMMENT '环境地址',
    `global_vars` JSON NOT NULL  COMMENT '全局变量',
    `project_id` INT NOT NULL COMMENT '所属项目',
    CONSTRAINT `fk_test_env_test_pro_f21b8019` FOREIGN KEY (`project_id`) REFERENCES `test_project` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='测试环境表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
