import repo_functions as functions
projDir = "/users/nmtarr/documents/ncba/"

dataDir = projDir + "data/"

inDir = dataDir + "inputs/"

outDir = dataDir + "outputs/"

summ_db = outDir + "testDB.sqlite"

gap_id = "bwewax"

NChucs = inDir + "NC_hucs"

NCBAblocks = inDir + "ncba_blocks"

NCcounties = inDir + "NC_counties"

functions.make_summary_db(summary_db = summ_db, gap_id, inDir, outDir, NChucs, NCBAblocks, NCcounties)

occurrence_db = outDir + "bloshx0GBIFr19GBIFf8"

functions.occurrence_records_to_db(occurrence_db, summ_db, "2017, 2018", "11, 12, 1")
