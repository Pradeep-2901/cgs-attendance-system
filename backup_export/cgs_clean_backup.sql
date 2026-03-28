-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: cgs
-- ------------------------------------------------------
-- Server version	8.0.42

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
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `check_in_time` time DEFAULT NULL,
  `check_in_latitude` varchar(50) DEFAULT NULL,
  `check_in_longitude` varchar(50) DEFAULT NULL,
  `check_in_address` varchar(255) DEFAULT NULL,
  `image_path_checkin` varchar(255) DEFAULT NULL,
  `check_out_time` time DEFAULT NULL,
  `check_out_latitude` varchar(50) DEFAULT NULL,
  `check_out_longitude` varchar(50) DEFAULT NULL,
  `check_out_address` varchar(255) DEFAULT NULL,
  `image_path_checkout` varchar(255) DEFAULT NULL,
  `attendance_type` enum('Regular','Comp-Off') NOT NULL DEFAULT 'Regular',
  `compoff_credited` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`attendance_id`),
  KEY `idx_attendance_user_date` (`user_id`,`date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,'emp001','2025-09-28','17:27:15','13.0482176','80.2553856','Ward 111, Zone 9 Teynampet, Chennai, Tamil Nadu, 600001, India','checkin_emp001_20250928_172714.jpg','18:48:10','13.0482176','80.2553856','Ward 111, Zone 9 Teynampet, Chennai, Tamil Nadu, 600001, India','checkout_emp001_20250928_184809.jpg','Regular',0),(2,'emp003','2025-09-28','18:34:04','13.0482176','80.2553856','Ward 111, Zone 9 Teynampet, Chennai, Tamil Nadu, 600001, India','checkin_emp003_20250928_183403.jpg','18:34:17','13.0482176','80.2553856','Ward 111, Zone 9 Teynampet, Chennai, Tamil Nadu, 600001, India','checkout_emp003_20250928_183417.jpg','Regular',0),(3,'emp003','2025-10-01','09:49:55','12.9073152','80.0882688','Varun Avenue, Plot no. 27, Balaji Nagar, New Perungalathur, Chennai, Perungalathur, Tamil Nadu 600063, India','checkin_emp003_20251001_094955.jpg','09:50:15','12.9073152','80.0882688','Varun Avenue, Plot no. 27, Balaji Nagar, New Perungalathur, Chennai, Perungalathur, Tamil Nadu 600063, India','checkout_emp003_20251001_095015.jpg','Regular',0),(4,'emp001','2025-12-23','17:51:33','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkin_emp001_20251223_175133.jpg','17:54:07','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkout_emp001_20251223_175406.jpg','Regular',0),(5,'emp001','2025-12-24','17:02:09','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkin_emp001_20251224_170208.jpg','17:04:25','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkout_emp001_20251224_170424.jpg','Regular',0),(6,'emp002','2025-12-24','17:50:39','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkin_emp002_20251224_175039.jpg','17:51:28','12.9302528','80.1112064','12/25, West, Lakshmipuram, Tambaram, Chennai, Tamil Nadu 600045, India','checkout_emp002_20251224_175128.jpg','Regular',0),(7,'emp001','2026-01-09','10:32:41','13.0351104','80.232448','45, Burkit Rd, T. Nagar, Chennai, Tamil Nadu 600017, India','checkin_emp001_20260109_103240.jpg','10:53:33','13.0351104','80.232448','45, Burkit Rd, T. Nagar, Chennai, Tamil Nadu 600017, India','checkout_emp001_20260109_105333.jpg','Regular',0);
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company_settings`
--

DROP TABLE IF EXISTS `company_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_settings` (
  `setting_id` int NOT NULL AUTO_INCREMENT,
  `setting_name` varchar(50) NOT NULL,
  `setting_value` varchar(255) NOT NULL,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`setting_id`),
  UNIQUE KEY `setting_name` (`setting_name`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `company_settings_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_settings`
--

LOCK TABLES `company_settings` WRITE;
/*!40000 ALTER TABLE `company_settings` DISABLE KEYS */;
INSERT INTO `company_settings` VALUES (1,'office_address','Old Pallavaram, Chennai, 600117, Tamil Nadu','2026-01-09 04:58:16',NULL),(2,'office_lat','13.035110','2026-01-09 05:01:30',NULL),(3,'office_lon','80.232448','2026-01-09 05:01:30',NULL),(4,'office_radius','700','2026-01-09 05:01:30',NULL),(5,'company_name','CGS Green Sustainergy','2025-10-08 13:30:23',NULL),(11,'geofencing_enabled','true','2025-10-08 13:32:21',NULL);
/*!40000 ALTER TABLE `company_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compoff_requests`
--

DROP TABLE IF EXISTS `compoff_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compoff_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) NOT NULL,
  `work_date` date NOT NULL,
  `reason` text NOT NULL,
  `status` enum('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
  `request_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` varchar(10) DEFAULT NULL,
  `review_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  UNIQUE KEY `uc_user_work_date` (`user_id`,`work_date`),
  CONSTRAINT `fk_compoff_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compoff_requests`
--

LOCK TABLES `compoff_requests` WRITE;
/*!40000 ALTER TABLE `compoff_requests` DISABLE KEYS */;
INSERT INTO `compoff_requests` VALUES (1,'emp001','2025-10-05','for future purposes','Approved','2025-09-28 16:37:52','adm001','2025-09-28 16:40:10'),(2,'emp002','2025-10-05','ff','Approved','2025-09-29 08:51:15','adm001','2025-09-29 08:51:37'),(3,'emp003','2026-01-11','compensatory off','Approved','2026-01-09 05:32:12','adm001','2026-01-09 05:32:42'),(4,'emp001','2026-01-11','comp off','Approved','2026-01-09 05:46:15','adm001','2026-01-09 05:46:36');
/*!40000 ALTER TABLE `compoff_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `geofence_requests`
--

DROP TABLE IF EXISTS `geofence_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `geofence_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) NOT NULL,
  `requested_lat` decimal(10,8) NOT NULL,
  `requested_lon` decimal(11,8) NOT NULL,
  `request_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `reviewed_by` varchar(10) DEFAULT NULL,
  `review_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `fk_geofence_user` (`user_id`),
  CONSTRAINT `fk_geofence_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `geofence_requests`
--

LOCK TABLES `geofence_requests` WRITE;
/*!40000 ALTER TABLE `geofence_requests` DISABLE KEYS */;
INSERT INTO `geofence_requests` VALUES (1,'emp001',13.04821760,80.25538560,'2025-09-28 13:15:54','approved','adm001','2025-09-28 13:17:12'),(2,'emp002',12.95918380,80.16108770,'2025-09-29 08:46:17','approved','adm001','2025-09-29 08:49:09');
/*!40000 ALTER TABLE `geofence_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `holidays`
--

DROP TABLE IF EXISTS `holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `holidays` (
  `holiday_id` int NOT NULL AUTO_INCREMENT,
  `holiday_date` date NOT NULL,
  `holiday_name` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`holiday_id`),
  UNIQUE KEY `holiday_date` (`holiday_date`),
  KEY `idx_holidays_date` (`holiday_date`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `holidays`
--

LOCK TABLES `holidays` WRITE;
/*!40000 ALTER TABLE `holidays` DISABLE KEYS */;
INSERT INTO `holidays` VALUES (1,'2025-12-28','Sunday','2025-12-24 11:43:26'),(2,'2026-01-09','fest','2026-01-09 05:55:55');
/*!40000 ALTER TABLE `holidays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leave_requests`
--

DROP TABLE IF EXISTS `leave_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leave_requests` (
  `leave_id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) NOT NULL,
  `leave_type` enum('Vacation','Sick Leave','Personal Day') NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `reason` text NOT NULL,
  `status` enum('Pending','Approved','Rejected') NOT NULL DEFAULT 'Pending',
  `request_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` varchar(10) DEFAULT NULL,
  `review_date` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`leave_id`),
  KEY `idx_leave_user_status` (`user_id`,`status`),
  KEY `idx_leave_status` (`status`),
  CONSTRAINT `fk_leave_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_leave_dates` CHECK ((`end_date` >= `start_date`))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leave_requests`
--

LOCK TABLES `leave_requests` WRITE;
/*!40000 ALTER TABLE `leave_requests` DISABLE KEYS */;
INSERT INTO `leave_requests` VALUES (1,'emp002','Vacation','2025-09-29','2025-09-29','out of station','Approved','2025-09-28 14:22:29','adm001','2025-09-28 14:23:52');
/*!40000 ALTER TABLE `leave_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `remote_work_requests`
--

DROP TABLE IF EXISTS `remote_work_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `remote_work_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) NOT NULL,
  `address` text NOT NULL,
  `lat` decimal(10,8) NOT NULL,
  `lon` decimal(11,8) NOT NULL,
  `reason` text,
  `status` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `requested_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` varchar(10) DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `review_notes` text,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `reviewed_by` (`reviewed_by`),
  CONSTRAINT `remote_work_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `remote_work_requests_ibfk_2` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `remote_work_requests`
--

LOCK TABLES `remote_work_requests` WRITE;
/*!40000 ALTER TABLE `remote_work_requests` DISABLE KEYS */;
INSERT INTO `remote_work_requests` VALUES (1,'emp001','39/F1, 1st Floor,\r\nSAI Kiran Apartment,\r\nYamunai Street Extension, Balaji Nagar, Tambaram, Chennai 600059',12.93025280,80.11120640,'work from home','Approved','2025-12-23 12:09:17','adm001','2025-12-23 12:20:45','','2025-12-23','2025-12-23'),(2,'emp001','39/F1, 1st Floor,\r\nSAI Kiran Apartment,\r\nYamunai Street Extension, Balaji Nagar, Tambaram, Chennai 600059',12.93025280,80.11120640,'work from home','Approved','2025-12-24 10:16:17','adm001','2025-12-24 10:16:51','','2025-12-24','2025-12-24'),(3,'emp002','39/F1, 1st Floor,\r\nSAI Kiran Apartment,\r\nYamunai Street Extension, Balaji Nagar, Tambaram, Chennai 600059',12.93025280,80.11120640,'work from error','Approved','2025-12-24 12:19:45','adm001','2025-12-24 12:20:15','','2025-12-24','2025-12-26');
/*!40000 ALTER TABLE `remote_work_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site_visits`
--

DROP TABLE IF EXISTS `site_visits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `site_visits` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(10) NOT NULL,
  `site_id` int NOT NULL,
  `visit_date` date NOT NULL,
  `reason` text,
  `status` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `requested_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_by` varchar(10) DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `review_notes` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_site_date` (`user_id`,`site_id`,`visit_date`),
  KEY `site_id` (`site_id`),
  KEY `reviewed_by` (`reviewed_by`),
  KEY `idx_site_visits_user_date` (`user_id`,`visit_date`),
  KEY `idx_site_visits_status` (`status`),
  CONSTRAINT `site_visits_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `site_visits_ibfk_2` FOREIGN KEY (`site_id`) REFERENCES `sites` (`id`) ON DELETE CASCADE,
  CONSTRAINT `site_visits_ibfk_3` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site_visits`
--

LOCK TABLES `site_visits` WRITE;
/*!40000 ALTER TABLE `site_visits` DISABLE KEYS */;
/*!40000 ALTER TABLE `site_visits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `site_name` varchar(255) NOT NULL,
  `site_address` text NOT NULL,
  `site_lat` decimal(10,8) NOT NULL,
  `site_lon` decimal(11,8) NOT NULL,
  `site_radius` int DEFAULT '200',
  `is_active` tinyint(1) DEFAULT '1',
  `created_by` varchar(10) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `sites_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sites`
--

LOCK TABLES `sites` WRITE;
/*!40000 ALTER TABLE `sites` DISABLE KEYS */;
INSERT INTO `sites` VALUES (4,'Client Office - Tech Park','IT Corridor, OMR, Chennai, Tamil Nadu',12.96980000,80.24340000,200,1,'adm001','2025-10-08 13:32:21','2025-10-08 13:32:21'),(5,'Project Site - Guindy','Guindy Industrial Estate, Chennai, Tamil Nadu',13.00670000,80.22060000,200,1,'adm001','2025-10-08 13:32:21','2025-10-08 13:32:21'),(6,'Regional Office - Coimbatore','RS Puram, Coimbatore, Tamil Nadu',11.01680000,76.95580000,200,1,'adm001','2025-10-08 13:32:21','2025-10-08 13:32:21'),(7,'Client Office - Tech Park','IT Corridor, OMR, Chennai, Tamil Nadu',12.96980000,80.24340000,200,1,'adm001','2025-10-08 13:33:31','2025-10-08 13:33:31'),(8,'Project Site - Guindy','Guindy Industrial Estate, Chennai, Tamil Nadu',13.00670000,80.22060000,200,1,'adm001','2025-10-08 13:33:31','2025-10-08 13:33:31'),(9,'Regional Office - Coimbatore','RS Puram, Coimbatore, Tamil Nadu',11.01680000,76.95580000,200,1,'adm001','2025-10-08 13:33:31','2025-10-08 13:33:31');
/*!40000 ALTER TABLE `sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('admin','employee') NOT NULL,
  `work_mode` enum('Office','Remote') NOT NULL DEFAULT 'Office',
  `remote_address` varchar(255) DEFAULT NULL,
  `remote_lat` decimal(10,8) DEFAULT NULL,
  `remote_lon` decimal(11,8) DEFAULT NULL,
  `vacation_days_total` int NOT NULL DEFAULT '5',
  `sick_days_total` int NOT NULL DEFAULT '5',
  `vacation_days_taken` int NOT NULL DEFAULT '0',
  `sick_days_taken` int NOT NULL DEFAULT '0',
  `geofence_lat` decimal(10,8) DEFAULT NULL,
  `geofence_lon` decimal(11,8) DEFAULT NULL,
  `geofence_status` enum('none','pending','approved','rejected') NOT NULL DEFAULT 'none',
  `compoff_balance` int NOT NULL DEFAULT '0',
  `remote_latitude` decimal(10,8) DEFAULT NULL,
  `remote_longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('adm001','Francis','francis','scrypt:32768:8:1$PAJjy4USWLdtRYHZ$fa0ed490b60d5a869817c4785d904bfa681fc9cdae30237614fc064935569fa0e1bd1af8ec30be46e9b81fafb9d1a8add045d362bcc375fdd9162ba69ee69bfe','admin','Office',NULL,NULL,NULL,5,5,0,0,NULL,NULL,'none',0,NULL,NULL),('emp001','Pradeep','pradeep','scrypt:32768:8:1$07YO62BQbfUj39P1$35df7e0673c0ae3b2a7b51719ad93645bd624e59059499e50932cd5d7343d56d27ec915c7960f929423aab661179fe10135762d7155fbbf983178bf4c5b4e6e3','employee','Office',NULL,NULL,NULL,5,5,0,0,13.04821760,80.25538560,'approved',0,NULL,NULL),('emp002','Sounthar','sounthar','scrypt:32768:8:1$32mBDnbbzrzCSIsK$6368ac3fc11bd89ee66f86dccbce62549ac6eb9e37f086c6d855ff5e3c5e05324bd18209d7a82372f9ddf8856f640dc684b594a7febcce03443b93ece57a3bcf','employee','Office',NULL,NULL,NULL,5,5,1,0,12.95918380,80.16108770,'approved',0,NULL,NULL),('emp003','Aadhi','aadhi','scrypt:32768:8:1$B3mIVUdXTaiwAo7F$f4230922b02e8e5dd98bb033e3b8b052b700d5597459cddca4e8bbbe2bf297d774072df6bb87c6bb7ec938510de628bb50e279c5a27553579b3b42bb5c765a52','employee','Office',NULL,NULL,NULL,5,5,0,0,NULL,NULL,'none',0,NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-28 10:38:43
