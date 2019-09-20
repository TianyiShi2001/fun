# 数据来源：中华人民共和国国家国家数据网站（http://data.stats.gov.cn）

library(tidyverse)

# 读取数据 --------------------------------------------------------------------

# 人口抽样调查之样本容量
sample_size <- readxl::read_excel('../data/china/sample_size.xls', skip = 2) %>% 
  slice(1) %>% select(-1) %>% 
  gather(`2017年`:`2003年`, key = '年份', value = 'n') %>% 
  mutate(年份 = parse_number(年份))

# 2003-2017人口抽样调查的男女比例
sex <- readxl::read_excel('../data/china/sex_ratio.xls', skip = 2) %>% 
  slice(-23, -22, -1) %>% 
  gather(`2017年`:`2003年`, key = '年份', value = '男女比例') %>% 
  rename(年龄段 = 指标) %>% 
  mutate(年龄段 = as_factor(str_extract(年龄段, '.+岁(以上)?'))) %>% 
  mutate(年份 = parse_number(年份)) %>%
  left_join(sample_size) %>% 
  filter(年份 != 2010)

# 2000年人口普查
pucha2000 <- readxl::read_excel('../data/china/pucha2000.xls', skip = 3) %>% 
  select(1, 8) %>% 
  rename(年龄段 = 1, 男女比例 = 2) %>% 
  filter(年龄段 %in% sex$年龄段) %>% 
  add_column(年份 = 2000, n = 1242612226)

# 2010年人口普查
pucha2010 <- readxl::read_excel('../data/china/pucha2000.xls', skip = 3) %>% 
  select(1, 8) %>% 
  rename(年龄段 = 1, 男女比例 = 2) %>% 
  filter(年龄段 %in% sex$年龄段) %>% 
  add_column(年份 = 2010, n = 1332810869)

# 人口抽样调查和两次人口普查的男女比例
sex_0 <- sex %>% 
  bind_rows(pucha2000) %>% 
  bind_rows(pucha2010) %>% 
  mutate(年龄段 = as_factor(str_extract(年龄段, '.+岁(以上)?')))


# 绘图设置（全局） ----------------------------------------------------------------

theme_set(
  theme_bw()+
    theme(text = element_text(family = 'Source Han Serif SC'),
          plot.margin = margin(0.7, 0.3, 0.7, 0.3, 'cm'),
          plot.title = element_text(hjust = 0.5),
          plot.subtitle = element_text(hjust = 0.5),
          plot.caption = element_text(hjust = 0))
)

col <- list(
  scale_color_brewer(palette = "Set2")
)

sx <- function(min, max, gap){
  scale_x_continuous(breaks = seq(min, max, gap))
}

sy <- scale_y_continuous(breaks = c(90, 95, 100, 105, 110, 115, 120, 125, 130, 135))

author <- '数据来源：中华人民共和国国家统计局国家数据网站\n数据处理/制图：石天熠'

# 绘图（仅人口抽样调查） -------------------------------------------------------------

# 抽取0-29岁，年份不为2010的数据
sex_1 <- sex %>% 
  filter(!str_detect(年龄段, '^[3-9](0|5)')) %>% 
  filter(年份 != 2010)

# 2003-2017年人口抽样调查：0至29岁人口的按年龄段的男女比例
ggplot(sex_1, aes(年份, 男女比例))+
  geom_line()+
  geom_point(size = 1)+
  facet_wrap(~年龄段, nrow = 1)+
  labs(title = "2003-2017年人口抽样调查：0至29岁人口的按年龄段的男女比例（男/100女）", 
       subtitle = author,
       caption = '注：因为2010年有人口普查，所以没有进行人口抽样调查。')+
  sx(2003, 2017, 2)+
  sy+
  theme(axis.text = element_text(angle = 45, hjust = 1), panel.grid.minor = element_blank())

ggsave('plot/抽样_源.png', width = 10, height = 5)

# 为预测做准备
sex2 <- sex_1 %>% 
  mutate(diff = 20 - as.double(str_extract(年龄段, '\\d{1,2}')),
         年份 = 年份 + diff)

# 通过2003-2017年人口抽样调查之按年龄男女性别比预测的20-24岁年龄段的男女性别比（男/100女）（无加权）
ggplot(sex2, aes(年份, 男女比例))+
  geom_line(aes(color = 年龄段))+
  geom_smooth(aes(weight = n), alpha = 0.3, span = 0.7)+
  labs(title = "通过2003-2017年人口抽样调查之按年龄男女性别比\n预测的20-24岁年龄段的男女性别比（男/100女）（无加权）", 
       subtitle = author,
       caption = '注1：因为2010年有人口普查，所以没有进行人口抽样调查。\n注2：用n-n+5岁年龄段在m年的男女比例预测20-24岁年龄段在m+(20-n)年的男女比例。假设0-29岁男女死亡率相等，且人口抽样调查没有偏差。',
       color = '源数据\n（年龄段）')+
  col+
  sx(1996, 2040, 4)+
  sy

