-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: gestao_oficina
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

-- =====================================================================
-- Base de dados: gestao_oficina
-- Script completo e portátil: cria a base de dados desde o inicio,
-- sem depender de estado GTID ou de utilizadores/definers do PC de origem.
-- Basta correr este ficheiro num MySQL vazio (ex: mysql -u root -p < gestao_oficina.sql)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `gestao_oficina`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `gestao_oficina`;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nome_categoria` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nome_categoria` (`nome_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (4,'Equipamento informático'),(1,'Ferramenta elétrica'),(3,'Ferramenta manual'),(2,'Instrumento de medida');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id_equipamento` int NOT NULL AUTO_INCREMENT,
  `designacao` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_inventario` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_categoria` int DEFAULT NULL,
  `id_localizacao` int DEFAULT NULL,
  `id_estado` int NOT NULL,
  `id_fornecedor` int DEFAULT NULL,
  `data_aquisicao` date DEFAULT NULL,
  `valor_aquisicao` decimal(10,2) DEFAULT NULL,
  `observacoes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_equipamento`),
  UNIQUE KEY `numero_inventario` (`numero_inventario`),
  KEY `fk_equipamento_categoria` (`id_categoria`),
  KEY `fk_equipamento_localizacao` (`id_localizacao`),
  KEY `fk_equipamento_estado` (`id_estado`),
  KEY `fk_equipamento_fornecedor` (`id_fornecedor`),
  KEY `idx_equipamento_designacao` (`designacao`),
  CONSTRAINT `fk_equipamento_categoria` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_equipamento_estado` FOREIGN KEY (`id_estado`) REFERENCES `estados_equipamento` (`id_estado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_equipamento_fornecedor` FOREIGN KEY (`id_fornecedor`) REFERENCES `fornecedores` (`id_fornecedor`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_equipamento_localizacao` FOREIGN KEY (`id_localizacao`) REFERENCES `localizacoes` (`id_localizacao`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
INSERT INTO `equipamentos` VALUES (1,'Berbequim Bosch GSB 13','EQ-0001',1,1,1,1,'2024-03-10',89.90,NULL),(2,'Multímetro Digital Fluke 117','EQ-0002',2,2,1,2,'2023-11-05',210.00,NULL),(3,'Osciloscópio Rigol DS1054Z','EQ-0003',2,3,2,2,'2023-06-20',320.00,NULL),(4,'Máquina de Solda Elétrica','EQ-0004',1,4,4,1,'2022-09-15',150.00,NULL),(5,'Martelo de Bola 500g','EQ-0005',3,7,1,1,'2023-06-15',18.58,NULL),(6,'Martelo de Unha','EQ-0006',3,10,1,2,'2025-09-15',17.84,NULL),(7,'Chave de Fendas Phillips PH2','EQ-0007',3,10,1,1,'2022-10-16',46.74,NULL),(8,'Chave de Fendas Plana 6mm','EQ-0008',3,6,1,2,'2024-10-10',10.68,NULL),(9,'Jogo de Chaves de Fendas de Precisão','EQ-0009',3,7,1,3,'2023-12-20',53.33,NULL),(10,'Alicate Universal 200mm','EQ-0010',3,12,1,1,'2025-03-31',9.27,NULL),(11,'Alicate de Corte Diagonal','EQ-0011',3,5,1,5,'2025-01-21',39.43,NULL),(12,'Alicate de Bico Fino','EQ-0012',3,12,4,6,'2023-07-23',51.27,NULL),(13,'Alicate de Pressão Vise-Grip','EQ-0013',3,2,1,1,'2025-04-06',21.32,NULL),(14,'Jogo de Chaves Sextavadas (Allen) Métricas','EQ-0014',3,11,1,2,'2025-02-25',25.99,NULL),(15,'Jogo de Chaves de Caixa 1/2\"','EQ-0015',3,11,1,6,'2021-10-20',41.35,NULL),(16,'Chave Inglesa 250mm','EQ-0016',3,3,1,2,'2022-11-01',32.47,NULL),(17,'Chave de Fenda Torx T25','EQ-0017',3,5,1,6,'2023-06-19',45.92,NULL),(18,'Serrote de Costas','EQ-0018',3,14,1,1,'2023-07-28',54.22,NULL),(19,'Serra de Arco para Metais','EQ-0019',3,13,1,3,'2021-09-29',17.26,NULL),(20,'X-Ato / Cutter Profissional','EQ-0020',3,10,2,3,'2023-05-21',44.15,NULL),(21,'Fita Métrica 5m','EQ-0021',3,7,2,6,'2026-02-23',13.14,NULL),(22,'Fita Métrica 8m','EQ-0022',3,3,1,5,'2023-12-13',49.69,NULL),(23,'Nível de Bolha 60cm','EQ-0023',3,7,2,4,'2025-01-22',17.77,NULL),(24,'Nível de Bolha 30cm','EQ-0024',3,3,1,1,'2021-07-12',56.60,NULL),(25,'Esquadro de Aço 30cm','EQ-0025',3,3,1,6,'2025-09-26',40.58,NULL),(26,'Punção de Bater','EQ-0026',3,7,1,4,'2023-10-27',63.25,NULL),(27,'Escopro de Bater 12mm','EQ-0027',3,14,2,6,'2022-04-15',45.74,NULL),(28,'Lima Chata Bastarda','EQ-0028',3,9,1,6,'2024-10-25',11.25,NULL),(29,'Lima Meia-Cana','EQ-0029',3,7,1,1,'2023-12-15',63.30,NULL),(30,'Rebarbadora Manual','EQ-0030',3,13,1,1,'2024-05-07',55.42,NULL),(31,'Torno de Bancada 100mm','EQ-0031',3,9,1,2,'2025-03-12',50.63,NULL),(32,'Grampo em C 100mm','EQ-0032',3,9,3,5,'2021-01-03',40.74,NULL),(33,'Grampo Rápido 300mm','EQ-0033',3,8,1,3,'2024-06-13',18.99,NULL),(34,'Chave de Caixa T25','EQ-0034',3,4,2,1,'2021-12-17',48.78,NULL),(35,'Extrator de Parafusos Danificados','EQ-0035',3,14,1,5,'2022-05-31',12.27,NULL),(36,'Chave de Roquete 3/8\"','EQ-0036',3,8,3,2,'2023-12-22',36.42,NULL),(37,'Macaco de Garagem 2T','EQ-0037',3,10,1,2,'2023-04-04',47.63,NULL),(38,'Cavalete de Apoio Dobrável','EQ-0038',3,7,1,6,'2025-03-10',31.01,NULL),(39,'Jogo de Limas de Agulha','EQ-0039',3,9,1,2,'2023-07-10',8.37,NULL),(40,'Rebitadeira Manual','EQ-0040',3,1,1,2,'2023-06-22',4.94,NULL),(41,'Arco de Serra Ajustável','EQ-0041',3,12,1,2,'2021-10-04',59.28,NULL),(42,'Chave de Correia','EQ-0042',3,14,1,5,'2023-09-02',21.35,NULL),(43,'Chave de Filtro de Óleo','EQ-0043',3,8,1,2,'2026-04-21',19.20,NULL),(44,'Alicate de Corte Lateral','EQ-0044',3,8,1,2,'2022-01-22',10.36,NULL),(45,'Espátula de Massa 5cm','EQ-0045',3,7,1,4,'2026-03-28',56.76,NULL),(46,'Espátula de Massa 10cm','EQ-0046',3,1,1,6,'2022-02-08',8.17,NULL),(47,'Berbequim/Aparafusadora sem Fios 18V','EQ-0047',1,12,1,1,'2023-10-16',128.34,NULL),(48,'Berbequim de Impacto 750W','EQ-0048',1,9,1,4,'2023-01-22',166.17,NULL),(49,'Rebarbadora Angular 125mm','EQ-0049',1,4,2,1,'2025-12-21',396.49,NULL),(50,'Rebarbadora Angular 230mm','EQ-0050',1,14,1,1,'2021-03-02',466.51,NULL),(51,'Lixadora Orbital','EQ-0051',1,13,1,2,'2025-07-23',256.25,NULL),(52,'Lixadora de Cinta','EQ-0052',1,4,2,1,'2022-11-06',209.85,NULL),(53,'Serra Circular Portátil','EQ-0053',1,7,1,4,'2024-03-14',229.01,NULL),(54,'Serra Tico-Tico','EQ-0054',1,12,1,5,'2026-06-17',112.34,NULL),(55,'Pistola de Calor 2000W','EQ-0055',1,5,1,1,'2021-09-07',370.37,NULL),(56,'Parafusadora de Impacto sem Fios','EQ-0056',1,1,1,4,'2026-08-22',444.93,NULL),(57,'Compressor de Ar Portátil 24L','EQ-0057',1,9,1,5,'2021-11-25',415.33,NULL),(58,'Máquina de Solda por Pontos','EQ-0058',1,2,1,6,'2023-08-22',220.64,NULL),(59,'Máquina de Solda MIG/MAG','EQ-0059',1,10,1,5,'2021-06-12',314.43,NULL),(60,'Máquina de Solda TIG','EQ-0060',1,7,1,5,'2024-07-19',451.60,NULL),(61,'Ferro de Soldar Elétrico 60W','EQ-0061',1,4,1,3,'2023-09-05',160.54,NULL),(62,'Estação de Soldadura Digital','EQ-0062',1,3,1,3,'2026-02-16',182.54,NULL),(63,'Aspirador de Oficina Industrial','EQ-0063',1,13,2,1,'2026-02-21',315.20,NULL),(64,'Fresadora de Bancada','EQ-0064',1,10,1,1,'2023-05-24',265.06,NULL),(65,'Furadora de Coluna','EQ-0065',1,3,2,1,'2023-09-28',205.74,NULL),(66,'Torno Mecânico de Bancada','EQ-0066',1,3,1,5,'2024-05-24',311.08,NULL),(67,'Rebarbadora Reta (Moto-esmeril)','EQ-0067',1,13,1,1,'2024-05-11',450.31,NULL),(68,'Pistola de Cola Quente','EQ-0068',1,2,2,2,'2023-12-20',95.21,NULL),(69,'Compressor de Ar de Bancada 50L','EQ-0069',1,2,1,2,'2024-01-21',167.56,NULL),(70,'Parafusadora de Bateria de Impacto','EQ-0070',1,4,1,2,'2023-12-18',264.85,NULL),(71,'Multímetro Digital de Bancada','EQ-0071',2,5,2,1,'2022-01-14',421.43,NULL),(72,'Multímetro Digital Portátil','EQ-0072',2,14,1,1,'2024-09-28',506.95,NULL),(73,'Osciloscópio Digital 2 Canais','EQ-0073',2,11,1,2,'2025-12-15',369.80,NULL),(74,'Paquímetro Digital 150mm','EQ-0074',2,7,1,1,'2021-11-05',615.66,NULL),(75,'Micrómetro Externo 0-25mm','EQ-0075',2,12,2,5,'2021-05-28',546.62,NULL),(76,'Fonte de Alimentação de Bancada Regulável','EQ-0076',2,10,1,4,'2022-06-07',51.14,NULL),(77,'Gerador de Sinais','EQ-0077',2,6,2,1,'2025-01-05',156.30,NULL),(78,'Termómetro Infravermelho','EQ-0078',2,4,1,3,'2025-07-23',633.65,NULL),(79,'Medidor de Espessura de Tinta','EQ-0079',2,12,1,2,'2022-10-28',635.13,NULL),(80,'Pinça Amperimétrica','EQ-0080',2,13,1,4,'2021-04-12',137.10,NULL),(81,'Analisador de Rede Elétrica','EQ-0081',2,6,1,4,'2023-10-14',191.75,NULL),(82,'Detector de Tensão sem Contacto','EQ-0082',2,13,1,4,'2021-06-08',561.62,NULL),(83,'Medidor de Humidade','EQ-0083',2,4,1,4,'2024-12-03',215.74,NULL),(84,'Analisador de Baterias','EQ-0084',2,13,2,2,'2021-04-07',437.52,'None'),(85,'Contador de Frequência','EQ-0085',2,7,1,1,'2024-02-18',244.47,NULL),(86,'Nível Laser Rotativo','EQ-0086',2,9,1,5,'2024-09-18',612.02,NULL),(87,'Distanciómetro Laser','EQ-0087',2,2,2,3,'2023-01-02',387.87,NULL),(88,'Computador de Bancada (Diagnóstico)','EQ-0088',4,5,1,5,'2025-11-15',389.64,NULL),(89,'Portátil de Diagnóstico Industrial','EQ-0089',4,13,1,5,'2022-04-19',420.45,NULL),(90,'Impressora 3D FDM','EQ-0090',4,10,1,1,'2025-11-22',121.32,NULL),(91,'Estação de Programação de Microcontroladores','EQ-0091',4,13,1,6,'2023-03-19',404.09,NULL),(92,'Leitor de Códigos OBD-II','EQ-0092',4,2,3,3,'2024-07-09',637.44,NULL),(93,'Monitor de Bancada 24\"','EQ-0093',4,2,1,3,'2024-06-20',640.18,NULL),(94,'Rack de Rede da Oficina','EQ-0094',4,6,1,3,'2022-06-06',269.64,NULL);
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estados_equipamento`
--

DROP TABLE IF EXISTS `estados_equipamento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estados_equipamento` (
  `id_estado` int NOT NULL AUTO_INCREMENT,
  `nome_estado` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_estado`),
  UNIQUE KEY `nome_estado` (`nome_estado`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estados_equipamento`
--

LOCK TABLES `estados_equipamento` WRITE;
/*!40000 ALTER TABLE `estados_equipamento` DISABLE KEYS */;
INSERT INTO `estados_equipamento` VALUES (3,'Avariado'),(1,'Disponível'),(4,'Em manutenção'),(2,'Em uso');
/*!40000 ALTER TABLE `estados_equipamento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fornecedores`
--

DROP TABLE IF EXISTS `fornecedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fornecedores` (
  `id_fornecedor` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contacto` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_fornecedor`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fornecedores`
--

LOCK TABLES `fornecedores` WRITE;
/*!40000 ALTER TABLE `fornecedores` DISABLE KEYS */;
INSERT INTO `fornecedores` VALUES (1,'Ferramentas Silva Lda.','234 000 111','geral@ferramentassilva.pt'),(2,'ElectroTech Portugal','234 222 333','vendas@electrotech.pt'),(3,'Bricolage Industrial Norte','231 125 859','geral@bricolage.pt'),(4,'FerroMax Distribuição','234 350 328','geral@ferromax.pt'),(5,'Instrumentos Técnicos Aveiro','232 854 204','geral@instrumentos.pt'),(6,'Global Tools PT','238 189 704','geral@global.pt');
/*!40000 ALTER TABLE `fornecedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `localizacoes`
--

DROP TABLE IF EXISTS `localizacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `localizacoes` (
  `id_localizacao` int NOT NULL AUTO_INCREMENT,
  `designacao` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_localizacao`),
  UNIQUE KEY `designacao` (`designacao`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `localizacoes`
--

LOCK TABLES `localizacoes` WRITE;
/*!40000 ALTER TABLE `localizacoes` DISABLE KEYS */;
INSERT INTO `localizacoes` VALUES (1,'Prateleira A1','Sala de ferramentas'),(2,'Armário B2','Laboratório de eletrónica'),(3,'Bancada 3','Oficina principal'),(4,'Oficina 1','Área de soldadura'),(5,'Prateleira A2','Sala de ferramentas'),(6,'Prateleira A3','Sala de ferramentas'),(7,'Armário B3','Laboratório de eletrónica'),(8,'Armário C1','Sala de instrumentos de medição'),(9,'Bancada 4','Oficina principal'),(10,'Bancada 5','Oficina principal'),(11,'Oficina 2','Área de montagem'),(12,'Sala de Metrologia','Calibração e instrumentos de precisão'),(13,'Carrinho de Ferramentas 1','Oficina principal'),(14,'Carrinho de Ferramentas 2','Oficina principal');
/*!40000 ALTER TABLE `localizacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manutencoes`
--

DROP TABLE IF EXISTS `manutencoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manutencoes` (
  `id_manutencao` int NOT NULL AUTO_INCREMENT,
  `id_equipamento` int NOT NULL,
  `data_inicio` date NOT NULL,
  `data_fim` date DEFAULT NULL,
  `descricao` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `custo` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_manutencao`),
  KEY `fk_manutencao_equipamento` (`id_equipamento`),
  CONSTRAINT `fk_manutencao_equipamento` FOREIGN KEY (`id_equipamento`) REFERENCES `equipamentos` (`id_equipamento`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manutencoes`
--

LOCK TABLES `manutencoes` WRITE;
/*!40000 ALTER TABLE `manutencoes` DISABLE KEYS */;
INSERT INTO `manutencoes` VALUES (1,4,'2026-06-20',NULL,'Substituição do cabo de alimentação danificado',25.00),(2,12,'2026-09-02',NULL,'Partido',NULL);
/*!40000 ALTER TABLE `manutencoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfis`
--

DROP TABLE IF EXISTS `perfis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfis` (
  `id_perfil` int NOT NULL AUTO_INCREMENT,
  `nome_perfil` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descricao` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_perfil`),
  UNIQUE KEY `nome_perfil` (`nome_perfil`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfis`
--

LOCK TABLES `perfis` WRITE;
/*!40000 ALTER TABLE `perfis` DISABLE KEYS */;
INSERT INTO `perfis` VALUES (1,'Administrador','Acesso total ao sistema: gestão de equipamentos, utilizadores e relatórios'),(2,'Utilizador','Pode consultar equipamentos e registar as suas próprias utilizações');
/*!40000 ALTER TABLE `perfis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservas`
--

DROP TABLE IF EXISTS `reservas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservas` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `id_equipamento` int NOT NULL,
  `id_utilizador` int NOT NULL,
  `data_inicio` datetime NOT NULL,
  `data_fim` datetime NOT NULL,
  `observacoes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reserva`),
  KEY `fk_reserva_utilizador` (`id_utilizador`),
  KEY `idx_reserva_equipamento` (`id_equipamento`),
  KEY `idx_reserva_datas` (`data_inicio`,`data_fim`),
  CONSTRAINT `fk_reserva_equipamento` FOREIGN KEY (`id_equipamento`) REFERENCES `equipamentos` (`id_equipamento`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_utilizador` FOREIGN KEY (`id_utilizador`) REFERENCES `utilizadores` (`id_utilizador`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_reserva_datas` CHECK ((`data_fim` > `data_inicio`))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservas`
--

LOCK TABLES `reservas` WRITE;
/*!40000 ALTER TABLE `reservas` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilizacoes`
--

DROP TABLE IF EXISTS `utilizacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilizacoes` (
  `id_utilizacao` int NOT NULL AUTO_INCREMENT,
  `id_equipamento` int NOT NULL,
  `id_utilizador` int NOT NULL,
  `data_inicio` datetime NOT NULL,
  `data_fim` datetime DEFAULT NULL,
  `observacoes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_utilizacao`),
  KEY `idx_utilizacao_equipamento` (`id_equipamento`),
  KEY `idx_utilizacao_utilizador` (`id_utilizador`),
  KEY `idx_utilizacao_datas` (`data_inicio`,`data_fim`),
  CONSTRAINT `fk_utilizacao_equipamento` FOREIGN KEY (`id_equipamento`) REFERENCES `equipamentos` (`id_equipamento`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_utilizacao_utilizador` FOREIGN KEY (`id_utilizador`) REFERENCES `utilizadores` (`id_utilizador`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilizacoes`
--

LOCK TABLES `utilizacoes` WRITE;
/*!40000 ALTER TABLE `utilizacoes` DISABLE KEYS */;
INSERT INTO `utilizacoes` VALUES (1,3,2,'2026-07-01 09:00:00',NULL,'Medição de sinais no protótipo'),(2,12,2,'2026-09-02 14:48:22','2026-09-02 14:55:17',''),(3,20,2,'2026-08-28 08:30:00',NULL,'Corte de material de embalagem'),(4,21,2,'2026-08-29 09:15:00',NULL,'Medições para corte de peças'),(5,23,1,'2026-08-27 10:00:00',NULL,'Verificação de nivelamento de bancada'),(6,27,2,'2026-08-30 14:20:00',NULL,'Marcação de furos em chapa'),(7,34,1,'2026-08-31 11:45:00',NULL,'Aperto de parafusos Torx no equipamento'),(8,49,2,'2026-08-28 15:00:00',NULL,'Rebarbagem de peça metálica'),(9,52,2,'2026-08-29 16:10:00',NULL,'Acabamento de superfície em madeira'),(10,63,1,'2026-08-30 08:00:00',NULL,'Limpeza da bancada principal'),(11,65,2,'2026-08-31 09:30:00',NULL,'Furação de peça em série'),(12,68,1,'2026-08-27 13:10:00',NULL,'Colagem de componentes'),(13,71,2,'2026-08-29 10:40:00',NULL,'Diagnóstico elétrico de placa'),(14,75,1,'2026-08-28 11:00:00',NULL,'Medição de tolerâncias de peça'),(15,77,2,'2026-08-30 09:00:00',NULL,'Teste de circuito com sinal gerado'),(16,84,1,'2026-08-31 14:50:00',NULL,'Teste de capacidade de baterias'),(17,87,2,'2026-08-27 16:30:00',NULL,'Medição de distâncias na oficina');
/*!40000 ALTER TABLE `utilizacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilizadores`
--

DROP TABLE IF EXISTS `utilizadores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilizadores` (
  `id_utilizador` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id_perfil` int NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `data_criacao` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_utilizador`),
  UNIQUE KEY `username` (`username`),
  KEY `fk_utilizador_perfil` (`id_perfil`),
  CONSTRAINT `fk_utilizador_perfil` FOREIGN KEY (`id_perfil`) REFERENCES `perfis` (`id_perfil`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilizadores`
--

LOCK TABLES `utilizadores` WRITE;
/*!40000 ALTER TABLE `utilizadores` DISABLE KEYS */;
INSERT INTO `utilizadores` VALUES (1,'Administrador','admin','scrypt:32768:8:1$XqjcTEP8Ic87UPvH$2928f78fdc8903137a6e12edee20bd0ac2fe6837f83755b6d570593feafa41e01fd06cf62eb54da25c9a2ba9d93e4d5ba3d8f0c550e01fff1fe09eb2cda05bfb','admin@oficina.pt',1,1,'2026-09-02 14:28:26'),(2,'Utilizador Teste','user','scrypt:32768:8:1$4mbcSXTCrP3Y85s9$fc9e9ce0396ddde906a5f21f654438696ec750acbfcf5444ea8ce39a5eb8766f4da50c801b14d5a127fb597bfc4a045b3bc63f9524000326ef08b3aa97c230ae','user@oficina.pt',2,1,'2026-09-02 14:28:26');
/*!40000 ALTER TABLE `utilizadores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_equipamentos_estado`
--

DROP TABLE IF EXISTS `vw_equipamentos_estado`;
/*!50001 DROP VIEW IF EXISTS `vw_equipamentos_estado`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_equipamentos_estado` AS SELECT 
 1 AS `id_equipamento`,
 1 AS `designacao`,
 1 AS `numero_inventario`,
 1 AS `categoria`,
 1 AS `localizacao`,
 1 AS `estado`,
 1 AS `fornecedor`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_utilizacoes_detalhe`
--

DROP TABLE IF EXISTS `vw_utilizacoes_detalhe`;
/*!50001 DROP VIEW IF EXISTS `vw_utilizacoes_detalhe`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_utilizacoes_detalhe` AS SELECT 
 1 AS `id_utilizacao`,
 1 AS `equipamento`,
 1 AS `numero_inventario`,
 1 AS `utilizador`,
 1 AS `data_inicio`,
 1 AS `data_fim`,
 1 AS `duracao_minutos`,
 1 AS `observacoes`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vw_equipamentos_estado`
--

/*!50001 DROP VIEW IF EXISTS `vw_equipamentos_estado`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `vw_equipamentos_estado` AS select `eq`.`id_equipamento` AS `id_equipamento`,`eq`.`designacao` AS `designacao`,`eq`.`numero_inventario` AS `numero_inventario`,`c`.`nome_categoria` AS `categoria`,`l`.`designacao` AS `localizacao`,`es`.`nome_estado` AS `estado`,`f`.`nome` AS `fornecedor` from ((((`equipamentos` `eq` left join `categorias` `c` on((`c`.`id_categoria` = `eq`.`id_categoria`))) left join `localizacoes` `l` on((`l`.`id_localizacao` = `eq`.`id_localizacao`))) left join `estados_equipamento` `es` on((`es`.`id_estado` = `eq`.`id_estado`))) left join `fornecedores` `f` on((`f`.`id_fornecedor` = `eq`.`id_fornecedor`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_utilizacoes_detalhe`
--

/*!50001 DROP VIEW IF EXISTS `vw_utilizacoes_detalhe`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `vw_utilizacoes_detalhe` AS select `u`.`id_utilizacao` AS `id_utilizacao`,`e`.`designacao` AS `equipamento`,`e`.`numero_inventario` AS `numero_inventario`,`ut`.`nome` AS `utilizador`,`u`.`data_inicio` AS `data_inicio`,`u`.`data_fim` AS `data_fim`,timestampdiff(MINUTE,`u`.`data_inicio`,coalesce(`u`.`data_fim`,now())) AS `duracao_minutos`,`u`.`observacoes` AS `observacoes` from ((`utilizacoes` `u` join `equipamentos` `e` on((`e`.`id_equipamento` = `u`.`id_equipamento`))) join `utilizadores` `ut` on((`ut`.`id_utilizador` = `u`.`id_utilizador`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-03 10:11:32
