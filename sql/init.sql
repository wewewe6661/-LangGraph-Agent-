-- 初始化数据库：创建模拟业务数据表和分析日志表。
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS smart_data_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_data_agent;

-- 客户表：用于分析城市、会员等级、客户来源等维度。
CREATE TABLE IF NOT EXISTS customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL COMMENT '客户姓名',
    city VARCHAR(50) NOT NULL COMMENT '所在城市',
    gender VARCHAR(10) NOT NULL COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    member_level VARCHAR(20) NOT NULL COMMENT '会员等级',
    registered_at DATE NOT NULL COMMENT '注册日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户表';

-- 商品表：用于分析商品品类、价格带和销售表现。
CREATE TABLE IF NOT EXISTS products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category VARCHAR(50) NOT NULL COMMENT '商品类别',
    price DECIMAL(12, 2) NOT NULL COMMENT '商品单价',
    cost DECIMAL(12, 2) NOT NULL COMMENT '商品成本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 订单表：核心事实表，用于趋势、排行、占比和原因分析。
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    customer_id BIGINT NOT NULL COMMENT '客户ID',
    product_id BIGINT NOT NULL COMMENT '商品ID',
    city VARCHAR(50) NOT NULL COMMENT '下单城市',
    quantity INT NOT NULL COMMENT '购买数量',
    total_amount DECIMAL(12, 2) NOT NULL COMMENT '订单总金额',
    order_status VARCHAR(20) NOT NULL COMMENT '订单状态：paid已支付、cancelled已取消、refunded已退款',
    channel VARCHAR(30) NOT NULL COMMENT '订单渠道',
    order_date DATE NOT NULL COMMENT '下单日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_orders_date (order_date),
    INDEX idx_orders_city (city),
    INDEX idx_orders_status (order_status),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_product (product_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 分析日志表：保存每一次自然语言查询，供前端展示历史记录。
CREATE TABLE IF NOT EXISTS analysis_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    question VARCHAR(500) NOT NULL COMMENT '用户自然语言问题',
    generated_sql TEXT NOT NULL COMMENT '生成并校验后的SQL',
    analysis TEXT NOT NULL COMMENT '大模型生成的业务分析结论',
    chart_type VARCHAR(20) NOT NULL COMMENT '推荐图表类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析日志表';

INSERT INTO customers (id, customer_name, city, gender, age, member_level, registered_at) VALUES
(1, '张伟', '北京', '男', 32, '黄金会员', '2023-01-12'),
(2, '李娜', '上海', '女', 28, '白银会员', '2023-03-05'),
(3, '王强', '广州', '男', 36, '铂金会员', '2022-11-18'),
(4, '赵敏', '深圳', '女', 25, '普通会员', '2023-07-22'),
(5, '陈晨', '杭州', '女', 31, '黄金会员', '2023-02-14'),
(6, '刘洋', '成都', '男', 29, '白银会员', '2023-04-09'),
(7, '周杰', '南京', '男', 41, '铂金会员', '2022-09-30'),
(8, '孙倩', '武汉', '女', 27, '普通会员', '2023-08-16'),
(9, '吴迪', '西安', '男', 34, '黄金会员', '2023-05-21'),
(10, '郑欣', '苏州', '女', 30, '白银会员', '2023-06-11')
ON DUPLICATE KEY UPDATE
    customer_name = VALUES(customer_name),
    city = VALUES(city),
    gender = VALUES(gender),
    age = VALUES(age),
    member_level = VALUES(member_level),
    registered_at = VALUES(registered_at);

INSERT INTO products (id, product_name, category, price, cost) VALUES
(1, '智能手表 Pro', '数码电子', 1299.00, 780.00),
(2, '无线蓝牙耳机', '数码电子', 399.00, 180.00),
(3, '空气炸锅', '家用电器', 599.00, 320.00),
(4, '扫地机器人', '家用电器', 1999.00, 1250.00),
(5, '男士运动鞋', '服饰鞋包', 499.00, 210.00),
(6, '女士双肩包', '服饰鞋包', 359.00, 140.00),
(7, '美白精华液', '美妆个护', 289.00, 90.00),
(8, '保湿面霜', '美妆个护', 199.00, 70.00),
(9, '精品咖啡豆', '食品饮料', 99.00, 45.00),
(10, '低糖燕麦片', '食品饮料', 59.00, 28.00)
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name),
    category = VALUES(category),
    price = VALUES(price),
    cost = VALUES(cost);

