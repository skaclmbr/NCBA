# Functions to help determine GBIF species code
def get_GBIF_species_key(scientific_name):
    """
    Description: Species-concepts change over time, sometimes with a spatial
    component (e.g., changes in range delination of closely related species or
    subspecies).  Retrieval of data for the wrong species-concept would introduce
    error.  Therefore, the first step is to sort out species concepts of different
    datasets to identify concepts that can be investigated.

    For this project/effort, individual species-concepts will be identified,
    crosswalked to concepts from various datasets, and stored in a table within
    a database.

    For now, a single species has been manually entered into species-concepts
    for development.
    """
    from pygbif import species
    key = species.name_backbone(name = 'Lithobates capito', rank='species')['usageKey']
    return key

# Function for connecting to sqlite database and loading spatialite capabilites
def spatialite(db):
    """
    Creates a connection and cursor for sqlite db and enables
    spatialite extension and shapefile functions.

    (db) --> cursor, connection

    Arguments:
    db -- path to the db you want to create or connect to.
    """
    import os
    import sqlite3
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    os.putenv('SPATIALITE_SECURITY', 'relaxed')
    connection.enable_load_extension(True)
    cursor.execute('SELECT load_extension("mod_spatialite");')

    return cursor, connection

# Function for exporting a shapefile from summary database
def export_shapefile(database, table, geometry_column, output_directory, shapefile_name, encoding='utf-8'):
    """
    Exports a shapefile from the database

    Arguments:
    database -- path to the database from which to export
    table -- name of the table to create shapefil from
    geometry_column -- name of the column containing geometries
    output_directory -- path to directory to save to
    shapefile_name -- what to name the output file
    encoding -- defaults to 'utf-8'
    """
    cursor, conn = spatialite(database)
    # Export occurrence 'points' as a shapefile (all seasons)
    cursor.execute("""SELECT ExportSHP('{0}', '{1}', '{2}{3}', '{4}');
                   """.format(table, geometry_column, output_directory,
                              shapefile_name, encoding))
    conn.commit()
    conn.close()
    del cursor
    return

