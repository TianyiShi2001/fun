library(tidyverse)

# retry apparent no-specials ----------------------------------------------

special <- read_csv('special.csv')
retry_index <- special$url %>% str_detect('\\d+$')
retry_id <- special[retry_index, ]$id

write(retry_id, 'error.txt', sep = '\n', append = TRUE)

special <- special[!retry_index, ]

write_csv(special, 'special_real.csv', append = TRUE)
write('id, url', 'special.csv', append = FALSE)