-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 05, 2021 at 06:00 PM
-- Server version: 10.4.6-MariaDB
-- PHP Version: 7.3.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dwm_be_sentiment`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
    `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
                              `id` int(11) NOT NULL,
                              `group_category_id` int(11) NOT NULL,
                              `category_name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `cities`
--

CREATE TABLE `cities` (
                          `id` int(11) NOT NULL,
                          `city_name` varchar(30) NOT NULL,
                          `state_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `countries`
--

CREATE TABLE `countries` (
                             `id` int(11) NOT NULL,
                             `country_initials` varchar(10) DEFAULT NULL,
                             `country_name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `group_categories`
--

CREATE TABLE `group_categories` (
                                    `id` int(11) NOT NULL,
                                    `user_id` int(11) NOT NULL,
                                    `group_category_name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `keywords`
--

CREATE TABLE `keywords` (
                            `id` int(11) NOT NULL,
                            `category_id` int(11) NOT NULL,
                            `keywords` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
                         `id` int(11) NOT NULL,
                         `user_id` int(11) NOT NULL,
                         `source_name` varchar(40) NOT NULL,
                         `data_id` varchar(100) NOT NULL,
                         `data_author_id` varchar(100) NOT NULL,
                         `data_user_name` varchar(100) NOT NULL,
                         `data_user_location` varchar(100) NOT NULL,
                         `full_object` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
                         `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
                         `country_name` varchar(100) DEFAULT NULL,
                         `state_name` varchar(100) DEFAULT NULL,
                         `city_name` varchar(100) DEFAULT NULL,
                         `created_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `post_data_categorised_view`
-- (See below for the actual view)
--
CREATE TABLE `post_data_categorised_view` (
                                              `user_id` int(11)
    ,`post_id` int(11)
    ,`group_category_id` int(11)
    ,`category_id` int(11)
    ,`keywords` text
    ,`text` text
    ,`post_source` varchar(40)
    ,`region` varchar(100)
    ,`country` varchar(100)
    ,`state` varchar(100)
    ,`city` varchar(100)
    ,`sentiment_score_value` double
    ,`sentiment_score` varchar(20)
    ,`created_at` timestamp
);

-- --------------------------------------------------------

--
-- Table structure for table `post_is_about_category`
--

CREATE TABLE `post_is_about_category` (
                                          `id` int(11) NOT NULL,
                                          `post_id` int(11) DEFAULT NULL,
                                          `category_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `post_sentiment_scores`
--

CREATE TABLE `post_sentiment_scores` (
                                         `id` int(11) NOT NULL,
                                         `post_id` int(11) NOT NULL,
                                         `sentiment` varchar(20) NOT NULL,
                                         `score` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `scopes`
--

CREATE TABLE `scopes` (
                          `id` int(11) NOT NULL,
                          `user_id` int(11) NOT NULL,
                          `scope` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `social_accounts`
--

CREATE TABLE `social_accounts` (
                                   `id` int(11) NOT NULL,
                                   `user_id` int(11) NOT NULL,
                                   `name` varchar(40) NOT NULL,
                                   `oauth_token` varchar(200) NOT NULL,
                                   `oauth_token_secret` varchar(200) NOT NULL,
                                   `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
                                   `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
                                   `deleted_at` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `states`
--

CREATE TABLE `states` (
                          `id` int(11) NOT NULL,
                          `state_name` varchar(100) DEFAULT NULL,
                          `country_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
                         `id` int(11) NOT NULL,
                         `first_name` varchar(255) NOT NULL,
                         `last_name` varchar(255) NOT NULL,
                         `email` varchar(255) NOT NULL,
                         `phone` varchar(50) NOT NULL,
                         `password` varchar(255) NOT NULL,
                         `is_active` tinyint(1) NOT NULL DEFAULT 0,
                         `is_deleted` tinyint(1) NOT NULL,
                         `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
                         `updated_at` timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
                         `deleted_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure for view `post_data_categorised_view`
--
DROP TABLE IF EXISTS `post_data_categorised_view`;

CREATE VIEW `post_data_categorised_view`  AS  select `posts`.`user_id` AS `user_id`,`posts`.`id` AS `post_id`,`categories`.`group_category_id` AS `group_category_id`,`categories`.`id` AS `category_id`,`keywords`.`keywords` AS `keywords`,`posts`.`text` AS `text`,`posts`.`source_name` AS `post_source`,`posts`.`data_user_location` AS `region`,`posts`.`country_name` AS `country`,`posts`.`state_name` AS `state`,`posts`.`city_name` AS `city`,`post_sentiment_scores`.`score` AS `sentiment_score_value`,`post_sentiment_scores`.`sentiment` AS `sentiment_score`,`posts`.`created_at` AS `created_at` from (((((`posts` join `users` on(`posts`.`user_id` = `users`.`id`)) join `post_is_about_category` on(`post_is_about_category`.`post_id` = `posts`.`id`)) join `categories` on(`post_is_about_category`.`category_id` = `categories`.`id`)) join `keywords` on(`keywords`.`category_id` = `categories`.`id`)) join `post_sentiment_scores` on(`posts`.`id` = `post_sentiment_scores`.`post_id`)) ;