# Function for displaying the maps that will be created.
def MapShapefilePolygons(map_these, title):
    """
    Displays shapefiles on a simple CONUS basemap.  Maps are plotted in the order
    provided so put the top map last in the listself.  You can specify a column
    to map as well as custom colors for it.  This function may not be very robust
    to other applications.

    NOTE: The shapefiles have to be in WGS84 CRS.

    (dict, str) -> displays maps, returns matplotlib.pyplot figure

    Arguments:
    map_these -- list of dictionaries for shapefiles you want to display in
                CONUS. Each dictionary should have the following format, but
                some are unneccesary if 'column' doesn't = 'None'.  The critical
                ones are file, column, and drawbounds.  Column_colors is needed
                if column isn't 'None'.  Others are needed if it is 'None'.
                    {'file': '/path/to/your/shapfile',
                     'alias': 'my layer'
                     'column': None,
                     'column_colors': {0: 'k', 1: 'r'}
                    'linecolor': 'k',
                    'fillcolor': 'k',
                    'linewidth': 1,
                    'drawbounds': True
                    'marker': 's'}
    title -- title for the map.
    """
    # Packages needed for plotting
    import matplotlib.pyplot as plt
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    from matplotlib.patches import Polygon
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import PathPatch

    # Basemap
    fig = plt.figure(figsize=(15,12))
    ax = plt.subplot(1,1,1)
    map = Basemap(projection='aea', resolution='i', lon_0=-79.8, lat_0=35.5,
                  height=410000, width=900000)
    map.drawcoastlines(color='grey')
    map.drawstates(color='grey')
    map.drawcountries(color='grey')
    map.fillcontinents(color='#a2d0a2',lake_color='#a9cfdc')
    map.drawmapboundary(fill_color='#a9cfdc')

    for mapfile in map_these:
        if mapfile['column'] == None:
            # Add shapefiles to the map
            if mapfile['fillcolor'] == None:
                map.readshapefile(mapfile['file'], 'mapfile',
                                  drawbounds=mapfile['drawbounds'],
                                  linewidth=mapfile['linewidth'],
                                  color=mapfile['linecolor'])
                # Empty scatter plot for the legend
                plt.scatter([], [], c='', edgecolor=mapfile['linecolor'],
                            alpha=1, label=mapfile['alias'], s=100,
                            marker=mapfile['marker'])

            else:
                map.readshapefile(mapfile['file'], 'mapfile',
                          drawbounds=mapfile['drawbounds'])
                # Code for extra formatting -- filling in polygons setting border
                # color
                patches = []
                for info, shape in zip(map.mapfile_info, map.mapfile):
                    patches.append(Polygon(np.array(shape), True))
                ax.add_collection(PatchCollection(patches,
                                                  facecolor= mapfile['fillcolor'],
                                                  edgecolor=mapfile['linecolor'],
                                                  linewidths=mapfile['linewidth'],
                                                  zorder=2))
                # Empty scatter plot for the legend
                plt.scatter([], [], c=mapfile['fillcolor'],
                            edgecolors=mapfile['linecolor'],
                            alpha=1, label=mapfile['alias'], s=100,
                            marker=mapfile['marker'])

        else:
            map.readshapefile(mapfile['file'], 'mapfile', drawbounds=mapfile['drawbounds'])
            for info, shape in zip(map.mapfile_info, map.mapfile):
                for thang in mapfile['column_colors'].keys():
                    if info[mapfile['column']] == thang:
                        x, y = zip(*shape)
                        map.plot(x, y, marker=None, color=mapfile['column_colors'][thang])

            # Empty scatter plot for the legend
            for seal in mapfile['column_colors'].keys():
                plt.scatter([], [], c=mapfile['column_colors'][seal],
                            edgecolors=mapfile['column_colors'][seal],
                            alpha=1, label=mapfile['value_alias'][seal],
                            s=100, marker=mapfile['marker'])

    # Legend -- the method that works is ridiculous but necessary; you have
    #           to add empty scatter plots with the symbology you want for
    #           each shapefile legend entry and then call the legend.  See
    #           plt.scatter(...) lines above.
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, loc='lower left',
               framealpha=1, fontsize='x-large')

    # Title
    plt.title(title, fontsize=20, pad=-40, backgroundcolor='w')
    return

# Function to get GAP range from ScienceBase
def download_GAP_range_CONUS2001v1(gap_id, toDir):
    """
    Downloads GAP Range CONUS 2001 v1 file and returns path to the unzipped
    file.  NOTE: doesn't include extension in returned path so that you can
    specify if you want csv or shp or xml when you use the path.
    """
    import sciencebasepy
    import zipfile

    # Connect
    sb = sciencebasepy.SbSession()

    # Search for gap range item in ScienceBase
    gap_id = gap_id[0] + gap_id[1:5].upper() + gap_id[5]
    item_search = '{0}_CONUS_2001v1 Range Map'.format(gap_id)
    items = sb.find_items_by_any_text(item_search)

    # Get a public item.  No need to log in.
    rng =  items['items'][0]['id']
    item_json = sb.get_item(rng)
    get_files = sb.get_item_files(item_json, toDir)

    # Unzip
    rng_zip = toDir + item_json['files'][0]['name']
    zip_ref = zipfile.ZipFile(rng_zip, 'r')
    zip_ref.extractall(toDir)
    zip_ref.close()

    # Return path to range file without extension
    return rng_zip.replace('.zip', '')

