
--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
    ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
    ADD PRIMARY KEY (`id`),
    ADD KEY `group_category_id` (`group_category_id`);

--
-- Indexes for table `cities`
--
ALTER TABLE `cities`
    ADD PRIMARY KEY (`id`);

--
-- Indexes for table `countries`
--
ALTER TABLE `countries`
    ADD PRIMARY KEY (`id`),
    ADD UNIQUE KEY `countries_id_uindex` (`id`);

--
-- Indexes for table `group_categories`
--
ALTER TABLE `group_categories`
    ADD PRIMARY KEY (`id`),
    ADD KEY `user_group_categories` (`user_id`) USING BTREE;

--
-- Indexes for table `keywords`
--
ALTER TABLE `keywords`
    ADD PRIMARY KEY (`id`),
    ADD KEY `category_keywords` (`category_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
    ADD PRIMARY KEY (`id`),
    ADD KEY `users_posts` (`user_id`);

--
-- Indexes for table `post_is_about_category`
--
ALTER TABLE `post_is_about_category`
    ADD PRIMARY KEY (`id`),
    ADD KEY `fk_post` (`post_id`);

--
-- Indexes for table `post_sentiment_scores`
--
ALTER TABLE `post_sentiment_scores`
    ADD PRIMARY KEY (`id`),
    ADD KEY `post` (`post_id`);

--
-- Indexes for table `scopes`
--
ALTER TABLE `scopes`
    ADD PRIMARY KEY (`id`),
    ADD KEY `users_scopes` (`user_id`);

--
-- Indexes for table `social_accounts`
--
ALTER TABLE `social_accounts`
    ADD PRIMARY KEY (`id`),
    ADD KEY `users_social_accounts` (`user_id`);

--
-- Indexes for table `states`
--
ALTER TABLE `states`
    ADD PRIMARY KEY (`id`),
    ADD UNIQUE KEY `states_id_uindex` (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
    ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cities`
--
ALTER TABLE `cities`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `countries`
--
ALTER TABLE `countries`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `group_categories`
--
ALTER TABLE `group_categories`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `keywords`
--
ALTER TABLE `keywords`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `post_is_about_category`
--
ALTER TABLE `post_is_about_category`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `post_sentiment_scores`
--
ALTER TABLE `post_sentiment_scores`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `scopes`
--
ALTER TABLE `scopes`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `social_accounts`
--
ALTER TABLE `social_accounts`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `states`
--
ALTER TABLE `states`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
    MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `categories`
--
ALTER TABLE `categories`
    ADD CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`group_category_id`) REFERENCES `group_categories` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `group_categories`
--
ALTER TABLE `group_categories`
    ADD CONSTRAINT `group_categories_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `keywords`
--
ALTER TABLE `keywords`
    ADD CONSTRAINT `category_keywords` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
    ADD CONSTRAINT `users_posts` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `post_is_about_category`
--
ALTER TABLE `post_is_about_category`
    ADD CONSTRAINT `fk_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `post_sentiment_scores`
--
ALTER TABLE `post_sentiment_scores`
    ADD CONSTRAINT `post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `scopes`
--
ALTER TABLE `scopes`
    ADD CONSTRAINT `users_scopes` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `social_accounts`
--
ALTER TABLE `social_accounts`
    ADD CONSTRAINT `users_social_accounts` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
