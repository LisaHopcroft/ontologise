suppressMessages( library( optparse, quietly=TRUE ) )
suppressMessages( library( glue    , quietly=TRUE ) )

option_list = list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="base dataset file name", metavar="character"),
  make_option(c("-s", "--style"), type="character", default=NULL,
              help="stylesheet for mapp", metavar="character"),
  make_option(c("-r", "--res"), type="integer", default=300,
              help="resolution (DPI)", metavar="integer"),
  make_option(c("-x", "--width"), type="integer", default=7,
              help="width (inches)", metavar="integer"),
  make_option(c("-y", "--height"), type="integer", default=7,
              help="height (inches)", metavar="integer"),
  make_option(c("-d", "--outputdir"), type="character", default=".",
              help="output directory for map [default=%default]", metavar="character"),
  make_option(c("-o", "--outputfile"), type="character", default="map.png",
              help="output file for map [default=%default]", metavar="character")
)

opt_parser = OptionParser(option_list=option_list)
opt        = parse_args(opt_parser)

# opt$base = "/Users/lisahopcroft_tmp/Dropbox/cairn.westindies.scot/bin/kml/LWH/ALL.tsv"
# opt$annotations = "/Users/lisahopcroft_tmp/Dropbox/cairn.westindies.scot/bin/kml/LWH/HIGHLIGHT.tsv"
# opt$style = "/Users/lisahopcroft_tmp/Dropbox/cairn.westindies.scot/bin/kml/styles.tsv"
# opt$outputdir = "fig"
# opt$outputfile = "map_out.png"

# opt$base = "kml/LWH/ALL.tsv"
# opt$annotations = "kml/tmp.tsv"
# opt$style = "kml/styles.tsv"
# opt$outputdir = "../site/img/maps/win"
# opt$outputfile = "WIN_VIN.png"

# opt$file = "data/kml/ALL.tsv"
# opt$style = "styles.tsv"
# opt$outputdir = "fig"
# opt$outputfile = "out.png"
# opt$width = 7
# opt$height = 7


quit_flag = 0

if ( is.null(opt$file) | is.null(opt$style) ) {
  cat( "\n[ERROR] crucial information is missing \n")
  if (is.null(opt$file) ) { ( cat( "------> file not provided\n" ) ) }
  if (is.null(opt$style)) { ( cat( "------> stylesheet not provided\n" ) ) }
  quit_flag = 1
}

if ( !dir.exists(opt$outputdir) ) {
  cat( "\n[ERROR] output directory provided does not exist\n" )
  cat( sprintf( "------> %s\n", opt$outputdir ) )
  quit_flag = 2
}

if ( !is.null(opt$file)  ) {
  if ( !file.exists(opt$file) ) {
    cat( "\n[ERROR] data file provided does not exist\n" )
    cat( sprintf( "------> %s\n", opt$file ) )
    quit_flag = 2
  }
}

if ( !is.null(opt$style) ) {
  if ( !file.exists(opt$style) ) {
    cat( "\n[ERROR] stylesheet file provided does not exist\n" )
    cat( sprintf( "-------> %s\n", opt$style ) )
    quit_flag = 2
  }
}

if ( quit_flag ) {
  cat( "\n" )
  quit( status=quit_flag )
  }


suppressMessages( library(ggplot2 , quietly=TRUE) )
suppressMessages( library(readr   , quietly=TRUE) )
suppressMessages( library(dplyr   , quietly=TRUE) )
suppressMessages( library(magrittr, quietly=TRUE) )
suppressMessages( library(stringr , quietly=TRUE) )
suppressMessages( library(ggrepel , quietly=TRUE) )
suppressMessages( library(mapproj , quietly=TRUE) )
suppressMessages( library(forcats , quietly=TRUE) )

input_file  = opt$file
style_file  = opt$style
output_file = glue("{opt$outputdir}/{opt$outputfile}")
img_res = opt$res
fig_width = opt$width
fig_height = opt$height

print (glue("Writing output file to: {output_file}"))

#####################################################################
### Reading in the data and styling information #####################
#####################################################################

### This file contains the x/y (lat/lon) data for the map.
d_in = read_tsv( file=input_file, show_col_types = FALSE,
                 col_types = cols(label = col_character()) )


### This file contains the styling information for the map.
### It describes the attributes for each class of object - attribute
### names are taken from CSS.
### NB. class names should be unique across all types of object,
###     unless those objects should be styled the same. For example,
###     a 'point' of class 'highlight' will be styled in the same way
###     as a 'poly' of class 'highlight'.
stylesheet = read_tsv(file=style_file, show_col_types = FALSE )


### This is a mapping from the ggplot keywords to the CSS
### keywords, and vice versa. It helps us to map between them later
### on.
css2ggplot = list(
  `border-color` = "colour",
  `R_shape`      = "shape",
  `background-color` = "fill",
  `border-style` = "linetype",
  `text-color` = "colour",
  `font-size` = "size",
  `font-weight` = "face",
  `text-align` = "hjust"
)


