from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `tasks` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '任务id',
    `name` VARCHAR(32) NOT NULL  COMMENT '任务名称',
    `create_time` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `project_id` INT NOT NULL COMMENT '所属项目',
    CONSTRAINT `fk_tasks_test_pro_cb144514` FOREIGN KEY (`project_id`) REFERENCES `test_project` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='测试任务表';
        CREATE TABLE `tasks_suite` (
    `suite_id` INT NOT NULL REFERENCES `suite` (`id`) ON DELETE CASCADE,
    `tasks_id` INT NOT NULL REFERENCES `tasks` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='任务中的套件';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `tasks_suite`;
        DROP TABLE IF EXISTS `tasks`;"""
