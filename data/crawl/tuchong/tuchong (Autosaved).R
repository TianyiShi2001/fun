library(tidyverse)

# 题材 <- c('人像', '纪实', '人文', '风光', ' 街拍')
题材 <- c('jk', 'lolita', '漫展', 'cosplay', '私房', '汉服', '和服', '写真', '性感', '情绪', '时尚')
器材 <- c('索尼', '佳能', '尼康', '徕卡', '富士')


# 数据导入和转换 -----------------------------------------------------------------

tag_info <- tibble(post_id = integer(0), tag = character(0))
for(i in 题材){
  filename = str_c(i, '/data/tag_info.csv')
  t = read_csv(filename, skip = 1, col_types = 'ic')
  tag_info = bind_rows(tag_info, t)
}
tag_info <- distinct(tag_info)
tag_info
# tag_info <- add_column(tag_info, date = Sys.Date())

post_info <- tibble()
for(i in 题材){
  filename = str_c(i, '/data/post_info.csv')
  t = read_csv(filename, skip = 1, col_types = 'iiccTiii')
  post_info = bind_rows(post_info, t)
}
post_info <- distinct(post_info, post_id, .keep_all = TRUE)
post_info

tag_info_collapsed <- tag_info %>% 
  group_by(post_id) %>% 
  summarise(collapsed_tag = str_c(tag, collapse = ' '))
tag_info_collapsed


# 使获赞数能够轻易用post_id获取（字符索引向量） ----------------------------------------------

fav <- post_info$favorites
names(fav) <- post_info$post_id


# 器材与题材的关联 ----------------------------------------------------------------

association <- expand_grid(题材, 器材) %>% 
  mutate(post_ids = map2(题材, 器材, ~ tag_info_collapsed$post_id[
                                str_detect(tag_info_collapsed$collapsed_tag, regex(.x, ignore_case = TRUE))&
                                str_detect(tag_info_collapsed$collapsed_tag, regex(.y, ignore_case = TRUE))
                              ]),
         count = sapply(post_ids, length),
         favs = map(post_ids, ~ fav[as.character(.)]),
         total_favs = sapply(favs, sum),
         mean_fav = total_favs/count,
         median_fav = sapply(favs, median),
         t = qt(0.975, count),
         SE = map2_dbl(favs, count, ~ sd(.x)/sqrt(.y)),
         ymin = mean_fav - t*SE,
         ymax = mean_fav + t*SE
        )


# 使得facet_wrap根据题材的获赞数中位数/平均数之和排列 -------------------------

association1 <- association %>%
  mutate(题材 = fct_reorder(association$题材, -median_fav, sum))

association2 <- association %>%
  mutate(题材 = fct_reorder(association$题材, -mean_fav, sum))

# 设置ggplot全局theme ---------------------------------------------------------

theme_set(
  theme_bw()+
    theme(text = element_text(family = 'Source Han Serif SC'), 
          plot.title = element_text(hjust = 0.5, size = 12, lineheight = 1),
          plot.subtitle = element_text(hjust = 0.5),
          plot.margin = margin(1,1,1,1,'cm'),
          plot.caption = element_text(hjust = 0))
)
  

ggplot(association1, aes(x = 器材))+
  geom_point(aes(y = median_fav, color = median_fav, size=count))+
  facet_wrap(~题材, scales='fixed', ncol = 3)+
  geom_text(aes(label = str_c('n=', count)), size = 3, y = 3)+
  scale_color_gradient(low = 'blue', high = 'red')+
  scale_y_continuous(limits = c(0,70), expand = c(0,0))+
  theme(legend.position = c(0.85,0.1), legend.direction = 'horizontal')+
  labs(x = '相机品牌', 'y' = '获赞数中位值', color = '获赞数中位值', size = '作品数量',
  title = '图虫网11种关于人像的tags的2019年9月22日当日热度前10000名的作品
       与5种主流相机品牌tags的关联：作品数量和获赞数中位值
       （谁能帮我想个顺一点的名字）', 
       subtitle = '作者：石天熠',
       caption = '
       注意：样本量非常小，方法很不严谨，仅供娱乐。索尼大法好。
       方法：在chomre中访问一个图虫网的任意一个tag的热度排名，如"https://tuchong.com/tags/cosplay", 监视XHR，
                得到用于获取作品信息的ajax请求，如"https://tuchong.com/rest/tags/cosplay/posts?page=1>&count=20&order=weekly"
                不断尝试，发现参数page和count的最大值都是100，即最大获取10000组作品信息，order参数为new, weekly或daily
                于是便可以用python抓取数据，整理，并到本地为csv. 然后用R分析数据。
                （我的python脚本还可以根据tags生成词云，以及下载图片）
                项目代码在https://github.com/TianyiShi2001/fun/data/crawl/tuchong，
                第一次用python和R做事，代码写得很乱，清多多包涵。')

ggplot(association2, aes(x = 器材, y = mean_fav))+
  geom_point(aes(size = count))+
  geom_text(aes(label = str_c('n=', count)), size = 3, y = -50)+
  geom_errorbar(aes(ymin = ymin, ymax = ymax), width = 0.5)+
  facet_wrap(~题材, scales='fixed', ncol = 3)+
  scale_color_gradient(low = 'blue', high = 'red')+
  theme(legend.position = c(0.9,0.1), legend.direction = 'horizontal')+
  labs(x = '相机品牌', 'y' = '获赞数')

ggsave('tuchong.png', width = 10, height = 15, dpi=600, scale = 0.9)



