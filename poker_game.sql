-- MySQL dump 10.13  Distrib 8.1.0, for Win64 (x86_64)
--
-- Host: localhost    Database: poker_game
-- ------------------------------------------------------
-- Server version	8.1.0

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
-- Table structure for table `game_results`
--

DROP TABLE IF EXISTS `game_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_results` (
  `result_id` int NOT NULL AUTO_INCREMENT,
  `game_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `pos` int DEFAULT NULL,
  `winnings` int DEFAULT NULL,
  PRIMARY KEY (`result_id`),
  KEY `game_id` (`game_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `game_results_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE,
  CONSTRAINT `game_results_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_results`
--

LOCK TABLES `game_results` WRITE;
/*!40000 ALTER TABLE `game_results` DISABLE KEYS */;
/*!40000 ALTER TABLE `game_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game_statistics`
--

DROP TABLE IF EXISTS `game_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_statistics` (
  `stat_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `games_played` int DEFAULT '0',
  `games_won` int DEFAULT '0',
  `rgscore` int DEFAULT '0',
  `aggressiveness_score` float DEFAULT '0',
  `conservativeness_score` float DEFAULT '0',
  `total_play_time` int DEFAULT '0',
  PRIMARY KEY (`stat_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `game_statistics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_statistics`
--

LOCK TABLES `game_statistics` WRITE;
/*!40000 ALTER TABLE `game_statistics` DISABLE KEYS */;
/*!40000 ALTER TABLE `game_statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `games` (
  `game_id` int NOT NULL AUTO_INCREMENT,
  `lobby_id` int DEFAULT NULL,
  `start_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `end_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`game_id`),
  KEY `lobby_id` (`lobby_id`),
  CONSTRAINT `games_ibfk_1` FOREIGN KEY (`lobby_id`) REFERENCES `lobbies` (`lobby_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `games`
--

LOCK TABLES `games` WRITE;
/*!40000 ALTER TABLE `games` DISABLE KEYS */;
/*!40000 ALTER TABLE `games` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lobbies`
--

DROP TABLE IF EXISTS `lobbies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lobbies` (
  `lobby_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `host_user_id` int DEFAULT NULL,
  `status` enum('waiting','in_progress','completed') DEFAULT 'waiting',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `show_odds` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`lobby_id`),
  KEY `host_user_id` (`host_user_id`),
  CONSTRAINT `lobbies_ibfk_1` FOREIGN KEY (`host_user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lobbies`
--

LOCK TABLES `lobbies` WRITE;
/*!40000 ALTER TABLE `lobbies` DISABLE KEYS */;
INSERT INTO `lobbies` VALUES (1,'lobby',2,'waiting','2023-09-26 22:18:43',1),(2,'test',2,'waiting','2023-09-26 22:22:15',1),(3,'summer\'s lobby',13,'waiting','2023-09-26 22:38:57',0),(4,'test',13,'waiting','2023-09-26 22:40:36',1);
/*!40000 ALTER TABLE `lobbies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_lobbies`
--

DROP TABLE IF EXISTS `player_lobbies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_lobbies` (
  `user_id` int NOT NULL,
  `lobby_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`lobby_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `lobby_id` (`lobby_id`),
  CONSTRAINT `player_lobbies_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `player_lobbies_ibfk_2` FOREIGN KEY (`lobby_id`) REFERENCES `lobbies` (`lobby_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_lobbies`
--

LOCK TABLES `player_lobbies` WRITE;
/*!40000 ALTER TABLE `player_lobbies` DISABLE KEYS */;
/*!40000 ALTER TABLE `player_lobbies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_chips`
--

DROP TABLE IF EXISTS `user_chips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_chips` (
  `user_id` int NOT NULL,
  `chips_balance` int DEFAULT '1000',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_chips_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_chips`
--

LOCK TABLES `user_chips` WRITE;
/*!40000 ALTER TABLE `user_chips` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_chips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_game_limits`
--

DROP TABLE IF EXISTS `user_game_limits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_game_limits` (
  `user_id` int NOT NULL,
  `daily_game_limit` int DEFAULT '5',
  `last_game_timestamp` timestamp NULL DEFAULT NULL,
  `games_played_today` int DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_game_limits_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_game_limits`
--

LOCK TABLES `user_game_limits` WRITE;
/*!40000 ALTER TABLE `user_game_limits` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_game_limits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `salt` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `profile_picture` varchar(255) DEFAULT 'default.png',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'test','ffd7adf617d7c101230d0164b0e5cf1e1dc64f48d9ea4247550d5c77baad9dca','9fc3239fd856368d011bb6c4653329b2','opkoala4@gmail.com','default.png'),(3,'username','3f11f5dff8c63633b95535a4b09904b62e0c176a74ccc596ea6ef17ed4d645f6','b35dfaaa333da22bce71b005497192f7','email@','default.png'),(6,'username1','0c524cb702f69ee9fa6cffabd999a86466b6f5781f1684c25937b03e1a334b99','851ff8018b6dd4c733791bff10d92b95','email@1','default.png'),(8,'qet','33fba67b4da137d722c90ac6e1acc37f3bb4cd09c308d2af983e5e4c292994d3','2b894047f418e110d0ffc17e6f5ff3d0','adg@','default.png'),(12,'tea','9b0e1ed4dcba6df6f0ea0f3736b06d2bf134b9b8361573fe198bdaf23382e770','4ac640360b4400530ac0e96ce193e864','email@.com','default.png'),(13,'summer','36c08d2d6418ca43d21d9203331b4e408e0e78e65ed97f2a0b26fa61b54f3ae8','17f8f07b77f57f6248aafa4227a695a5','summer@gmail.com','default.png');
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

-- Dump completed on 2023-09-26 23:51:37