ggsave('plot/抽样_预测_无加权.png', width = 10, height = 8)

ggplot(sex2, aes(年份, 男女比例))+
  geom_line(aes(color = 年龄段))+
  geom_point(aes(size = n), show.legend = FALSE)+
  geom_smooth(aes(weight = n), alpha = 0.3, span = 0.7)+
  labs(title = "通过2003-2017年人口抽样调查之按年龄男女性别比\n预测的20-24岁年龄段的男女性别比（男/100女）（加权）", 
       subtitle = author,
       caption = '注1：因为2010年有人口普查，所以没有进行人口抽样调查。\n注2：点的大小代表样本量。2005和2015年进行了1%人口抽样调查，其他年份为5‰人口抽样调查。\n注3：用n-n+5岁年龄段在m年的男女比例预测20-24岁年龄段在m+(20-n)年的男女比例。假设0-29岁男女死亡率相等，且人口抽样调查没有偏差。',
       color = '源数据\n（年龄段）')+
  col+
  sx(1996, 2040, 4)+
  sy

ggsave('plot/抽样_预测_加权.png', width = 10, height = 8)


# 绘图（人口抽样调查和人口普查） ---------------------------------------------------------

sex_1 <- sex_0 %>% 
  filter(!str_detect(年龄段, '^[3-9](0|5)'))


ggplot(sex_1, aes(年份, 男女比例))+
  geom_line()+
  geom_point(data = filter(sex_1, 年份 == 2000 | 年份 ==2010), shape = 1, size = 5, color = 'red')+
  facet_wrap(~年龄段, nrow = 1)+
  labs(title = "中国0至29岁人口的按年龄段的男女比例（男/100女）", 
       subtitle = author,
       caption = '注：2000年和2010年的数据来自人口普查，2003年至2009和2011至2017年的数据来自人口抽样调查。')+
  scale_y_continuous(breaks = c(95, 100, 105, 110, 115, 120, 125))+
  scale_x_continuous(breaks = seq(2000,2018,2))+
  theme(axis.text = element_text(angle = 45, hjust = 1), panel.grid.minor = element_blank())

ggsave('plot/抽样和普查_源.png', width = 10, height = 5)

sex2 <- sex_1 %>% 
  mutate(diff = 20 - as.double(str_extract(年龄段, '\\d{1,2}')),
         年份 = 年份 + diff)

ggplot(sex2, aes(年份, 男女比例))+
  geom_line(aes(color = 年龄段))+
  geom_smooth(alpha = 0.3, span = 0.7)+
  labs(title = "通过2003-2017年人口抽样调查和2000、2010年人口普查的按年龄男女性别比\n预测的20-24岁年龄段的男女性别比（男/100女）（无加权）", 
       subtitle = author,
       caption = '注：用n-n+5岁年龄段在m年的男女比例预测20-24岁年龄段在m+(20-n)年的男女比例。假设0-29岁男女死亡率相等，且人口抽样调查没有偏差。',
       color = '源数据\n（年龄段）')+
  col+
  sx(1996, 2040, 4)+
  sy

ggsave('plot/抽样和普查_预测_无加权.png', width = 10, height = 8)


ggplot(sex2, aes(年份, 男女比例))+
  geom_line(aes(color = 年龄段))+
  geom_point(aes(size = n), show.legend = FALSE)+
  geom_smooth(aes(weight = n), alpha = 0.3)+
  labs(title = "通过2003-2017年人口抽样调查和2000、2010年人口普查的按年龄男女性别比\n预测的20-24岁年龄段的男女性别比（男/100女）（加权）", 
       subtitle = author,
       caption = '注1：用n-n+5岁年龄段在m年的男女比例预测20-24岁年龄段在m+(20-n)年的男女比例。假设0-29岁男女死亡率相等，且人口抽样调查没有偏差。\n注2：点的大小代表样本量。2005和2015年进行了1%人口抽样调查，其他年份为5‰人口抽样调查。',
       color = '源数据\n（年龄段）')+
  col+
  sx(1996, 2040, 4)+
  sy

ggsave('plot/抽样和普查_预测_加权.png', width = 10, height = 8)

# 《计划生育技术服务管理条例》第二章（技术服务） 第十五条 任何机构和个人不得进行非医学需要的胎儿性别鉴定或者选择性别的人工终止妊娠。
# 第六章 附则  第四十二条 本条例自 2001年10月1日起施行。 