# Function to make a database for housing layers and occurrence records
def make_summary_db(summary_db, gap_id, inDir, outDir, NChucs, NCBAblocks, NCcounties):
    """
    Builds an sqlite database in which to store NC bird occurrence information.

    Arguments:
    summary_db -- name of database to create for evaluation.
    gap_id -- gap species code. For example, 'bAMROx'
    NChucs -- path to GAP's 12 digit hucs shapefile for NC.
    NCBAblocks -- path to NCBA blocks shapefile.
    NCcounties -- path to shapefile of NC counties.
    inDir -- project's input directory
    outDir -- output directory for this repo
    """
    import sqlite3
    import pandas as pd
    import os

    # Delete db if it exists
    if os.path.exists(summary_db):
        os.remove(summary_db)

    # Create the database
    cursorQ, conn = spatialite(summary_db)

    cursorQ.executescript("""SELECT InitSpatialMetadata(1);""")

    # Add the NChucs shapefile to the db.
    cursorQ.execute("""SELECT ImportSHP(?, 'NChucs', 'utf-8', 4326, 'geom_4326', 'HUC12RNG', 'POLYGON');""", (NChucs,))
    # Add the NCBA blocks shapefile to the db.
    cursorQ.execute("""SELECT ImportSHP(?, 'NCBAblocks', 'utf-8', 4326, 'geom_4326', 'BLOCK_QUAD', 'POLYGON');""", (NCBAblocks,))
    # Add the NC counties shapefile to the db.
    cursorQ.execute("""SELECT ImportSHP(?, 'NCcounties', 'utf-8', 4326, 'geom_4326', 'OBJECTID', 'POLYGON');""", (NCcounties,))

    # Load the GAP range csv, filter out some columns, rename others
    csvfile = inDir + gap_id + "_CONUS_RANGE_2001v1.csv"
    sp_range = pd.read_csv(csvfile, dtype={'strHUC12RNG':str})
    sp_range.to_sql('sp_range', conn, if_exists='replace', index=False)
    conn.commit() # Commit and close here, reopen connection or else code throws errors.
    conn.close()

    cursorQ, conn = spatialite(summary_db)

    sql1 = """
    ALTER TABLE sp_range RENAME TO garb;

    CREATE TABLE sp_range AS SELECT strHUC12RNG,
                                 intGapOrigin AS intGAPOrigin,
                                 intGapPres AS intGAPPresence,
                                 intGapRepro AS intGAPReproduction,
                                 intGapSeas AS intGAPSeason,
                                 Origin AS strGAPOrigin,
                                 Presence AS strGAPPresence,
                                 Reproduction AS strGAPReproduction,
                                 Season AS strGAPSeason
                          FROM garb;
    DROP TABLE garb;
    """
    cursorQ.executescript(sql1)

    sql3 = """
    CREATE TABLE season AS SELECT sp_range.strHUC12RNG, sp_range.strGAPSeason, NChucs.geom_4326
                             FROM NChucs INNER JOIN sp_range ON sp_range.strHUC12RNG = NChucs.HUC12RNG
                             WHERE sp_range.intGAPPresence = 1;
    SELECT RecoverGeometryColumn('season', 'geom_4326', 4326, 'POLYGON', 'XY');
    """.format(outDir, gap_id)

    cursorQ.executescript(sql3)

    conn.commit()
    conn.close()
    del cursorQ

    return

