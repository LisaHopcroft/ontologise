# ontologise
Code to leverage insight from marked up historical sources

## Drawing graphs

```command
(base) % python run.py -d "..."
Reading this directory .../kml
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
(base) % base) lisahopcroft@ ontologise % Rscript --vanilla draw_map_from_KML.R -f "data/kml/ALL.tsv" -s styles.tsv -d "fig" -o "output_map.png" -r 600 --width 8 --height 8
Warning message:
package ‘glue’ was built under R version 4.1.2 
Warning message:
package ‘magrittr’ was built under R version 4.1.2 
Warning message:
package ‘mapproj’ was built under R version 4.1.2 
Writing output file to: fig/output_map.png
Saving map to fig/output_map.pngWarning message:
No shared levels found between `names(values)` of the manual scale and the data's shape values.

```