INSERT INTO orders (order_no, customer_id, product_id, city, quantity, total_amount, order_status, channel, order_date) VALUES
('OD20260401001', 1, 1, '北京', 1, 1299.00, 'paid', '小程序', '2026-04-01'),
('OD20260402001', 2, 2, '上海', 2, 798.00, 'paid', 'APP', '2026-04-02'),
('OD20260403001', 3, 4, '广州', 1, 1999.00, 'paid', '官网', '2026-04-03'),
('OD20260405001', 4, 7, '深圳', 3, 867.00, 'paid', '直播间', '2026-04-05'),
('OD20260406001', 5, 3, '杭州', 1, 599.00, 'paid', 'APP', '2026-04-06'),
('OD20260407001', 6, 9, '成都', 5, 495.00, 'paid', '小程序', '2026-04-07'),
('OD20260409001', 7, 5, '南京', 2, 998.00, 'paid', 'APP', '2026-04-09'),
('OD20260411001', 8, 10, '武汉', 4, 236.00, 'cancelled', '官网', '2026-04-11'),
('OD20260413001', 9, 6, '西安', 1, 359.00, 'paid', '直播间', '2026-04-13'),
('OD20260415001', 10, 8, '苏州', 2, 398.00, 'paid', 'APP', '2026-04-15'),
('OD20260418001', 1, 4, '北京', 1, 1999.00, 'paid', 'APP', '2026-04-18'),
('OD20260421001', 2, 3, '上海', 2, 1198.00, 'paid', '小程序', '2026-04-21'),
('OD20260424001', 3, 1, '广州', 1, 1299.00, 'refunded', '官网', '2026-04-24'),
('OD20260426001', 4, 2, '深圳', 3, 1197.00, 'paid', '直播间', '2026-04-26'),
('OD20260428001', 5, 7, '杭州', 2, 578.00, 'paid', 'APP', '2026-04-28'),

('OD20260501001', 6, 1, '成都', 1, 1299.00, 'paid', 'APP', '2026-05-01'),
('OD20260502001', 7, 4, '南京', 1, 1999.00, 'paid', '官网', '2026-05-02'),
('OD20260503001', 8, 2, '武汉', 2, 798.00, 'paid', '小程序', '2026-05-03'),
('OD20260505001', 9, 5, '西安', 1, 499.00, 'paid', '直播间', '2026-05-05'),
('OD20260506001', 10, 6, '苏州', 2, 718.00, 'paid', 'APP', '2026-05-06'),
('OD20260508001', 1, 3, '北京', 1, 599.00, 'paid', '小程序', '2026-05-08'),
('OD20260510001', 2, 8, '上海', 3, 597.00, 'paid', 'APP', '2026-05-10'),
('OD20260512001', 3, 9, '广州', 6, 594.00, 'paid', '官网', '2026-05-12'),
('OD20260514001', 4, 10, '深圳', 8, 472.00, 'paid', '直播间', '2026-05-14'),
('OD20260516001', 5, 7, '杭州', 1, 289.00, 'cancelled', 'APP', '2026-05-16'),
('OD20260518001', 6, 4, '成都', 1, 1999.00, 'paid', '官网', '2026-05-18'),
('OD20260520001', 7, 1, '南京', 1, 1299.00, 'paid', 'APP', '2026-05-20'),
('OD20260522001', 8, 2, '武汉', 1, 399.00, 'paid', '小程序', '2026-05-22'),
('OD20260524001', 9, 6, '西安', 2, 718.00, 'paid', '直播间', '2026-05-24'),
('OD20260526001', 10, 3, '苏州', 1, 599.00, 'paid', 'APP', '2026-05-26'),
('OD20260528001', 1, 5, '北京', 2, 998.00, 'paid', '小程序', '2026-05-28'),