# Function to load occurrence records into the summary database
def occurrence_records_to_db(occurrence_db, summary_db, years, months):
    """
    Loads occurrence records into a summary database.

    (str, str, list, list) --> action

    Arguments:
    occurrence_db -- path to the occurrence-records-wrangler database with
                     records to use.
    summary_db -- path to the summary database.
    years --  years to include.  Format as a string version of a list:  "2002,2004,2019"
    months -- months to include.  Format as a string version of a list: "11,12,1,2"
    """
    #################################  Read in occurrence records
    #############################################################
    # Connect to the summary database
    cursor, conn = spatialite(summary_db)

    # Attach occurrence database
    cursor.execute("ATTACH DATABASE ? AS occs;", (occurrence_db,))

    # Create table of occurrences that fit within evaluation parameters
    years = tuple([x.strip() for x in years.split(',')])
    months = tuple([x.strip().zfill(2) for x in months.split(',')])
    cursor.execute("""CREATE TABLE occurrence_records AS
                       SELECT * FROM occs.occurrences
                       WHERE STRFTIME('%Y', OccurrenceDate) IN {0}
                           AND STRFTIME('%m', OccurrenceDate) IN {1};""".format(years, months))

    # Recover geometry
    cursor.execute("""SELECT RecoverGeometryColumn('occurrence_records', 'circle_wgs84',
                      4326, 'POLYGON', 'XY');""")
    #cursor.execute("""SELECT RecoverGeometryColumn('occurrence_records', 'geom_xy4326',
    #                  4326, 'POINT', 'XY');""")
    # Add a geometry in equal area projection
    cursor.executescript("""ALTER TABLE occurrence_records ADD COLUMN circle_5070 BLOB;
                        UPDATE occurrence_records SET circle_5070 = Transform(circle_wgs84, 5070);
                        SELECT RecoverGeometryColumn('occurrence_records', 'circle_5070', 5070,
                                         'POLYGON', 'XY');""")
    conn.commit()
    return

