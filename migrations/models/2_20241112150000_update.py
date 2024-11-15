from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `cases` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT ' 用例id',
    `name` VARCHAR(32) NOT NULL  COMMENT '用例名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `steps` JSON NOT NULL  COMMENT '用例执行步骤',
    `project_id` INT NOT NULL COMMENT '所属项目',
    CONSTRAINT `fk_cases_test_pro_2cfe9d6c` FOREIGN KEY (`project_id`) REFERENCES `test_project` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='测试用例';
        CREATE TABLE IF NOT EXISTS `suite` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '套件id',
    `name` VARCHAR(32) NOT NULL  COMMENT '套件名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `suite_setup_step` JSON NOT NULL  COMMENT '前置执行步骤',
    `suite_type` VARCHAR(50) NOT NULL  COMMENT '套件类型' DEFAULT '业务流',
    `project_id` INT NOT NULL COMMENT '所属项目',
    CONSTRAINT `fk_suite_test_pro_f09d60fe` FOREIGN KEY (`project_id`) REFERENCES `test_project` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='测试套件';
        CREATE TABLE IF NOT EXISTS `suitetocase` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '关联id',
    `sort` INT NOT NULL  COMMENT '用例执行排序',
    `skip` BOOL NOT NULL  COMMENT '用例在某个套件是否跳过' DEFAULT 0,
    `cases_id` INT NOT NULL COMMENT '所属用例',
    `suite_id` INT NOT NULL COMMENT '所属套件',
    CONSTRAINT `fk_suitetoc_cases_debb9f78` FOREIGN KEY (`cases_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_suitetoc_suite_c8245a14` FOREIGN KEY (`suite_id`) REFERENCES `suite` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='中间表';
        CREATE TABLE `suite_project_module` (
    `projectmodule_id` INT NOT NULL REFERENCES `project_module` (`id`) ON DELETE CASCADE,
    `suite_id` INT NOT NULL REFERENCES `suite` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='所属模块';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `suite_project_module`;
        DROP TABLE IF EXISTS `cases`;
        DROP TABLE IF EXISTS `suite`;
        DROP TABLE IF EXISTS `suitetocase`;"""
