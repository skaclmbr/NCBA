import repo_functions as functions
projDir = "/users/nmtarr/documents/ncba/"
codeDir = "/users/nmtarr/code/NC-BBA/"
dataDir = projDir + "data/"
inDir = dataDir + "inputs/"
outDir = dataDir + "outputs/"
gap_id = "bblskx"
summary_id = "summer1"
summary_db = outDir + gap_id + "_summer1.sqlite"
NChucs = inDir + "NC_hucs"
NCBAblocks = inDir + "ncba_blocks"
NCcounties = inDir + "NC_counties"
occurrence_db = outDir + gap_id + "0GBIFr19GBIFf8.sqlite"

functions.download_GAP_range_CONUS2001v1(gap_id=gap_id, toDir=inDir)

functions.make_summary_db(summary_db=summary_db, gap_id=gap_id, inDir=inDir,
                          outDir=outDir, NChucs=NChucs, NCBAblocks=NCBAblocks,
                          NCcounties=NCcounties)

functions.occurrence_records_to_db(occurrence_db, summary_db,
                                    "2014,2015,2016,2017,2018,2019",
                                    "4,5,6,7,8,")

functions.summarize_by_features(features='NChucs', summary_id = summary_id,
                        gap_id = gap_id, summary_db=summary_db,
                        outDir=outDir, codeDir=codeDir)

functions.summarize_by_features(features='NCcounties', summary_id = summary_id,
                        gap_id = gap_id, summary_db=summary_db,
                        outDir=outDir, codeDir=codeDir)

functions.summarize_by_features(features='NCBAblocks', summary_id = summary_id,
                        gap_id = gap_id, summary_db=summary_db,
                        outDir=outDir, codeDir=codeDir)




################################################################################
################################################################################
functions.export_shapefile(database=summary_db, table='NCcounties',
                           geometry_column='geom_4326',
                           output_directory=outDir,
                           shapefile_name='bloshxCounty', encoding='utf-8')

functions.export_shapefile(database=summary_db, table='NChucs',
                           geometry_column='geom_4326',
                           output_directory=outDir,
                           shapefile_name='bloshxHucs', encoding='utf-8')

functions.export_shapefile(database=summary_db, table='NCBAblocks',
                           geometry_column='geom_4326',
                           output_directory=outDir,
                           shapefile_name='bloshxBlocks', encoding='utf-8')



###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

DROP VIEW nontarget;
CREATE VIEW nontarget AS
					SELECT st_union(geom_4326)
                    FROM NCcounties
                    WHERE sufficient_count = 1;

CREATE TABLE target AS
                    SELECT *
                    FROM NC_counties
                    WHERE geom_4326 Touches(SELECT St_union(geom_4326)
                                            FROM NCcounties
                                            WHERE sufficient_count = 1);


Select f.field1 as field1, st_union(f.geometry) as geometry
From tableA as f
Group by field1;




################################################################################
