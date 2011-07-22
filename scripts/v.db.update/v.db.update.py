#!/usr/bin/env python
#
############################################################################
#
# MODULE:       v.db.update
# AUTHOR(S):    Moritz Lennert
#               Extensions by Markus Neteler
#               Converted to Python by Glynn Clements
# PURPOSE:      Interface to db.execute to update a column in the attribute table connected to a given map
# COPYRIGHT:    (C) 2005,2007-2008,2011 by the GRASS Development Team
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################

#%Module
#%  description: Allows to update a column in the attribute table connected to a vector map.
#%  keywords: vector
#%  keywords: database
#%  keywords: attribute table
#%End
#%option
#% key: map
#% type: string
#% gisprompt: old,vector,vector
#% description: Name of vector map
#% required : yes
#% key_desc: name
#%end
#%option
#% key: layer
#% type: string
#% gisprompt: old_layer,layer,layer
#% label: Layer number or name
#% description: A single vector map can be connected to multiple database tables. This number determines which table to use. Layer name for direct OGR access. 
#% answer: 1
#% required : no
#% key_desc: name
#%end
#%option
#% key: column
#% type: string
#% gisprompt: old_dbcolumn,dbcolumn,dbcolumn
#% description: Name of column to update
#% required : yes
#% key_desc: name
#%end
#%option
#% key: value
#% type: string
#% description: Value to update the column with, can be (combination of) other column(s)
#% required : no
#%end
#%option
#% key: qcolumn
#% type: string
#% gisprompt: old_dbcolumn,dbcolumn,dbcolumn
#% description: Name of column to query
#% required : no
#% key_desc: name
#%end
#%option
#% key: where
#% type: string
#% label: WHERE conditions of SQL statement without 'where' keyword
#% description: Example: income < 1000 and inhab >= 10000
#% required : no
#%end

import sys
import os
import grass.script as grass

def main():
    vector = options['map']
    layer = options['layer']
    column = options['column']
    value = options['value']
    qcolumn = options['qcolumn']
    where = options['where']

    mapset = grass.gisenv()['MAPSET']

    # does map exist in CURRENT mapset?
    if not grass.find_file(vector, element = 'vector', mapset = mapset)['file']:
	grass.fatal(_("Vector map <%s> not found in current mapset") % vector)

    try:
        f = grass.vector_db(vector)[int(layer)]
    except KeyError:
	grass.fatal(_('There is no table connected to this map. Run v.db.connect or v.db.addtable first.'))

    table = f['table']
    database = f['database']
    driver = f['driver']

    # checking column types
    try:
        coltype = grass.vector_columns(vector, layer)[column]['type']
    except KeyError:
	grass.fatal(_('Column <%s> not found') % column)

    if qcolumn:
	if value:
	    grass.fatal(_('<value> and <qcolumn> are mutually exclusive'))
	# special case: we copy from another column
	value = qcolumn
    else:
	if not value:
	    grass.fatal(_('Either <value> or <qcolumn> must be given'))
	# we insert a value
	if coltype.upper() not in ["INTEGER", "DOUBLE PRECISION"]:
	    value = "'%s'" % value

    cmd = "UPDATE %s SET %s=%s" % (table, column, value)
    if where:
	cmd += " WHERE " + where

    grass.verbose("SQL: \"%s\"" % cmd)

    grass.write_command('db.execute', input = '-', database = database, driver = driver, stdin = cmd)

    # write cmd history:
    grass.vector_history(vector)

    return 0

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
