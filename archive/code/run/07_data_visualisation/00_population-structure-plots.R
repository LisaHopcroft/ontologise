# library(XML)
library(ggplot2)
library(readr)
library(dplyr)
library(magrittr)
library(stringr)
library(glue)

### READS PEOPLA FILES IN THE DAT/ DIRECTORY AND GENERATES
### A PLOT SHOWING THE POPULATION STRUCTURE ACCORDING TO 
### AGE AND GENDER.

### SAVES PLOTS TO THE FIG/ DIRECTORY. 

# ## pyramid charts are two barcharts with axes flipped
# pyramidGH2 <- ggplot(popGH, aes(x = Age, y = Population, fill = Gender)) + 
#   geom_bar(data = subset(popGH, Gender == "Female"), stat = "identity") +
#   geom_bar(data = subset(popGH, Gender == "Male"), stat = "identity") + 
#   scale_y_continuous(labels = paste0(as.character(c(seq(2, 0, -1), seq(1, 2, 1))), "m")) + 
#   coord_flip()

update_bin_string = function( s ) {
  s_out = "Missing"
  
  if ( !is.na( s ) ) {
    
    s_in = s %>% as.character()
    
    s_list = s %>% 
      as.character() %>% 
      str_replace_all( "[\\[\\]]", "" ) %>% 
      str_replace_all( "[\\(\\)]", "" ) %>% 
      str_split(",") %>% 
      unlist %>% 
      as.numeric()
    
    if ( str_detect( s_in, "\\)$" ) ) {
      s_list[2] = s_list[2] - 1
    }
    
    s_out = s_list %>% paste(collapse="-")
  }
  
  return( s_out )
  
}

for ( d_file in dir( path="dat", pattern="*.PEOPLA.tsv", full.names = TRUE ) ) {
  
  cat( sprintf( "FILE: %s\n", d_file ) )
  
  d_in = read_tsv( file=d_file )
  
  d = d_in %>%
    rename( sex = pers_sex ) %>% 
    mutate( age = as.numeric( pers_aged ) ) %>% 
    filter( !is.na(age) ) 
  
  if ( nrow( d ) > 0 ) {
    
    if ( !all(is.na(d$sex)) & !all(is.na(d$age))) {
      
      d = d %>% 
        select( sex, age ) %>% 
        mutate( age_cut = cut( age, breaks = seq(0, 100, 5), right = FALSE ) ) %>% 
        rowwise()  %>% 
        mutate( age_bin = as.factor( update_bin_string( age_cut ) ) ) %>% 
        arrange( age ) %>%
        mutate( age_bin = factor(age_bin, levels=age_bin) ) %>% 
        group_by( sex, age_bin ) %>% 
        summarise( n = n() ) %>% 
        mutate( n = ifelse( sex == "Male", -1*n, n ))
      
      ggplot( d,
              aes( x = age_bin, y=n, fill=sex )) +
        geom_histogram( stat="identity" ) + coord_flip() +
        labs( title = d_file )
      
      d_plot = d_file %>%
        str_replace( "\\.tsv$", "\\.png" ) %>% 
        str_replace( "^dat/", "fig/" )
      
      ggsave( file=d_plot )
    }
    
  }  
}