### If a datapoint belongs to a class that is not defined in the
### stylesheet, it should assume some default formatting. That
### default formatting is given below. Note that numeric values
### should be provided as characters (these will be converted
### to numeric values later).
DEFAULT_styling = tribble( 
  ~type  , ~attribute        , ~value,
  "point", "border-color"    , "#aaaaaa",
  "point", "R_shape"         , "20",
  "point", "background-color", "#aaaaaa",
  "poly" , "border-color"    , "#000000",
  "poly" , "background-color", "#ffffff",
  "poly" , "border-style"    , "solid",
  "path" , "border-color"    , "#000000",
  "path" , "background-color", "#ffffff",
  "path" , "border-style"    , "solid"
)

### Here, the styling provided in the style sheet is converted
### to the necessary scales (e.g., scale_colour_manual) for ggplot.
### This is done for points and polygons separately at the moment,
### but I think it could be possible to combine them.

### (1) point styling 
point_styling = d_in %>% 
  filter( type == "point" ) %>% 
  select( type, class ) %>% unique() %>% 
  inner_join( stylesheet, by="class" )


for ( this_attribute in c( "border-color",
                           "R_shape" ) ) {
  
  this_scheme = point_styling[this_attribute] %>% unlist
  names(this_scheme) = point_styling %>% pull( class ) %>% unlist
  
  undefined_classes = setdiff( d_in %>% filter( type=="point" ) %>% pull( class ) %>% unique(),
                               names(this_scheme) )
  
  if ( length(undefined_classes) ) { 
  for ( default_class in undefined_classes ) {
    this_value = DEFAULT_styling %>%
      filter( type == "point" ) %>%
      filter( attribute == this_attribute ) %>% 
      pull( value )
    
    if( str_detect(this_value, "^[:digit:]+$") ) {
      this_value = as.numeric(this_value)
    }
    
    this_scheme[ default_class ] = this_value
  }
  }
  
  assign( glue("point_{css2ggplot[this_attribute]}_scheme"),
          this_scheme )
  
}

### (2) polygon styling 
polygon_styling = d_in %>% 
  filter( type == "poly" ) %>% 
  select( type, class) %>% unique() %>% 
  inner_join( stylesheet, by="class")

for ( this_attribute in c( "border-color",
                           "background-color",
                           "border-style" ) ) {
  
  this_scheme = polygon_styling[this_attribute] %>% unlist
  names(this_scheme) = polygon_styling %>% pull( class ) %>% unlist

  undefined_classes = setdiff( d_in %>% filter( type=="poly" ) %>% pull( class ) %>% unique(),
                               names(this_scheme) )
  
  if ( length(undefined_classes) ) { 
    
    for ( default_class in undefined_classes ) {
      this_value = DEFAULT_styling %>%
        filter( type == "poly" ) %>%
        filter( attribute == this_attribute ) %>% 
        pull( value )
      
      if( str_detect(this_value, "^[:digit:]+$") ) {
        this_value = as.numeric(this_value)
      }
      
      this_scheme[ default_class ] = this_value
    }
  }
  
  assign( glue("polygon_{css2ggplot[this_attribute]}_scheme"),
          this_scheme )
  
}


### (3) path styling 
path_styling = d_in %>% 
  filter( type == "path" ) %>% 
  select( type, class) %>% unique() %>% 
  inner_join( stylesheet, by="class")

for ( this_attribute in c( "border-color",
                           "background-color",
                           "border-style" ) ) {
  
  this_scheme = path_styling[this_attribute] %>% unlist
  names(this_scheme) = path_styling %>% pull( class ) %>% unlist
  
  undefined_classes = setdiff( d_in %>% filter( type=="path" ) %>% pull( class ) %>% unique(),
                               names(this_scheme) )
  
  if ( length(undefined_classes) ) { 
    
    for ( default_class in undefined_classes ) {
      this_value = DEFAULT_styling %>%
        filter( type == "path" ) %>%
        filter( attribute == this_attribute ) %>% 
        pull( value )
      
      if( str_detect(this_value, "^[:digit:]+$") ) {
        this_value = as.numeric(this_value)
      }
      
      this_scheme[ default_class ] = this_value
    }
  }
  
  assign( glue("path_{css2ggplot[this_attribute]}_scheme"),
          this_scheme )
  
}


### (4) label styling 
label_styling = d_in %>% 
  filter( type == "point" ) %>% 
  filter( label != "" ) %>% 
  select( type, class ) %>% unique() %>% 
  inner_join( stylesheet, by="class" )

