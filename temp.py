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

functions.make_summary_db(summ_db, gap_id, inDir, outDir, NChucs, NCBAblocks, NCcounties)