# Function to perform summaries of records within feature polygons
def summarize_by_features(features, summary_id, gap_id, summary_db, outDir, codeDir):
    """ REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE REVISE
    Uses occurrence data collected with the occurrence records wrangler repo
    to summarize occurrence records by feature layers such as counties or hucs.
    Columns are added to feature tables that report summary information
    Columns added:
    record_count -- how many records were attributed to the feature
    knowledge -- did the number of records meet the minimum_count for the species?

    The results of this code are new columns in the feature tables (in the db
    created for work in this repository).

    Unresolved issues:
    1. Can the runtime be improved with spatial indexing?  Minimum bounding rectangle?
    2. Condition data used on the parameters, such as filter_sets in the evaluations
       table.

    Arguments:
    features -- "NChucs", "NCcounties", or "NCblocks"
    summary_id -- name/code of the evaluation
    gap_id -- gap species code.
    summary_db -- path to the evaluation database.  It should have been created with
                make_evaluation_db() so the schema is correct.
    outDir -- directory of
    codeDir -- directory of code repo
    """
    import sqlite3
    import os

    if features == "NChucs":
        IDfield = "HUC12RNG"
        overlapField = "min_overlap_huc12"
    elif features == "NCcounties":
        IDfield = "OBJECTID"
        overlapField = "min_overlap_county"
    elif features == "NCBAblocks":
        IDfield = "BLOCK_QUAD"
        overlapField = "min_overlap_block"

    #cursor, conn = spatialite(codeDir + "/evaluations.sqlite")
    #method = cursor.execute("SELECT method FROM evaluations WHERE evaluation_id = ?;", (summary_id,)).fetchone()[0]
    #conn.close()
    #del cursor

    # Connect to range evaluation database.
    cursor, conn = spatialite(summary_db)

    cursor.execute("""ATTACH DATABASE '{0}/evaluations.sqlite' AS params;""".format(codeDir))
    sql2="""

    /*#########################  How many occurrences per feature?
     #############################################################*/
    /*  Intersect occurrence circles with features  */
    CREATE TABLE green AS
                 SELECT {3}.{4}, ox.occ_id, ox.occurrenceDate, ox.retrievalDate,
                 CastToMultiPolygon(Intersection({3}.geom_4326,
                                                 ox.circle_wgs84)) AS geom_4326
                 FROM {3}, occurrence_records AS ox
                 WHERE Intersects({3}.geom_4326, ox.circle_wgs84);
    SELECT RecoverGeometryColumn('green', 'geom_4326', 4326, 'MULTIPOLYGON', 'XY');

    /* Projected (equal area) geometries have to be created. */
    ALTER TABLE green ADD COLUMN geom_5070 BLOB;
    UPDATE green SET geom_5070 = Transform(geom_4326, 5070);
    SELECT RecoverGeometryColumn('green', 'geom_5070', 5070, 'MULTIPOLYGON', 'XY');

    /* Select records with area greater or equal to the minimum overlap  */
    CREATE TABLE orange AS
      SELECT green.{4}, green.occ_id, green.occurrenceDate, green.retrievalDate,
             100 * (Area(green.geom_5070) / Area(ox.circle_5070)) AS proportion_circle
      FROM green
           LEFT JOIN occurrence_records AS ox
           ON green.occ_id = ox.occ_id
      WHERE proportion_circle >= (SELECT {5}
                                  FROM params.evaluations
                                  WHERE evaluation_id = '{0}'
                                  AND species_id = '{1}');

    /*  How many occurrences in each huc that had an occurrence? */
    ALTER TABLE {3} ADD COLUMN record_count INTEGER;

    UPDATE {3} SET record_count = (SELECT COUNT(occ_id)
                                      FROM orange
                                      WHERE {4} = {3}.{4}
                                      GROUP BY {4});

    /*###################  What is the knowledge status for feature?
     #############################################################*/
    ALTER TABLE {3} ADD COLUMN knowledge INTEGER;

    CREATE TABLE seasonPres AS
                        SELECT St_union(geom_4326) AS geom_4326
                        FROM season;
    /*SELECT RecoverGeometryColumn('seasonPres', 'geom_4326', 4326, 'MULTIPOLYGON', 'XY');*/

    UPDATE {3}
    SET knowledge = 1
    WHERE Intersects({3}.geom_4326, (SELECT geom_4326 FROM seasonPres))
    AND NOT Touches({3}.geom_4326, (SELECT geom_4326 FROM seasonPres));

    UPDATE {3}
    SET knowledge = 2
    WHERE record_count >= (SELECT minimum_count
                           FROM params.evaluations
                           WHERE evaluation_id = '{0}'
                           AND species_id = '{1}');

    /*###################################   Years since last record
    #############################################################*/
    ALTER TABLE {3} ADD COLUMN years_since_record INTEGER;

    CREATE VIEW purple AS
                        SELECT {4}, retrievalDate - occurrenceDate AS age
                        FROM orange
                        GROUP BY {4}
                        HAVING MIN(age);

    UPDATE {3}
    SET years_since_record = (SELECT purple.age
                              FROM purple
                              WHERE purple.{4} = {3}.{4});

    /*######################## Find features to target for sampling
    #############################################################
    Targets are features touching a feature having sufficient count or
    with fewer than the minimum count.  Code uses 'BETWEEN' which is inclusive,
    so you have to get select for values between 0 and min_count - 1.

    A couple intermediate tables with dissolved geometries have to be
    created for applying spatial conditions (near documented or overlaping
    initial gap range)*/
    CREATE TABLE documented AS
                        SELECT St_union(geom_4326) AS geom_4326
                        FROM {3}
                        WHERE knowledge = 2;
    SELECT RecoverGeometryColumn('documented', 'geom_4326', 4326, 'MULTIPOLYGON', 'XY');

    ALTER TABLE {3} ADD COLUMN target INTEGER;

    UPDATE {3}
    SET target = 1
    WHERE Touches(geom_4326, (SELECT geom_4326 FROM documented))
    OR record_count BETWEEN 0 AND ((SELECT minimum_count
                                    FROM params.evaluations
                                    WHERE evaluation_id = '{0}'
                                    AND species_id = '{1}') - 1);

    UPDATE {3}
    SET target = 1
    WHERE Intersects({3}.geom_4326, (SELECT geom_4326 FROM seasonPres))
    AND NOT Touches({3}.geom_4326, (SELECT geom_4326 FROM seasonPres));

    UPDATE {3}
    SET target = Null
    WHERE knowledge = 2;

    DROP VIEW purple;
    DROP TABLE documented;
    DROP TABLE seasonPres;
    DROP TABLE green;
    DROP TABLE orange;
    """.format(summary_id, gap_id, outDir, features, IDfield, overlapField)

    try:
        cursor.executescript(sql2)
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()
    return
