import repo_functions as functions
projDir = "/users/nmtarr/documents/ncba/"
codeDir = "/users/nmtarr/code/NC-BBA/"
dataDir = projDir + "data/"
inDir = dataDir + "inputs/"
outDir = dataDir + "outputs/"
gap_id = "bloshx"
summary_id = "summer1"
summary_db = outDir + gap_id + "_summer1.sqlite"
NChucs = inDir + "NC_hucs"
NCBAblocks = inDir + "ncba_blocks"
NCcounties = inDir + "NC_counties"
occurrence_db = outDir + "bblskx0GBIFr19GBIFf8.sqlite"

#functions.download_GAP_range_CONUS2001v1(gap_id=gap_id, toDir=inDir)

functions.make_summary_db(summary_db=summary_db, gap_id=gap_id, inDir=inDir,
                          outDir=outDir, NChucs=NChucs, NCBAblocks=NCBAblocks,
                          NCcounties=NCcounties)

functions.occurrence_records_to_db(occurrence_db, summary_db,
                                    "2014,2015,2016,2017,2018,2019",
                                    "4,5,6,7,8,")

functions.summarize_by_features(features='NCcounties', summary_id = summary_id,
                        gap_id = gap_id, summary_db=summary_db,
                        outDir=outDir, codeDir=codeDir)

functions.summarize_by_features(features='NChucs', summary_id = summary_id,
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
select distinct retrievalDate from occurrence_records limit 1;
select distinct occurrenceDate, retrievalDate, retrievalDate - occurrenceDate from occurrence_records;

SELECT age FROM (SELECT occurrenceDate, retrievalDate - occurrenceDate AS age
                        FROM orange
                        ORDER BY occurrenceDate DESC
                        LIMIT 1);

SELECT MAX(age) FROM (SELECT occurrenceDate, retrievalDate - occurrenceDate AS age
                      FROM orange
                      ORDER BY occurrenceDate DESC
                      LIMIT 500);

ALTER TABLE NCcounties ADD COLUMN years_since_record INTEGER;

CREATE VIEW purple AS
                    SELECT OBJECTID, retrievalDate - occurrenceDate AS age
                    FROM orange
                    GROUP BY OBJECTID
                    HAVING MIN(age);

UPDATE NCcounties
SET years_since_record = (SELECT purple.age FROM purple WHERE purple.OBJECTID = NCcounties.OBJECTID);


##########################################################################################



/*
/*############################  How long since occurrence record in each feature?
#############################################################*/
ALTER TABLE sp_range ADD COLUMN eval INTEGER;

/*  Record in sp_range that gap and gbif agreed on species presence, in light
of the minimum_count for the species. */
UPDATE sp_range
SET eval = 1
WHERE record_count >= (SELECT minimum_count
                        FROM params.evaluations
                        WHERE evaluation_id = '{0}'
                        AND species_id = '{1}');

*/

/*#############################################################################
                               Export Maps
 ############################################################################*/
/*
/*  Create a version of sp_range with geometry  */
CREATE TABLE new_range AS
              SELECT sp_range.*, shucs.geom_102008
              FROM sp_range LEFT JOIN shucs ON sp_range.strHUC12RNG = shucs.HUC12RNG;

ALTER TABLE new_range ADD COLUMN geom_4326 INTEGER;

SELECT RecoverGeometryColumn('new_range', 'geom_102008', 102008, 'POLYGON', 'XY');

UPDATE new_range SET geom_4326 = Transform(geom_102008, 4326);

SELECT RecoverGeometryColumn('new_range', 'geom_4326', 4326, 'POLYGON', 'XY');

SELECT ExportSHP('new_range', 'geom_4326', '{2}{1}_CONUS_Range_2001v1_eval',
                 'utf-8');

/* Make a shapefile of evaluation results */
CREATE TABLE eval AS
              SELECT strHUC12RNG, eval, geom_4326
              FROM new_range
              WHERE eval >= 0;

SELECT RecoverGeometryColumn('eval', 'geom_4326', 4326, 'POLYGON', 'XY');

SELECT ExportSHP('eval', 'geom_4326', '{2}{1}_eval', 'utf-8');
*/
