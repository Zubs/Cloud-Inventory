DROP TABLE IF EXISTS `items`;
CREATE TABLE `items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `quantity` int DEFAULT '0',
  `status` enum('Ready','In Production') DEFAULT 'Ready',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_id` int DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `status` enum('Pending','In Progress','Completed') DEFAULT 'Pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `items` (`id`, `name`, `quantity`, `status`) VALUES
(1, 'Dell XPS 13', 50, 'Ready'),
(3, 'Logitech Mouse', 150, 'Ready'),
(4, 'Office Chairs', 100, 'In Production'),
(5, 'HP Elite Book', 34, 'Ready');

INSERT INTO `orders` (`id`, `item_id`, `quantity`, `status`, `created_at`) VALUES
(1, 1, 5, 'In Progress', '2026-01-12 14:32:40'),
(2, 3, 1, 'Completed', '2026-01-12 14:32:40'),
(3, 5, 4, 'In Progress', '2026-01-12 15:33:16');

INSERT INTO `user` (`id`, `email`, `password`) VALUES
(1, 'zubairidrisaweda@gmail.com', 'password'),
(2, 'zubairidrisaweda@yahoo.com', '-5260180889615528533');