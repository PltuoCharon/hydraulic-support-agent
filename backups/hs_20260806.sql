-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: hydraulic_support
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `dict_enum`
--

DROP TABLE IF EXISTS `dict_enum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dict_enum` (
  `id` int NOT NULL AUTO_INCREMENT,
  `field` varchar(50) NOT NULL,
  `raw_value` varchar(100) NOT NULL,
  `std_value` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_field_raw` (`field`,`raw_value`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dict_enum`
--

LOCK TABLES `dict_enum` WRITE;
/*!40000 ALTER TABLE `dict_enum` DISABLE KEYS */;
INSERT INTO `dict_enum` VALUES (1,'gas_level','低瓦斯','低瓦斯'),(2,'gas_level','高瓦斯','高瓦斯'),(3,'gas_level','突出','突出'),(4,'support_type','ZY','掩护式'),(5,'support_type','ZZ','支撑式'),(6,'support_type','ZF','放顶煤');
/*!40000 ALTER TABLE `dict_enum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mining_areas`
--

DROP TABLE IF EXISTS `mining_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mining_areas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `area_name` varchar(50) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `coal_thickness` decimal(5,2) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `depth` decimal(6,2) DEFAULT NULL,
  `mining_height_min` decimal(5,2) DEFAULT NULL,
  `mining_height_max` decimal(5,2) DEFAULT NULL,
  `dip_angle` decimal(4,1) DEFAULT NULL,
  `hardness_f` decimal(5,2) DEFAULT NULL,
  `roof_category` varchar(20) DEFAULT NULL,
  `floor_pressure` varchar(50) DEFAULT NULL COMMENT '底板压力情况',
  `mine_pressure` varchar(50) DEFAULT NULL COMMENT '矿压显现程度',
  `gas_level` varchar(20) DEFAULT NULL,
  `face_length` decimal(5,2) DEFAULT NULL,
  `support_model` varchar(50) DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `mine_name` varchar(50) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_test` tinyint DEFAULT '0' COMMENT '盲测集标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mining_areas`
--

LOCK TABLES `mining_areas` WRITE;
/*!40000 ALTER TABLE `mining_areas` DISABLE KEYS */;
INSERT INTO `mining_areas` VALUES (1,'补连塔12514','补连塔12514',8.80,'浅埋大采高',277.00,NULL,NULL,2.0,2.50,'浅埋薄基岩','2.8','来压剧烈','低瓦斯',327.70,NULL,'补连塔煤矿矿压规律分析方法应用研究',NULL,NULL,'2026-07-31 07:42:45',0),(2,'补连塔22304','补连塔22304',6.80,'浅埋大采高',285.00,NULL,NULL,2.0,2.30,'浅埋薄基岩','2.5','来压明显','低瓦斯',301.00,NULL,'神东矿区世界一流矿井建设示范经验及实用技术',NULL,NULL,'2026-07-31 07:42:45',0),(3,'曹家滩122106','曹家滩122106',9.80,'超大采高',180.00,NULL,NULL,NULL,1.80,'坚硬','3.5','强矿压初次来压150m',NULL,300.00,NULL,'中国煤炭科工集团10m超大采高工作面技术装备',NULL,NULL,'2026-07-31 07:42:45',0),(4,'塔山8102','塔山8102',3.50,'坚硬顶板综放',350.00,NULL,NULL,3.0,3.00,'坚硬','4','平均来压步距16m','低瓦斯煤层涌出量大',231.00,NULL,'塔山矿特厚煤层综放开采矿压显现规律初步研究',NULL,NULL,'2026-07-31 07:42:45',0),(5,'兴隆庄4301','兴隆庄4301',9.40,'综放',420.00,NULL,NULL,5.0,2.30,'中等稳定','3.2','来压明显',NULL,176.00,NULL,'兖州矿区综放面端头及两巷超前液压支架研制与应用',NULL,NULL,'2026-07-31 07:42:45',0),(6,'鲍店1316','鲍店1316',8.74,'综放',450.00,NULL,NULL,6.5,3.50,'中等稳定','3.5','来压平缓',NULL,170.00,NULL,'兖州矿区综放面端头及两巷超前液压支架研制与应用',NULL,NULL,'2026-07-31 07:42:45',1),(7,'东滩矿','东滩矿',6.50,'综放',380.00,NULL,NULL,5.5,2.80,'中等稳定','3','来压平缓',NULL,250.00,NULL,'我国综放开采40年及展望(煤炭学报2023)',NULL,NULL,'2026-07-31 07:42:45',0),(8,'晋城寺河','晋城寺河',5.60,'高瓦斯大采高',520.00,NULL,NULL,NULL,2.50,'破碎','2.8','来压明显','高瓦斯(400m3/min)',180.00,NULL,'山西日报2004寺河煤矿报道;厚煤层开采技术文献',NULL,NULL,'2026-07-31 07:42:45',1),(9,'金鸡滩','金鸡滩',7.00,'大采高综放',200.00,NULL,NULL,1.0,1.50,'浅埋','2.5','来压平缓',NULL,300.00,NULL,'我国综放开采40年及展望(煤炭学报2023)',NULL,NULL,'2026-07-31 07:42:45',0),(10,'平朔安家岭','平朔安家岭',13.14,'浅埋硬煤',220.00,NULL,NULL,NULL,2.50,'坚硬','3','来压明显',NULL,300.00,NULL,'我国综放开采40年及展望;特大型矿井建设文献',NULL,NULL,'2026-07-31 07:42:45',1),(11,'潞安王庄','潞安王庄',NULL,'综放',480.00,NULL,NULL,NULL,3.50,'中等稳定','3.8','来压明显','涌出量大',270.00,NULL,'我国综放开采40年的重大创新(2022)',NULL,NULL,'2026-07-31 07:42:45',0),(12,'潞安屯留','潞安屯留',NULL,'综放',500.00,NULL,NULL,NULL,3.80,'中等稳定','4','来压平缓',NULL,220.00,NULL,'创新煤炭安全高效开发技术支撑特大型矿井建设',NULL,NULL,'2026-07-31 07:42:45',0),(13,'神东黄玉川','神东黄玉川',3.50,'综放缓斜',260.00,NULL,NULL,8.5,2.20,'浅埋','2.8','来压平缓',NULL,260.00,NULL,'我国综放开采40年及展望(煤炭学报2023)',NULL,NULL,'2026-07-31 07:42:45',1),(14,'淮北涡北','淮北涡北',10.00,'极软复杂',600.00,NULL,NULL,NULL,0.20,'复杂','5','来压剧烈',NULL,150.00,NULL,'我国综放开采40年及展望(煤炭学报2023)',NULL,NULL,'2026-07-31 07:42:45',0),(15,'新汶华丰1411','新汶华丰1411',6.20,'冲击地压深部',800.00,NULL,NULL,32.0,4.50,'深部','6','强冲击倾向',NULL,120.00,NULL,'基于贝叶斯神经网络的冲击地压预测(中国矿业2022)',NULL,NULL,'2026-07-31 07:42:45',0),(16,'义马千秋21121','义马千秋21121',23.40,'冲击地压',650.00,NULL,NULL,11.0,3.50,'冲击','5.5','重大冲击事故','低瓦斯',130.00,NULL,'安监总煤调[2011]171号通报;煤炭学报冲击地压文献',NULL,NULL,'2026-07-31 07:42:45',1),(17,'义马耿村13230','义马耿村13230',23.40,'冲击地压',620.00,NULL,NULL,11.0,3.20,'冲击','5','冲击停产',NULL,196.00,NULL,'冲击地压煤矿深部开采煤岩动力灾害(煤炭学报)',NULL,NULL,'2026-07-31 07:42:45',0),(18,'淮南顾桥1313(3)','淮南顾桥1313(3)',5.80,'高瓦斯复杂',NULL,NULL,NULL,5.5,NULL,NULL,NULL,NULL,'高瓦斯突出矿区',NULL,NULL,'顾桥煤矿大宽度工作面防火技术;淮南深部开采文献',NULL,NULL,'2026-07-31 07:42:45',0);
/*!40000 ALTER TABLE `mining_areas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `param_dependencies`
--

DROP TABLE IF EXISTS `param_dependencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `param_dependencies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `param_name` varchar(50) NOT NULL,
  `param_value` varchar(100) DEFAULT NULL,
  `description` text,
  `category` varchar(30) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `param_dependencies`
--

LOCK TABLES `param_dependencies` WRITE;
/*!40000 ALTER TABLE `param_dependencies` DISABLE KEYS */;
INSERT INTO `param_dependencies` VALUES (1,'初撑力系数','0.8','初撑力与工作阻力的比值','力学参数','2026-07-30 08:23:22'),(2,'支护强度公式','P = F / A','支护强度等于工作阻力除以支护面积','计算公式','2026-07-30 08:23:22'),(3,'采高裕量','0.3','支架最大采高与煤层厚度的安全差值','安全参数','2026-07-30 08:23:22'),(4,'eta','0.9','立柱机械效率','计算参数','2026-08-06 07:48:30'),(5,'safety_factor','1.2','支护强度安全系数','计算参数','2026-08-06 07:48:30');
/*!40000 ALTER TABLE `param_dependencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `support_models`
--

DROP TABLE IF EXISTS `support_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `support_models` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model` varchar(50) NOT NULL,
  `type` varchar(20) DEFAULT NULL,
  `working_resistance` int DEFAULT NULL,
  `height_min` decimal(5,2) DEFAULT NULL,
  `height_max` decimal(5,2) DEFAULT NULL,
  `manufacturer` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `center_dist` decimal(6,2) DEFAULT NULL COMMENT '支架中心距(m)',
  `canopy_len` decimal(5,2) DEFAULT NULL COMMENT '顶梁长度(m)',
  `intensity` varchar(20) DEFAULT NULL,
  `initial_force` int DEFAULT NULL,
  `floor_pressure` varchar(20) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `data_status` varchar(20) DEFAULT 'verified' COMMENT '数据置信状态: verified/suspect',
  PRIMARY KEY (`id`),
  UNIQUE KEY `model` (`model`)
) ENGINE=InnoDB AUTO_INCREMENT=147 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `support_models`
--

LOCK TABLES `support_models` WRITE;
/*!40000 ALTER TABLE `support_models` DISABLE KEYS */;
INSERT INTO `support_models` VALUES (1,'ZY12000/28/58','掩护式',12000,2.80,5.80,'郑煤机','2026-07-30 08:23:22',1.50,4.80,NULL,NULL,NULL,NULL,NULL,'verified'),(2,'ZY8000/20/40','支撑掩护式',8000,2.00,4.00,'北煤机','2026-07-30 08:23:22',1.50,4.20,NULL,NULL,NULL,NULL,NULL,'verified'),(3,'ZZ10000/25/50','支撑式',10000,2.50,5.00,'平煤机','2026-07-30 08:23:22',1.50,4.50,NULL,NULL,NULL,NULL,NULL,'verified'),(4,'ZY12000/28/62D','掩护式',12000,2.80,6.20,'郑煤机','2026-07-30 11:33:53',1.50,4.80,NULL,NULL,NULL,NULL,NULL,'verified'),(5,'ZZ9600/22/45','支撑掩护式',9600,2.20,4.50,'北煤机','2026-07-30 11:33:53',1.50,4.50,NULL,NULL,NULL,NULL,NULL,'verified'),(6,'ZF15000/25/45','放顶煤',15000,2.50,4.50,'平煤机','2026-07-30 11:33:53',1.75,5.20,NULL,NULL,NULL,NULL,NULL,'verified'),(7,'ZY6800/17/35','掩护式',6800,1.70,3.50,'郑煤机','2026-07-30 11:33:53',1.50,4.20,'0.92',NULL,NULL,NULL,' | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.9～0.94','verified'),(8,'ZZ5200/13/28','支撑掩护式',5200,1.30,2.80,'北煤机','2026-07-30 11:33:53',1.50,3.60,NULL,NULL,NULL,NULL,NULL,'verified'),(9,'ZY2200/8.5/17','掩护式',2200,0.85,1.70,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(10,'ZY3200/07/15','掩护式',3200,0.70,1.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(11,'ZY3400/08/20','掩护式',3400,0.80,2.00,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(12,'ZY4000/07/15','掩护式',4000,0.70,1.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(13,'ZY4800/8.5/19','掩护式',4800,0.85,1.90,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(14,'ZY6800/08/18','掩护式',6800,0.80,1.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(15,'ZY6800/9.5/19','掩护式',6800,0.95,1.90,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(16,'ZY9200/09/18D','掩护式',9200,0.90,1.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(17,'ZY6800/09/18','掩护式',6800,0.90,1.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(18,'ZY6800/08/15.5','掩护式',6800,0.80,1.55,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.7~0.8',5064,'2.5~3.6',NULL,'采矿与岩层控制工程学报2013','verified'),(19,'ZYB4400/8.5/18','掩护式',4400,0.85,1.80,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.766',3860,NULL,9.22,'专利CN102094647B','verified'),(20,'ZJY2400/8.5/15.5','掩护式(急倾斜)',2400,0.85,1.55,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'中国矿业期刊','verified'),(21,'ZY3400/09/22','掩护式',3400,0.90,2.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.5',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.45～0.55','verified'),(22,'ZY3400/11/25','掩护式',3400,1.10,2.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(23,'ZY3400/12/28','掩护式',3400,1.20,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(24,'ZY4000/09/21','掩护式',4000,0.90,2.10,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(25,'ZY4000/10/24','掩护式',4000,1.00,2.40,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(26,'ZY4000/12/28','掩护式',4000,1.20,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(27,'ZY5200/10/24','掩护式',5200,1.00,2.40,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(28,'ZY5200/13/27','掩护式',5200,1.30,2.70,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(29,'ZY5200/14/28','掩护式',5200,1.40,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(30,'ZY6800/11/22','掩护式',6800,1.10,2.20,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(31,'ZY6800/12/25','掩护式',6800,1.20,2.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(32,'ZY6800/14/28','掩护式',6800,1.40,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(33,'ZY6800/14/32','掩护式',6800,1.40,3.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'1.02',NULL,NULL,NULL,'液压支架型号大全(百度文库) | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.97～1.07','verified'),(34,'ZY6800/15/32','掩护式',6800,1.50,3.20,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(35,'ZY6800/18/38','掩护式',6800,1.80,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(36,'ZY8000/13/26','掩护式',8000,1.30,2.60,NULL,'2026-07-31 07:31:24',1.50,NULL,'1.0~1.12',5716,'2.7~4.1',NULL,'采矿与岩层控制工程学报2014','verified'),(37,'ZY3000/13/22','支撑掩护式',3000,1.30,2.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.48~0.54',2616,'1.13~1.27',8.2,'乐山市政府公开技术文件','verified'),(38,'ZY8800/18/40','掩护式',8800,1.80,4.00,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'液压支架型号大全(百度文库)','verified'),(39,'ZD3200/17/35','支撑式',3200,1.70,3.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'液压支架型号大全(百度文库)','verified'),(40,'ZY9000/14/28','掩护式',9000,1.40,2.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(41,'ZY9000/17/35','掩护式',9000,1.70,3.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(42,'ZY9000/20/40','掩护式',9000,2.00,4.00,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.0225',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.0～1.045','verified'),(43,'ZY9000/22/45','掩护式',9000,2.20,4.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(44,'ZY10000/13/26D','掩护式',10000,1.30,2.60,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(45,'ZY10000/18/38D','掩护式',10000,1.80,3.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(46,'ZY12000/14/28D','掩护式',12000,1.40,2.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(47,'ZY12000/20/40','掩护式',12000,2.00,4.00,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.305',NULL,NULL,NULL,'郑州煤机综机产品列表 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.30～1.31','verified'),(48,'ZY12000/22/45D','掩护式',12000,2.20,4.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(49,'ZY12000/15/30D','掩护式',12000,1.50,3.00,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.17~1.26',NULL,NULL,NULL,'液压支架安全阀频繁开启研究(汉斯)','verified'),(50,'ZY12000/28/62','掩护式',12000,2.80,6.20,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.36~1.40',NULL,NULL,NULL,'大比尺采场模型试验研究','verified'),(51,'ZY12000/28/64D','掩护式',12000,2.80,6.40,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.27~1.32',10390,'1.55~3.98',NULL,'采矿与岩层控制工程学报2011','verified'),(52,'ZY13000/27/60D','掩护式',13000,2.70,6.00,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.41~1.46',10400,NULL,NULL,'煤炭工程期刊2025','verified'),(53,'ZY13000/28/63','掩护式',13000,2.80,6.30,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.25',NULL,NULL,NULL,'郑州煤机综机产品列表 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.24～1.26','verified'),(54,'ZY13000/26/55D','掩护式',13000,2.60,5.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(55,'ZY13000/30/65D','掩护式',13000,3.00,6.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(56,'ZY15000/22/45D','掩护式',15000,2.20,4.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(57,'ZY15000/28/55D','掩护式',15000,2.80,5.50,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(58,'ZY15000/33/72D','掩护式',15000,3.30,7.20,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(59,'ZY18000/25/45D','掩护式',18000,2.50,4.50,NULL,'2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(60,'ZY18000/30/65D','掩护式',18000,3.00,6.50,NULL,'2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(61,'ZY18000/32/70D','掩护式',18000,3.20,7.00,NULL,'2026-07-31 07:31:24',2.05,NULL,'1.63',NULL,NULL,NULL,'大比尺采场模型试验研究','verified'),(62,'ZY18000/34.5/74D','掩护式',18000,3.45,7.40,NULL,'2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(63,'ZY21000/38/82D','掩护式',21000,3.80,8.20,NULL,'2026-07-31 07:31:24',2.05,NULL,'1.45',NULL,NULL,NULL,'煤炭科学技术2023','verified'),(64,'ZY21000/33.5/70D','掩护式',21000,3.35,7.00,NULL,'2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(65,'ZY21000/36.5/80D','掩护式',21000,3.65,8.00,NULL,'2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(66,'ZY26000/40/88D','掩护式',26000,4.00,8.80,NULL,'2026-07-31 07:31:24',2.40,NULL,'1.71~1.83',19782,NULL,99,'煤炭科学技术(8.8m工作面)','verified'),(67,'ZYA29000/45/100D','掩护式',29000,4.50,10.00,NULL,'2026-07-31 07:31:24',2.40,NULL,'1.88~1.95',23368,NULL,NULL,'煤炭学报2024(10m超大采高)','verified'),(68,'ZZ6400/18/38','支撑掩护式',6400,1.80,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.895',NULL,NULL,NULL,'郑州煤机综机产品列表 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.89～0.9','verified'),(69,'ZZ7800/22/45','支撑掩护式',7800,2.20,4.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(70,'ZZ8000/14/26','支撑掩护式',8000,1.40,2.60,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'采矿与岩层控制工程学报2014','verified'),(71,'ZZS5300/14/28','支撑掩护式',5300,1.40,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,4515,NULL,15.8,'专利CN102094647B','verified'),(72,'ZZ13000/28/60','支撑掩护式',13000,2.80,6.00,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.24~1.28',10128,'1.0~3.5',NULL,'煤炭学报(坚硬顶板压架事故)','verified'),(73,'ZZ20000/28/62D','支撑掩护式',20000,2.80,6.20,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.7~1.76',NULL,NULL,61.5,'郑煤机集团官网','verified'),(74,'ZF3800/17/28','放顶煤',3800,1.70,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'急倾斜厚煤层水平分段放顶煤(期刊)','verified'),(75,'ZF6400/19/30','放顶煤',6400,1.90,3.00,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(76,'ZF7000/18/28','放顶煤',7000,1.80,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'综采液压支架支撑阻力计算(百度文库)','verified'),(77,'ZF7800/16/28','放顶煤',7800,1.60,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(78,'ZF9000/19/38','放顶煤',9000,1.90,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(79,'ZFS6500/18/35','放顶煤(双输送机)',6500,1.80,3.50,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.82~0.85',5711,'2.1',NULL,'潞安环能招股说明书2006','verified'),(80,'ZF10000/20/38','放顶煤',10000,2.00,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'液压支架型号大全(百度文库)','verified'),(81,'ZF10000/25/38','放顶煤',10000,2.50,3.80,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.04',NULL,NULL,NULL,'塔山矿综放矿压研究 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.04','verified'),(82,'ZF13000/25/38','放顶煤',13000,2.50,3.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,10096,NULL,NULL,'ZF13000/25/38技术改造(豆丁)','verified'),(83,'ZF13000/22/42','放顶煤',13000,2.20,4.20,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑州煤机综机产品列表','verified'),(84,'ZF15000/27.5/42','放顶煤',15000,2.75,4.20,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.46',NULL,NULL,NULL,'采矿与岩层控制工程学报2011 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.46','verified'),(85,'ZF18000/21/38D','放顶煤',18000,2.10,3.80,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'重装公司使用纪实(微信)','verified'),(86,'ZF18000/23/42D','放顶煤',18000,2.30,4.20,NULL,'2026-07-31 07:31:24',1.75,NULL,'1.64~1.7',15270,'4.2',NULL,'山东煤炭科技2026','verified'),(87,'ZFY18000/28/53D','放顶煤(两柱掩护)',18000,2.80,5.30,NULL,'2026-07-31 07:31:24',2.05,NULL,'1.51~1.55',14718,NULL,NULL,'河南科技(龙王沟选型)','verified'),(88,'ZF21000/25/42D','放顶煤',21000,2.50,4.20,NULL,'2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'我国综放开采40年及展望','verified'),(89,'ZF6800/19/38','放顶煤',6800,1.90,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'我国综放开采40年及展望','verified'),(90,'ZY2200/11/22','掩护式',2200,1.10,2.20,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(91,'ZY3400/10/17','掩护式',3400,1.00,1.70,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(92,'ZY4000/08/20','掩护式',4000,0.80,2.00,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(93,'ZY4000/11/25','掩护式',4000,1.10,2.50,'郑煤机','2026-07-31 07:31:24',1.50,NULL,'0.585',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.53～0.64','verified'),(94,'ZY4000/15/32','掩护式',4000,1.50,3.20,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(95,'ZY4000/16/35','掩护式',4000,1.60,3.50,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(96,'ZY4000/17.5/38','掩护式',4000,1.75,3.80,'郑煤机','2026-07-31 07:31:24',1.50,NULL,'0.7',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.7','verified'),(97,'ZY4800/09/21','掩护式',4800,0.90,2.10,'郑煤机','2026-07-31 07:31:24',1.50,NULL,'0.625',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.57～0.68','verified'),(98,'ZY5200/11/26','掩护式',5200,1.10,2.60,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(99,'ZY5200/14/32','掩护式',5200,1.40,3.20,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(100,'ZY5200/17/35','掩护式',5200,1.70,3.50,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(101,'ZY5200/18/38','掩护式',5200,1.80,3.80,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(102,'ZY5200/19/43','掩护式',5200,1.90,4.30,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(103,'ZY6800/20/42','掩护式',6800,2.00,4.20,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(104,'ZY6800/21/45','掩护式',6800,2.10,4.50,'郑煤机','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(105,'ZY6800/24/50','掩护式',6800,2.40,5.00,'郑煤机','2026-07-31 07:31:24',1.50,NULL,'0.94',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.93～0.95','verified'),(106,'ZY9000/11/22D','掩护式',9000,1.10,2.20,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(107,'ZY9000/15/32','掩护式',9000,1.50,3.20,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(108,'ZY9000/18/38','掩护式',9000,1.80,3.80,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(109,'ZY9000/24/50','掩护式',9000,2.40,5.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,'1.055',NULL,NULL,NULL,'郑煤机型谱 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.02～1.09','verified'),(110,'ZY9000/25.5/55','掩护式',9000,2.55,5.50,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(111,'ZY10500/11/22D','掩护式',10500,1.10,2.20,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(112,'ZY10000/17/35D','掩护式',10000,1.70,3.50,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(113,'ZY12000/16/32D','掩护式',12000,1.60,3.20,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(114,'ZY12000/25/50D','掩护式',12000,2.50,5.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(115,'ZY12000/18/50D','掩护式',12000,1.80,5.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(116,'ZY13000/28/60D','掩护式',13000,2.80,6.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(117,'ZY15000/26/50D','掩护式',15000,2.60,5.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(118,'ZY15000/29/60D','掩护式',15000,2.90,6.00,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(119,'ZY15000/29/63D','掩护式',15000,2.90,6.30,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(120,'ZY15000/33/67D','掩护式',15000,3.30,6.70,'郑煤机','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(121,'ZY18000/26.5/50D','掩护式',18000,2.65,5.00,'郑煤机','2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(122,'ZY18000/28/55D','掩护式',18000,2.80,5.50,'郑煤机','2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(123,'ZY18000/29/60D','掩护式',18000,2.90,6.00,'郑煤机','2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(124,'ZY21000/34/72D','掩护式',21000,3.40,7.20,'郑煤机','2026-07-31 07:31:24',2.05,NULL,NULL,NULL,NULL,NULL,'郑煤机型谱','verified'),(125,'ZY9000/20/40D','掩护式',9000,2.00,4.00,'平煤机','2026-07-31 07:31:24',1.50,NULL,'1.0225',NULL,NULL,NULL,'煤矿机械2023(千米埋深1.5m中心距设计) | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.0～1.045','verified'),(126,'ZY12000/32.5/72','掩护式',12000,3.25,7.20,'北京开采设计分院','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'国产大采高液压支架研究现状(矿业科学学报)','verified'),(127,'ZY5200/12/28','掩护式',5200,1.20,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.695',3879,'0.8~1.45',NULL,'宁夏发改委稳评报告(技术特征表) | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.62～0.77','verified'),(128,'ZYG5200/12/28','掩护式(过渡)',5200,1.20,2.80,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.57',3876,NULL,NULL,'宁夏发改委稳评报告 | 国家矿山安监局公开评估报告 原始值:0.50～0.64','verified'),(129,'ZYT5200/15/30D','端头支架',5200,1.50,3.00,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.525',NULL,NULL,NULL,'宁夏发改委稳评报告 | 国家矿山安监局公开评估报告 原始值:0.45～0.6','verified'),(130,'ZY10800/28/63D','掩护式',10800,2.80,6.30,'国产','2026-07-31 07:31:24',1.75,NULL,'1.08',NULL,NULL,NULL,'煤炭科学技术(大采高智能工作面跟机控制) | 找煤机网郑煤机型谱表(搜狐转载) 原始值:1.04～1.12','verified'),(131,'ZY18900/36/72D','掩护式',18900,3.60,7.20,'兰煤机','2026-07-31 07:31:24',NULL,NULL,'1.585',NULL,NULL,70,'兰州煤机产品页(支护强度1.55-1.62,70t) | 林州重机官网产品页 原始值:1.55～1.62MPa, 70t | 厂商标称3.2-8.0m与型号编码36/72不符,高度以厂商标称为准','suspect'),(132,'ZY13000/25/50D','掩护式',13000,2.50,5.00,'三一重装','2026-07-31 07:31:24',1.75,NULL,NULL,NULL,NULL,NULL,'浅谈ZY13000/25/50D研制(缸径420mm)','verified'),(133,'ZY8000/17.5/35','掩护式',8000,1.75,3.50,'三一重装','2026-07-31 07:31:24',1.75,NULL,NULL,7912,NULL,NULL,'煤矿工作面设计(安全工程专业)','verified'),(134,'ZF7200/20/32','放顶煤',7200,2.00,3.20,'三一重装','2026-07-31 07:31:24',1.50,NULL,'0.98',6182,NULL,NULL,'综放工作面安装作业规程 | 找煤机网郑煤机型谱表(搜狐转载) 原始值:0.95～1.01','verified'),(135,'ZF6400/16/30Q','放顶煤(大倾角)',6400,1.60,3.00,'河南能源重装','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'河南能源重装公司报道','verified'),(136,'ZFA10000/22/35D','放顶煤(低位)',10000,2.20,3.50,'河南能源重装','2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'河南能源重装公司报道','verified'),(137,'ZF8600/20/38','放顶煤',8600,2.00,3.80,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'上榆泉煤矿机电装备简介','verified'),(138,'ZY6600/19/39','掩护式',6600,1.90,3.90,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'上榆泉煤矿机电装备简介','verified'),(139,'ZY2000/06/15','掩护式',2000,0.60,1.50,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'煤矿支护手册','verified'),(140,'ZYL2200/06/17','掩护式',2200,0.60,1.70,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'煤矿支护手册','verified'),(141,'ZYQ1700/09/22','掩护式(轻型)',1700,0.90,2.20,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'煤矿支护手册','verified'),(142,'ZYQ1860/12/26','掩护式(轻型)',1860,1.20,2.60,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'煤矿支护手册','verified'),(143,'ZY2000/10/26','掩护式',2000,1.00,2.60,NULL,'2026-07-31 07:31:24',1.50,NULL,NULL,NULL,NULL,NULL,'煤矿支护手册','verified'),(144,'ZYR200/16/32','掩护式',200,1.60,3.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.47~0.53',1595,NULL,7.02,'煤矿支护手册','verified'),(145,'ZY2500/13/32','掩护式',2500,1.30,3.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.41~0.45',1960,NULL,8.3,'煤矿支护手册','verified'),(146,'ZY3200/13/32','掩护式',3200,1.30,3.20,NULL,'2026-07-31 07:31:24',1.50,NULL,'0.485',2354,NULL,8.7,'煤矿支护手册 | 《煤矿支护手册》支护强度0.4~0.57MPa取中值,重8.7t; 开滦矿资料0.47~0.58MPa佐证','verified');
/*!40000 ALTER TABLE `support_models` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `support_parts`
--

DROP TABLE IF EXISTS `support_parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `support_parts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_id` int NOT NULL,
  `part_name` varchar(50) DEFAULT NULL,
  `part_type` varchar(20) DEFAULT NULL,
  `material` varchar(50) DEFAULT NULL,
  `quantity` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `model_id` (`model_id`),
  CONSTRAINT `support_parts_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `support_models` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `support_parts`
--

LOCK TABLES `support_parts` WRITE;
/*!40000 ALTER TABLE `support_parts` DISABLE KEYS */;
INSERT INTO `support_parts` VALUES (1,1,'立柱','液压元件','27SiMn',4),(2,1,'千斤顶','液压元件','27SiMn',8),(3,2,'顶梁','结构件','Q690',1),(4,6,'立柱','液压元件','27SiMn',4),(5,6,'千斤顶','液压元件','27SiMn',8),(6,6,'顶梁','结构件','Q690',1),(7,6,'掩护梁','结构件','Q690',1),(8,6,'底座','结构件','Q690',1),(9,6,'连杆','结构件','Q460',2),(10,6,'推移千斤顶','液压元件','27SiMn',2),(11,6,'平衡千斤顶','液压元件','27SiMn',2),(12,6,'伸缩梁','结构件','Q690',1),(13,6,'护帮板','结构件','Q460',2),(14,6,'侧护板','结构件','Q460',4),(15,6,'控制器','电控元件','电子',1),(16,6,'传感器','检测元件','电子',4),(17,6,'电磁阀','液压元件','不锈钢',8),(18,1,'立柱','液压元件','27SiMn',4),(19,1,'千斤顶','液压元件','27SiMn',8),(20,1,'顶梁','结构件','Q690',1),(21,1,'掩护梁','结构件','Q690',1),(22,1,'底座','结构件','Q690',1),(23,1,'连杆','结构件','Q460',2),(24,1,'推移千斤顶','液压元件','27SiMn',2),(25,1,'平衡千斤顶','液压元件','27SiMn',2),(26,1,'控制器','电控元件','电子',1),(27,1,'传感器','检测元件','电子',4),(28,1,'电磁阀','液压元件','不锈钢',8),(29,4,'立柱','液压元件','27SiMn',4),(30,4,'千斤顶','液压元件','27SiMn',8),(31,4,'顶梁','结构件','Q690',1),(32,4,'掩护梁','结构件','Q690',1),(33,4,'底座','结构件','Q690',1),(34,4,'连杆','结构件','Q460',2),(35,4,'推移千斤顶','液压元件','27SiMn',2),(36,4,'平衡千斤顶','液压元件','27SiMn',2),(37,4,'控制器','电控元件','电子',1),(38,4,'传感器','检测元件','电子',4),(39,4,'电磁阀','液压元件','不锈钢',8),(40,65,'立柱','液压元件','27SiMn',4),(41,65,'千斤顶','液压元件','27SiMn',8),(42,65,'顶梁','结构件','Q690',1),(43,65,'掩护梁','结构件','Q690',1),(44,65,'底座','结构件','Q690',1),(45,65,'连杆','结构件','Q460',2),(46,65,'推移千斤顶','液压元件','27SiMn',2),(47,65,'平衡千斤顶','液压元件','27SiMn',2),(48,65,'伸缩梁','结构件','Q690',1),(49,65,'护帮板','结构件','Q460',2),(50,65,'侧护板','结构件','Q460',4),(51,65,'控制器','电控元件','电子',1),(52,65,'传感器','检测元件','电子',4),(53,65,'电磁阀','液压元件','不锈钢',8),(54,63,'立柱','液压元件','27SiMn',4),(55,63,'千斤顶','液压元件','27SiMn',8),(56,63,'顶梁','结构件','Q690',1),(57,63,'掩护梁','结构件','Q690',1),(58,63,'底座','结构件','Q690',1),(59,63,'连杆','结构件','Q460',2),(60,63,'推移千斤顶','液压元件','27SiMn',2),(61,63,'平衡千斤顶','液压元件','27SiMn',2),(62,63,'伸缩梁','结构件','Q690',1),(63,63,'护帮板','结构件','Q460',2),(64,63,'侧护板','结构件','Q460',4),(65,63,'控制器','电控元件','电子',1),(66,63,'传感器','检测元件','电子',4),(67,63,'电磁阀','液压元件','不锈钢',8),(68,3,'立柱','液压元件','27SiMn',4),(69,3,'千斤顶','液压元件','27SiMn',8),(70,3,'顶梁','结构件','Q690',1),(71,3,'掩护梁','结构件','Q690',1),(72,3,'底座','结构件','Q690',1),(73,3,'连杆','结构件','Q460',2),(74,3,'推移千斤顶','液压元件','27SiMn',2),(75,3,'平衡千斤顶','液压元件','27SiMn',2),(76,5,'立柱','液压元件','27SiMn',4),(77,5,'千斤顶','液压元件','27SiMn',8),(78,5,'顶梁','结构件','Q690',1),(79,5,'掩护梁','结构件','Q690',1),(80,5,'底座','结构件','Q690',1),(81,5,'连杆','结构件','Q460',2),(82,5,'推移千斤顶','液压元件','27SiMn',2),(83,5,'平衡千斤顶','液压元件','27SiMn',2);
/*!40000 ALTER TABLE `support_parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `working_conditions`
--

DROP TABLE IF EXISTS `working_conditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `working_conditions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `area_id` int NOT NULL,
  `support_model_id` int DEFAULT NULL,
  `working_face_name` varchar(50) DEFAULT NULL,
  `coal_thickness` decimal(5,2) DEFAULT NULL,
  `roof_condition` varchar(20) DEFAULT NULL,
  `floor_condition` varchar(20) DEFAULT NULL,
  `dip_angle` decimal(4,1) DEFAULT NULL,
  `gas_level` varchar(20) DEFAULT NULL,
  `mining_height` decimal(5,2) DEFAULT NULL,
  `daily_output` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `area_id` (`area_id`),
  KEY `support_model_id` (`support_model_id`),
  CONSTRAINT `working_conditions_ibfk_1` FOREIGN KEY (`area_id`) REFERENCES `mining_areas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `working_conditions_ibfk_2` FOREIGN KEY (`support_model_id`) REFERENCES `support_models` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `working_conditions`
--

LOCK TABLES `working_conditions` WRITE;
/*!40000 ALTER TABLE `working_conditions` DISABLE KEYS */;
INSERT INTO `working_conditions` VALUES (4,1,63,'补连塔12514工作面',8.80,'中等稳定','坚硬',2.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(5,2,63,'补连塔22304工作面',6.80,'中等稳定','坚硬',2.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(6,3,63,'曹家滩122106工作面',9.80,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(7,4,6,'塔山8102工作面',3.50,'中等稳定','坚硬',3.0,'低瓦斯煤层涌出量大',4.00,8000,'2026-08-04 11:36:02'),(8,5,6,'兴隆庄4301工作面',9.40,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(9,6,6,'鲍店1316工作面',8.74,'中等稳定','坚硬',6.5,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(10,7,6,'东滩矿工作面',6.50,'中等稳定','坚硬',5.5,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(11,8,63,'晋城寺河工作面',5.60,'中等稳定','坚硬',5.0,'高瓦斯(400m3/min)',4.00,8000,'2026-08-04 11:36:02'),(12,9,63,'金鸡滩工作面',7.00,'中等稳定','坚硬',1.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(13,10,1,'平朔安家岭工作面',13.14,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(14,11,6,'潞安王庄工作面',NULL,'中等稳定','坚硬',5.0,'涌出量大',4.00,8000,'2026-08-04 11:36:02'),(15,12,6,'潞安屯留工作面',NULL,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(16,13,6,'神东黄玉川工作面',3.50,'中等稳定','坚硬',8.5,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(17,14,1,'淮北涡北工作面',10.00,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(18,15,67,'新汶华丰1411工作面',6.20,'中等稳定','坚硬',32.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(19,16,67,'义马千秋21121工作面',23.40,'中等稳定','坚硬',11.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(20,17,67,'义马耿村13230工作面',23.40,'中等稳定','坚硬',11.0,'低瓦斯',4.00,8000,'2026-08-04 11:36:02'),(21,18,1,'淮南顾桥1313(3)工作面',5.80,'中等稳定','坚硬',5.5,'高瓦斯突出矿区',4.00,8000,'2026-08-04 11:36:02'),(22,1,63,'补连塔12514工作面',8.80,'浅埋薄基岩','坚硬',2.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(23,2,63,'补连塔22304工作面',6.80,'浅埋薄基岩','坚硬',2.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(24,3,63,'曹家滩122106工作面',9.80,'坚硬','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(25,4,6,'塔山8102工作面',3.50,'坚硬','坚硬',3.0,'低瓦斯煤层涌出量大',4.00,8000,'2026-08-04 11:39:24'),(26,5,6,'兴隆庄4301工作面',9.40,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(27,6,6,'鲍店1316工作面',8.74,'中等稳定','坚硬',6.5,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(28,7,6,'东滩矿工作面',6.50,'中等稳定','坚硬',5.5,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(29,8,63,'晋城寺河工作面',5.60,'破碎','坚硬',5.0,'高瓦斯(400m3/min)',4.00,8000,'2026-08-04 11:39:24'),(30,9,63,'金鸡滩工作面',7.00,'浅埋','坚硬',1.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(31,10,1,'平朔安家岭工作面',13.14,'坚硬','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(32,11,6,'潞安王庄工作面',NULL,'中等稳定','坚硬',5.0,'涌出量大',4.00,8000,'2026-08-04 11:39:24'),(33,12,6,'潞安屯留工作面',NULL,'中等稳定','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(34,13,6,'神东黄玉川工作面',3.50,'浅埋','坚硬',8.5,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(35,14,1,'淮北涡北工作面',10.00,'复杂','坚硬',5.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(36,15,67,'新汶华丰1411工作面',6.20,'深部','坚硬',32.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(37,16,67,'义马千秋21121工作面',23.40,'冲击','坚硬',11.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(38,17,67,'义马耿村13230工作面',23.40,'冲击','坚硬',11.0,'低瓦斯',4.00,8000,'2026-08-04 11:39:24'),(39,18,1,'淮南顾桥1313(3)工作面',5.80,'中等稳定','坚硬',5.5,'高瓦斯突出矿区',4.00,8000,'2026-08-04 11:39:24');
/*!40000 ALTER TABLE `working_conditions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-06 19:19:58