for ( this_attribute in c( "text-color",
                           "font-size"
                           # "font-weight",
                           # "font-style",
                           # "text-align"
                           ) ) {
  
  this_scheme = label_styling[this_attribute] %>% unlist
  names(this_scheme) = label_styling %>% pull( class ) %>% unlist
  
  undefined_classes = setdiff( d_in %>% filter( type=="label" ) %>% pull( class ) %>% unique(),
                               names(this_scheme) )
  
  if ( length(undefined_classes) ) { 
    
    for ( default_class in undefined_classes ) {
      this_value = DEFAULT_styling %>%
        filter( type == "label" ) %>%
        filter( attribute == this_attribute ) %>% 
        pull( value )
      
      if( str_detect(this_value, "^[:digit:]+$") ) {
        this_value = as.numeric(this_value)
      }
      
      this_scheme[ default_class ] = this_value
    }
  }
  
  assign( glue("label_{css2ggplot[this_attribute]}_scheme"),
          this_scheme )
  
}

#####################################################################
### Interpreting the data ###########################################
#####################################################################

### These data define the limits for the map - the 'type' of these
### datapoints are 'frame_TL' (frame top left) and 'frame_BR' (frame
### bottom right). It is a convenience that arranging 'frame_TL' and
### 'frame_BR' alphabetically will put them in the right order for 
### the limits object (i.e., east/north before west/south).
limits = d_in %>%
  filter( str_detect( type, "frame" ) )

#####################################################################
### Drawing the map! ################################################
#####################################################################

# d_in_old = d_in
# d_in = d_in_old
tmp = stylesheet %>%
  filter( !is.na( `text-transform`) ) %>%
  select( class, `text-transform` )

text_transformations = tmp$`text-transform`
names(text_transformations) = tmp$class


d_in_Zordered = d_in %>% inner_join( stylesheet %>% select( class, type, `z-index`),
                     by = c("type", "class") ) %>% 
  ### Set ordering of polygons using factors based on Z-index
  mutate( id = factor( id )) %>% 
  mutate( id = fct_reorder( id, `z-index` ) ) %>%
  ### Set ordering of points by ordering the data.frame using Z-index
  arrange( `z-index` ) %>% 
  ### amend labels using text-transform in stylesheet
  mutate( label = case_when(
    text_transformations[class] == "uppercase" ~ toupper( label ),
    text_transformations[class] == "lowercase" ~ tolower( label ),
    TRUE ~ label
  ) )

### This might help with text size:
### https://www.christophenicault.com/post/understand_size_dimension_ggplot2/

out_plot = 
    ggplot( ) +
      ### This draws all polygons, each polygon is defined by 'id'.
      ### Currently, polygons do not have a fill colour, but this is an
      ### easy fix (fill=class should be added inside the aes() call ).
      geom_polygon( data=d_in_Zordered %>% filter(type=="poly"),
                    aes( x=lon, y=lat,
                         group=id,
                         colour=class,
                         linetype=class,
                         fill=class) ) +
      ### This draws all polygons, each polygon is defined by 'id'.
      ### Currently, polygons do not have a fill colour, but this is an
      ### easy fix (fill=class should be added inside the aes() call ).
      geom_path( data=d_in_Zordered %>% filter(type=="path"),
                 aes( x=lon, y=lat,
                      group=id,
                      colour=class,
                      linetype=class
                      # fill=class
                      ) ) +
      ### This draws all points.
      geom_point( data=d_in_Zordered %>% filter(type=="point"),
                  aes( x=lon, y=lat,
                       colour=class,
                       shape=class ) ) +
    
      ### This will draw any labels
      geom_text_repel( data=d_in_Zordered %>% filter(type=="point"),
                  aes( x=lon, y=lat,
                       size = class,
                       label=label,
                       colour=class) )  +
    
      ### These are the colour schemes
      scale_colour_manual( values = c(point_colour_scheme,
                                      polygon_colour_scheme,
                                      path_colour_scheme,
                                      label_colour_scheme ) ) +
      scale_linetype_manual( values = c( polygon_linetype_scheme,
                                         path_linetype_scheme  ) ) +
      scale_shape_manual( values=point_shape_scheme ) +
      scale_fill_manual( values=c(polygon_fill_scheme,
                                  path_fill_scheme), na.value = NA ) +
      scale_size_manual( values = c( label_size_scheme ),
                         na.value = 3 ) +
      
      
      
      ### Use the right projection, xlim and ylim are defined here
      ### so that polygons will still be drawn correctly even if
      ### they extend beyond the limits.
      coord_map( xlim = limits$lon %>% sort,
                 ylim = limits$lat %>% sort ) +
      
      ### This will (1) remove plot annotations (axes, tick marks, ...)
      theme_void( ) +
      ### ... and (2) remove any legend 
      theme( legend.position = "none" ) +
      ### ... and (3) set the background colour of the plot
      theme(plot.background = element_rect(fill = stylesheet %>%
                                             filter(class=="body") %>%
                                             pull( `background-color` ),
                                           colour=NA) ) 
                                           
cat( sprintf("Saving map to %s", output_file) )

ggsave( output_file, out_plot, width=fig_width, height=fig_height, dpi=img_res )

