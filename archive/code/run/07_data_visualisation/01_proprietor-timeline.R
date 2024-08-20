# library(XML)
library(ggplot2)
library(readr)
library(dplyr)
library(magrittr)
library(stringr)
library(glue)
library(tidyr)
library(extrafont)
library(forcats)



library(extrafont)
# library(remotes)
# remotes::install_version("Rttf2pt1", version = "1.3.8")
# extrafont::font_import("/Users/lisahopcroft_tmp/Library/Fonts")
# https://cran.r-project.org/web/packages/extrafont/README.html
loadfonts()

d_in = read_tsv( file="dat/castle-semple.tsv" )

d_tmp = d_in %>% 
  select( pers_id, pers_id_context, action,
          date1_y, date1_rel,
          date2_y, date2_rel,
          empire_proximity ) %>%
  mutate( this_person = as.character(glue("{pers_id} ({pers_id_context})")))

order_frame = d_tmp %>% 
  filter( action=="PROPRIETOR" ) %>% 
  group_by(this_person) %>% 
  mutate( order_data = min( c(date1_y,date2_y), na.rm=TRUE ) ) %>% 
  select( this_person, order_data )

d = d_tmp %>% 
  inner_join( order_frame, by="this_person") %>% 
  arrange( order_data ) %>% 
  select( this_person, action,
          date1_y, date1_rel,
          date2_y, date2_rel,
          order_data,
          empire_proximity )



# group_order = d %>% group_by(group_id) %>% 
#   summarise( start_year = min( order_data ) ) %>% 
#   arrange(start_year) %>% pull( group_id )
# 
# d = d %>% 
#   mutate( group_id = factor(group_id,
#                             levels=group_order,
#                             ordered=TRUE) )

person_labels = d_in %>% 
  select( pers_id, pers_id_context, action, date1_y ) %>% 
  mutate( this_person = as.character(glue("{pers_id} ({pers_id_context})"))) %>%
  pivot_wider( names_from = "action",
               values_from = "date1_y" ) %>% 
  mutate( pers_label = as.character(glue( "{pers_id} ({BORN}-{DIED})") )) %>% 
  select( this_person, pers_label ) %>% 
  mutate( pers_label = str_remove_all(pers_label,"NA" ) )

d_final = d %>%
  inner_join( person_labels, by="this_person" ) %>% 
  mutate( pers_label = factor(pers_label) ) %>% 
  mutate( pers_label = fct_reorder( pers_label, order_data, .desc = TRUE))

lifespan_data = d_final %>% 
  filter( action %in% c( "BORN", "DIED") ) %>% 
  pivot_wider( names_from = "action",
               values_from = "date1_y" ) %>% 
  select( pers_label, BORN, DIED ) %>% 
  complete( pers_label,
            fill=list(BORN = NA,
                      DIED = NA))

  ### ORDER THE PEOPLE
  # group_by( pers_label ) %>% 
  # mutate( order_data = mean(c(BORN,DIED),na.rm=T)) %>% 
  # ungroup() %>% 
  # mutate( plot_order = order(order_data) ) %>% 
  # arrange( plot_order ) %>% 
  ### REPLACE MISSING BORN/DIED DATA WITH THE MIN/MAX
  ### (TEMPORARY FIX TO ALLOW PLOT TO BE DRAWN)
  # mutate( BORN = ifelse( is.na(BORN),
  #                        min(BORN,na.rm=TRUE),
  #                        BORN) )  %>% 
  # mutate( DIED = ifelse( is.na(DIED),
  #                        max(DIED,na.rm=TRUE),
  #                        DIED) ) 

proprietor_data.complete = d_final %>% 
  filter( action %in% c( "PROPRIETOR") ) %>% 
  select( pers_label, date1_y, date2_y, empire_proximity ) %>% 
  filter( !is.na(date1_y) & !is.na(date2_y) )

