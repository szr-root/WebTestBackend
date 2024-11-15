from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `suite_project_module`;
        ALTER TABLE `suite` ADD `modules_id` INT   COMMENT '所属模块';
        ALTER TABLE `suite` ADD CONSTRAINT `fk_suite_project__0829a924` FOREIGN KEY (`modules_id`) REFERENCES `project_module` (`id`) ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `suite` DROP FOREIGN KEY `fk_suite_project__0829a924`;
        ALTER TABLE `suite` DROP COLUMN `modules_id`;
        CREATE TABLE `suite_project_module` (
    `suite_id` INT NOT NULL REFERENCES `suite` (`id`) ON DELETE CASCADE,
    `projectmodule_id` INT NOT NULL REFERENCES `project_module` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='所属模块';"""