('OD20260601001', 2, 1, '上海', 1, 1299.00, 'paid', 'APP', '2026-06-01'),
('OD20260602001', 3, 4, '广州', 1, 1999.00, 'paid', '官网', '2026-06-02'),
('OD20260603001', 4, 7, '深圳', 2, 578.00, 'paid', '直播间', '2026-06-03'),
('OD20260605001', 5, 8, '杭州', 2, 398.00, 'paid', 'APP', '2026-06-05'),
('OD20260607001', 6, 9, '成都', 4, 396.00, 'paid', '小程序', '2026-06-07'),
('OD20260609001', 7, 5, '南京', 1, 499.00, 'paid', 'APP', '2026-06-09'),
('OD20260611001', 8, 10, '武汉', 5, 295.00, 'paid', '官网', '2026-06-11'),
('OD20260613001', 9, 6, '西安', 1, 359.00, 'cancelled', '直播间', '2026-06-13'),
('OD20260615001', 10, 3, '苏州', 2, 1198.00, 'paid', 'APP', '2026-06-15'),
('OD20260618001', 1, 4, '北京', 1, 1999.00, 'paid', '官网', '2026-06-18'),
('OD20260621001', 2, 2, '上海', 3, 1197.00, 'paid', '小程序', '2026-06-21'),
('OD20260624001', 3, 1, '广州', 1, 1299.00, 'paid', 'APP', '2026-06-24'),
('OD20260627001', 4, 7, '深圳', 3, 867.00, 'paid', '直播间', '2026-06-27'),
('OD20260630001', 5, 8, '杭州', 1, 199.00, 'refunded', 'APP', '2026-06-30'),

('OD20260701001', 6, 9, '成都', 3, 297.00, 'paid', '小程序', '2026-07-01'),
('OD20260703001', 7, 4, '南京', 1, 1999.00, 'paid', '官网', '2026-07-03'),
('OD20260705001', 8, 2, '武汉', 2, 798.00, 'paid', 'APP', '2026-07-05'),
('OD20260707001', 9, 5, '西安', 1, 499.00, 'paid', '直播间', '2026-07-07'),
('OD20260709001', 10, 6, '苏州', 1, 359.00, 'paid', 'APP', '2026-07-09'),
('OD20260711001', 1, 1, '北京', 1, 1299.00, 'paid', 'APP', '2026-07-11'),
('OD20260713001', 2, 3, '上海', 1, 599.00, 'paid', '小程序', '2026-07-13'),
('OD20260715001', 3, 7, '广州', 1, 289.00, 'cancelled', '官网', '2026-07-15'),
('OD20260717001', 4, 10, '深圳', 6, 354.00, 'paid', '直播间', '2026-07-17'),
('OD20260719001', 5, 8, '杭州', 2, 398.00, 'paid', 'APP', '2026-07-19'),
('OD20260721001', 6, 4, '成都', 1, 1999.00, 'paid', '官网', '2026-07-21'),
('OD20260723001', 7, 1, '南京', 1, 1299.00, 'paid', 'APP', '2026-07-23'),
('OD20260725001', 8, 2, '武汉', 3, 1197.00, 'paid', '小程序', '2026-07-25'),
('OD20260727001', 9, 6, '西安', 2, 718.00, 'paid', '直播间', '2026-07-27'),
('OD20260729001', 10, 3, '苏州', 1, 599.00, 'paid', 'APP', '2026-07-29')
ON DUPLICATE KEY UPDATE
    customer_id = VALUES(customer_id),
    product_id = VALUES(product_id),
    city = VALUES(city),
    quantity = VALUES(quantity),
    total_amount = VALUES(total_amount),
    order_status = VALUES(order_status),
    channel = VALUES(channel),
    order_date = VALUES(order_date);