proprietor_data.partial = d_final %>% 
  filter( action %in% c( "PROPRIETOR") ) %>% 
  select( pers_label,
          date1_y, date2_y,
          date1_rel, date2_rel,
          empire_proximity ) %>% 
  filter( is.na(date1_y) | is.na(date2_y) ) %>% 
  group_by(pers_label) %>% 
  mutate( direction = na.omit(c(date1_rel,date2_rel)) ) %>% 
  mutate( year = na.omit(c(date1_y,date2_y))) %>% 
  select( pers_label, year, direction, empire_proximity ) %>% 
  mutate( label = case_when( direction == "start" ~ "<U+1F780>",#"&#128898",#">",
                             direction == "end"   ~ "<",
                             direction == "on"    ~ "*",
                             TRUE ~ "!" )) %>% 
  mutate( hjust = case_when( direction == "start" ~ 0,
                             direction == "end"   ~ 1,
                             direction == "on"    ~ 0.5,
                             TRUE ~ 0.5 ) )


year_limits = c( 1600, 2000 )
year_string = paste(year_limits,collapse="-")


plot_colours = list(
  primary = "#456A8F",
  secondary = "#717074",
  tertiary = "#00323F",
  quaternary = "#00485A"
)

y_min = (d_final %>% pull(pers_label) %>% levels)[1]
y_max = (d_final %>% pull(pers_label) %>% levels %>% rev)[1]

HES_annotation = data.frame(
  xmin=1946,
  xmax=Inf,
  ymin=-Inf,
  ymax=Inf
  )

arrow_size = unit(0.30, "cm")
year_offset = 5.4


ggplot( ) +
  # geom_rect( data=HES_annotation,
  #            aes(xmin=xmin,
  #                xmax=xmax,
  #                ymin=ymin,
  #                ymax=ymax),
  #            fill="grey", alpha=0.5 ) +
  # geom_vline(xintercept = 1946) +
  geom_segment( data=lifespan_data,
                 aes( x=BORN, xend=DIED,
                      y=pers_label, yend=pers_label) ) +
  geom_segment(data=proprietor_data.complete,
               aes( x=date1_y, xend=date2_y,
                    y=pers_label, yend=pers_label,
                    col=empire_proximity ),
               size=7.5) +
  # geom_text(data=proprietor_data.partial,
  #              aes(x=year,y=pers_label,
  #                  label=label, hjust=hjust,
  #                  col=empire_proximity)) +
  geom_segment(data=proprietor_data.partial %>% filter( direction != "end") ,
               aes(x=year,xend=year+year_offset,
                   y=pers_label, yend=pers_label,
                   col=empire_proximity),
               linejoin="mitre",lineend="butt",
               size=1,
               arrow = arrow(length = arrow_size,type="closed",
                             angle=45)
               ) +
  geom_segment(data=proprietor_data.partial %>% filter( direction != "start") ,
               aes(x=year,xend=year-year_offset,
                   y=pers_label, yend=pers_label,
                   col=empire_proximity),
               linejoin="mitre",lineend="butt",
               size=1,
               arrow = arrow(length = arrow_size,type="closed",
                             angle=45)
  ) +
  
  scale_x_continuous(limits = year_limits,
                     expand = c(0,0) )+
  theme_minimal() +
  labs( title="") +
  ylab("") +
  xlab("" ) +
  # annotate( "text",
  #           x=1946, y=3,
  #           size=3,
  #           vjust=1.8,
  #           # hjust=0.2,
  #           label="State care" %>% toupper(),
  #           angle=90,
  #           family="GothamSSm-Book",
  #           col=grey(0.55)
  #           ) +
  theme(text=element_text(family="GothamSSm-Book"),
        strip.placement = "outside",
        axis.ticks = element_blank(),
        axis.text.y = element_text(hjust=0,
                                   size=11,
                                   margin=unit(c(0,0.8,0,0),"cm")),
        axis.text.x = element_text(colour="grey"),
        plot.margin=unit(c(-0.5,0.8,-0.4,-0.4),"cm"),
        legend.position="none",
        # axis.line.y.left   = element_line(color = 'black'),
        strip.background = element_rect(colour=NA,
                                        fill=alpha(plot_colours$tertiary, 0.2) )
  )

  
ggsave( "fig/Castle-Semple_proprietors_plot.png",
        width = 10,
        height = 3,
        units = "in")


