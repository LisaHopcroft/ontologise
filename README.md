# ontologise
Code to leverage insight from marked up historical sources

## Drawing graphs

```command
(base) lisahopcroft@ ontologise % pwd 
/Users/lisahopcroft/Projects/ontologise
(base) lisahopcroft@ ontologise % python kml_to_tsv.py
Reading this directory /Users/lisahopcroft/Dropbox/A Glance Ayont The Grave/^img
Reading this directory /Users/lisahopcroft/Dropbox/A Glance Ayont The Grave/kml
Reading frames file frame.kml
Reading polygon file 1808_parcels.kml
Reading polygon file 1944_parcels.kml
Reading polygon file 1856_parishes.kml
Reading polygon file land_water.kml
Reading polygon file land.kml
Reading paths file 1856_roads.kml
Reading paths file 1856_rivers.kml
Reading paths file 1856_tracks.kml
Reading paths file 1856_burns.kml
Reading paths file 1856_paths.kml
(base) lisahopcroft@ ontologise % /Library/Frameworks/R.framework/Resources/Rscript --vanilla 02_draw-map.R -f "data/kml/ALL.tsv" -s "styles.tsv" -d "fig" -o "output_map.png" -r 600
Warning message:
package ‘glue’ was built under R version 4.1.2 
Warning message:
package ‘magrittr’ was built under R version 4.1.2 
Warning message:
package ‘mapproj’ was built under R version 4.1.2 
Warning message:
No shared levels found between `names(values)` of the manual scale and the data's shape values. 
Saving map to fig/output_map.pngSaving 7 x 7 in image
Warning message:
No shared levels found between `names(values)` of the manual scale and the data's shape values. 

```
