-- MySQL dump 10.13  Distrib 5.7.16, for Linux (x86_64)
--
-- Host: localhost    Database: tenmiles
-- ------------------------------------------------------
-- Server version	5.7.16

--
-- Table structure for table `email_details`
--

DROP TABLE IF EXISTS `email_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_details` (
  `id` varchar(255) NOT NULL,
  `email_address` varchar(255) DEFAULT NULL,
  `internal_date` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `label_details`
--

DROP TABLE IF EXISTS `label_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `label_details` (
  `id` varchar(100) NOT NULL,
  `label_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `message_details`
--

DROP TABLE IF EXISTS `message_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message_id` varchar(255) DEFAULT NULL,
  `from_address` varchar(255) DEFAULT NULL,
  `to_address` varchar(255) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `label_id` varchar(100) DEFAULT NULL,
  `message_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `label_id` (`label_id`),
  KEY `message_id` (`message_id`),
  CONSTRAINT `message_details_ibfk_1` FOREIGN KEY (`label_id`) REFERENCES `label_details` (`id`),
  CONSTRAINT `message_details_ibfk_2` FOREIGN KEY (`message_id`) REFERENCES `email_details` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;


-- Dump completed on 2019-01-24 11:42:06
