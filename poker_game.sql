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
  `aggressiveness_score` float DEFAULT '0',
  `conservativeness_score` float DEFAULT '0',
  PRIMARY KEY (`result_id`),
  KEY `game_id` (`game_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `game_results_ibfk_1` FOREIGN KEY (`game_id`) REFERENCES `games` (`game_id`) ON DELETE CASCADE,
  CONSTRAINT `game_results_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_results`
--

LOCK TABLES `game_results` WRITE;
/*!40000 ALTER TABLE `game_results` DISABLE KEYS */;
INSERT INTO `game_results` VALUES (53,76,27,3,-100,100,0),(54,76,24,1,300,0,0),(55,76,23,2,-100,0,0);
/*!40000 ALTER TABLE `game_results` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `games`
--

LOCK TABLES `games` WRITE;
/*!40000 ALTER TABLE `games` DISABLE KEYS */;
INSERT INTO `games` VALUES (76,417,'2023-12-02 13:57:20','2023-12-02 13:57:39'),(77,419,'2023-12-02 14:24:49',NULL);
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
  `name` varchar(16) NOT NULL,
  `host_user_id` int DEFAULT NULL,
  `status` enum('waiting','in_progress','completed','abandoned') DEFAULT 'waiting',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `show_odds` tinyint(1) DEFAULT '1',
  `player_limit` int DEFAULT '6',
  `buy_in` int NOT NULL DEFAULT '100',
  PRIMARY KEY (`lobby_id`),
  KEY `host_user_id` (`host_user_id`),
  CONSTRAINT `lobbies_ibfk_1` FOREIGN KEY (`host_user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `lobbies_chk_1` CHECK (((`player_limit` >= 3) and (`player_limit` <= 6)))
) ENGINE=InnoDB AUTO_INCREMENT=420 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lobbies`
--

LOCK TABLES `lobbies` WRITE;
/*!40000 ALTER TABLE `lobbies` DISABLE KEYS */;
INSERT INTO `lobbies` VALUES (417,'test',27,'completed','2023-12-02 13:57:06',1,3,100),(418,'hlfklh',23,'abandoned','2023-12-02 14:20:59',1,3,100),(419,'utraaut',24,'abandoned','2023-12-02 14:23:50',1,3,100);
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
-- Table structure for table `user_game_limits`
--

DROP TABLE IF EXISTS `user_game_limits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_game_limits` (
  `user_id` int NOT NULL,
  `daily_game_limit` int DEFAULT '5',
  `last_logged_in` timestamp NULL DEFAULT NULL,
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
INSERT INTO `user_game_limits` VALUES (23,10,'2023-12-02 14:21:35',1),(24,10,'2023-12-02 14:23:39',1),(25,10,'2023-12-02 14:24:36',0),(26,10,'2023-12-02 17:14:42',0),(27,10,'2023-12-02 14:21:16',1),(29,10,'2023-11-29 18:52:07',0),(30,10,'2023-11-26 22:11:53',0),(31,10,'2023-11-29 19:33:37',0),(32,10,'2023-11-29 19:33:39',0),(33,10,'2023-11-29 19:33:43',0),(34,10,'2023-11-29 19:33:46',0),(35,10,'2023-11-29 19:33:49',0),(36,10,'2023-11-29 19:33:51',0);
/*!40000 ALTER TABLE `user_game_limits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_statistics`
--

DROP TABLE IF EXISTS `user_statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_statistics` (
  `stat_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `games_played` int DEFAULT '0',
  `games_won` int DEFAULT '0',
  `rgscore` float DEFAULT '100',
  `average_aggressiveness_score` float DEFAULT '0',
  `average_conservativeness_score` float DEFAULT '0',
  `total_play_time` int DEFAULT '0',
  `streak` int DEFAULT '0',
  PRIMARY KEY (`stat_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `user_statistics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_statistics`
--

LOCK TABLES `user_statistics` WRITE;
/*!40000 ALTER TABLE `user_statistics` DISABLE KEYS */;
INSERT INTO `user_statistics` VALUES (15,23,3,0,107.5,12.7,30.95,238,5),(16,24,3,6,107.5,31.85,14.07,238,5),(17,25,1,0,103,22.22,33.33,78,3),(18,26,0,0,103,0,0,0,3),(19,27,2,0,103,55,30,160,3),(20,29,0,0,101.5,0,0,0,2),(21,30,0,0,100,0,0,0,0),(22,31,0,0,100,0,0,0,0),(23,32,0,0,100,0,0,0,0),(24,33,0,0,100,0,0,0,0),(25,34,0,0,100,0,0,0,0),(26,35,0,0,100,0,0,0,0),(27,36,0,0,100,0,0,0,0);
/*!40000 ALTER TABLE `user_statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `salt` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `profile_picture` varchar(255) DEFAULT 'default.png',
  `chips_balance` int DEFAULT '500',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username_2` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (23,'player1','8f678a212314f3759e1d1c68a15dba7cd3c66dcf3dcf46b53d36d17565a36a18','fea61ae94ddca5837c962a3325f30f19','player1@gmail.com','cat.png',3900),(24,'player2','5fba1ffc71ac92ba9bc11fa9fa1438bd277f681302a0198e170f064cdea271ec','605190380f1a5bf994b1d24f57d858f8','player2@gmail.com','default.png',4800),(25,'player3','3e4ecc76290c0626aba4e7b3e2bfa3e8f13ae38e32291991b32b7f734951ba53','8ef242d44e01a5c9395c1e7a3fe50e22','player3@gmail.com','default.png',4200),(26,'player4','875ec513fd5a760aa9c87db1fa306ec872225024ef52ea6edaaa713f23da64cc','173099fc0751d270d20776836566f5d1','player4@gmail.com','26_1701211261.png',4800),(27,'player5','1b9bfe0fe634c8af05972455fa2d472099c93fd68b0d48fc21330e16fb15f2e2','6f7719be4665a0a3b3b9b3186940e1e0','player5@gmail.com','default.png',4300),(29,'player6','8931c90794991ae8c04ea51c9c22c4948bd6255bf224074ebb01b28662e033e2','d3c5e2c98fa8ae38f9405f43797428d7','player6@gmail.com','default.png',5000),(30,'player7','0b8107bbdd3107e3f20edb1cd81694a6c8cc879e45f2799afd4cecb81a064f5a','c437e3712d5f3eece3bf7930ef77ee0d','player7@mail.com','default.png',5000),(31,'player8','7576c8f4ed7fc53c0367391a4c060822db8d83a7b11f6ec23d55c6cdf7870601','37c380b9f33eb3aa5ea7dd5953b387b9','player8@gmail.com','default.png',500),(32,'player9','ecf168422902e69c24aeb035fa05bd2f46983df812f6cc871db4e1e3006c395d','db9a71453559e26496990a817f03c1ff','player9@gmail.com','default.png',500),(33,'player10','94316ac492c667ef0df214fa9603456d0428f9b19f6e7f054578a1011b448287','09e613c139628f63a0d2cda5963b6423','player10@gmail.com','default.png',500),(34,'player11','5c341c515208da00b5a0136016a66e14189fb2f638056b13cb2b048251ed4bee','21ded27dd321c9961b9ba33c8e238ca5','player11@gmail.com','default.png',500),(35,'player12','7e9e4fa45e2c69355366191a0814b1e61c3066f643e4b631e00a819222ef5df9','8d6b3ed734d805b1ef66512e08cab3fc','player12@gmail.com','default.png',500),(36,'player13','156cfd90481e95f19af6c05ee5143cd6c3d40d3435eb5c6e43782a7396582226','984b5798de9e209e69ce704042d4a21f','player13@gmail.com','default.png',500);
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

-- Dump completed on 2023-12-03 22:41:54
