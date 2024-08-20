#!/usr/bin/python

import sqlite3
import os
from collections import OrderedDict

import sys
sys.path.append("/media/michael/SSD3/Dropbox/workspace/2.research/_bin")
import ontologize.modules.util.confdat as confdat

DB_dir = confdat.academia_root + "_rdb"
DB_path = DB_dir + "/02_RDB/db.sqlite"
db = sqlite3.connect( DB_path )

import ontologize.modules.data_transformation.normalise
import ontologize.modules.data_transformation.mkd as mkd


import sys,zipfile,re,os,csv
from pyquery import PyQuery as pq
from lxml.cssselect import CSSSelector
from string import punctuation


def requires_refresh( filename, writepath, tbl_name, is_override=False ):
    if is_override:
        return True

    writepath = "%s.%s.tsv" % ( writepath, tbl_name )
    if os.path.exists( writepath ):
        if os.path.getmtime( writepath ) > os.path.getmtime( filename ):
            #print "***NO NEED TO UPDATE***"
            return False

    return True


def is_MKD( filepath ):
    root, fname = filepath.rsplit( "/", 1 )
    return (fname.endswith(".mkd") or fname.endswith(".txt")) and ( "02_" in root ) and not ( "^" in fname )


def is_tagged_ODS( filepath ):
    root, fname = filepath.rsplit( "/", 1 )
    return fname.endswith(".ods") and ( "02_" in root ) and not ( "[...]" in fname ) and not ( "#" in fname ) #and "Population" in fname


def is_tagged_TSV( filepath ):
    root, fname = filepath.rsplit( "/", 1 )
    return fname.endswith(".tsv") and ( "_TSV" in root ) and not ( "[...]" in fname ) and not ( "#" in fname )


def ods2csv(filepath):
    root, filename = filepath.rsplit( "/", 1 )
    writepath = root + "/^" + filename + ".csv"

    cmd = "libreoffice --headless --convert-to csv --outdir \"{root}\" \"{filepath}\"".format( root=root, filepath=filepath )
    os.system( cmd )

    cmd = "mv \"%s\" \"%s\"" % ( filepath.replace("ods", "csv"), writepath )
    os.system( cmd )

    '''
    xml = zipfile.ZipFile(filepath).read('content.xml')

    def rep_repl(match):
        return '<table:table-cell>%s' %match.group(2) * int(match.group(1))
    def repl_empt(match):
        n = int(match.group(1))
        pat = '<table:table-cell/>'
        return pat*n if (n<100) else pat

    p_repl = re.compile(r'<table:table-cell [^>]*?repeated="(\d+)[^/>]*>(.+?table-cell>)')
    p_empt = re.compile(r'<table:table-cell [^>]*?repeated="(\d+)[^>]*>')
    xml = re.sub(p_repl, rep_repl, xml)
    xml = re.sub(p_empt, repl_empt, xml)

    d = pq(xml, parser='xml')
    ns={'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'}
    selr = CSSSelector('table|table-row', namespaces=ns)
    selc = CSSSelector('table|table-cell', namespaces=ns)
    rowxs = pq(selr(d[0]))
    data = []
    for ir,rowx in enumerate(rowxs):
        cells = pq(selc(rowx))
        if cells.text():
            data.append([cells.eq(ic).text().encode('utf-8') for ic in range(len(cells))])

    path, filename = filepath.rsplit( "/", 1 )
    writepath = path + "/^" + filename + ".csv"

    with open(writepath, 'wb') as f:
        for row in data:
            dw = csv.writer(f)
            dw.writerow(row)
    '''


def insert_caret( path ):
    return ( "%s/^%s" % ( path.rsplit( "/", 1 )[0], path.rsplit( "/", 1 )[1] ) ).replace( "^^", "^" )


def get_RDB_table_as_dict( tablename ):
    cursor = db.cursor()
    sql = "SELECT * FROM %s LIMIT 1" % tablename
    try:
        rows = cursor.execute( sql )
    except sqlite3.OperationalError:
        return None
    desc = cursor.description
    column_names = [col[0] for col in desc]
    data = OrderedDict()
    for col in column_names:
        data[col] = ""
    return data


def get_short_filepath( filepath ):
    shorty = ""
    filepath = filepath.replace( "/media/michael/SSD3/Dropbox/workspace/2.research", "" )
    for x in filepath.split("/"):
        if "," in x:
            shorty += x.split(",",1)[0]
        elif "." in x:
            shorty += x.split(".",1)[0]
        else:
            shorty += x
        shorty += "."
    return shorty.strip(punctuation)


def get_ref_from_filepath( filepath, page_num="" ):

    basepath = "/media/michael/SSD3/Dropbox/workspace/2.research/01.Material/"
    filepath = filepath.replace( basepath, "" )
    filepath = filepath.replace( "../", "" )
    filepath = filepath.replace( "1.Material/", "" )
    dirs = filepath.split( "/" )

    ref = ""
    ref_type = ""
    first_d = dirs[0]
    second_d = dirs[1]

    # ...

    if "Manuscripts" in first_d:
        ref_type = "manu"
        ref = "Manu."

        if "Publ" in second_d:
            ref_type = "publ"
            ref = "Publ."

    if "Publications" in first_d:
        ref_type = "publ"
        ref = "Publ."

        if "Newspapers" in second_d:
            ref_type = "news"
            ref = "News."

        if "Periodicals" in second_d:
            ref_type = "news"
            ref = "Periodical."

    if "WWW" in first_d:
        ref_type = "www"
        ref = "WWW."

    if "Visual" in first_d:
        ref_type = "maps"
        ref = "Visual."

    if "Datasets" in first_d:
        ref_type = "datasets"
        ref = "Datasets."

    if "Personal" in first_d:
        ref_type = "persnnal"
        ref = "Personal."

    if "Tertiary" in first_d:
        ref_type = "tertiary"
        ref = "Tertiary."

    if "Maps" in first_d:
        ref_type = "maps"
        ref = "Maps."

    # ...

    if ref_type == "manu" or ref_type == "maps":
        for d in dirs[1:]:
            #print d
            if not d.startswith(( "1", "2", "3", "4", "5", "6", "7", "8", "9", "0" )) and d.endswith(".txt"):
                continue

            if d.startswith(( "01_", "02_", "03_", "00.", "00.", "01.", "02.", "03.", "04.", "a, ", "A, ", "(" )):
                continue

            if d.isdigit() and len( d ) == 8: # ??
                continue

            if d.endswith( ".ods" ) or d.endswith( ".tsv" ):
                ref += "|%s" % d
            else:
                if "," in d:
                    ref += d.split(",")[0] + "."
                else:
                    ref += d + "."

    if ref_type == "news" or ref_type == "datasets":
        for d in dirs[1:-1]:
            #print d
            if d.startswith(( "01_", "02_", "03_", "00.", "00.", "01." )): #, "a, ", "A, "
                continue

            if "," in d:
                ref += d.split(",")[0] + "."
            else:
                ref += d + "."

    if ref_type == "www":
        for d in dirs[1:-1]:
            #print d
            if d.startswith(( "01_", "02_", "03_", "00.", "00.", "01.", "a, ", "A, " )):
                continue

            if "," in d:
                ref += d.split(",")[0] + "."
            else:
                ref += d + "."

    path = basepath
    if ref_type == "publ":
        for d in dirs:
            path = path + "/" + d
            citepath = path + "/cite.bib"
            if os.path.exists( citepath ):
                with open( citepath, "r" ) as r:
                    shorttitle = author = year = publisher = ""
                    for line in r.readlines():
                        if "shorttitle = " in line:
                            shorttitle = line.replace( "shorttitle = ", "" ).replace( "{", "" ).replace( "}", "" ).strip()
                        if "author = " in line:
                            author = line.replace( "author = ", "" ).replace( "{", "" ).replace( "}", "" ).strip()
                            if ", " in author:
                                author = author.split( ", " )[0]
                        if "year = " in line:
                            year = line.replace( "year = ", "" ).replace( "{", "" ).replace( "}", "" ).strip()
                        if "publisher = " in line:
                            publisher = line.replace( "publisher = ", "" ).replace( "{", "" ).replace( "}", "" ).strip()
                    ref += "%s, %s" % ( author, year ) #, shorttitle, publisher ) #%s (%s)
                    if shorttitle:
                        ref += " (%s)" % shorttitle
                    if page_num:
                        ref += ", p.%s" % page_num

    return ref.rstrip(".")
