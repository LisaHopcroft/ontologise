
def get_siblings( g, target ):
	# target = "RANKINE, Jean (33)"
	siblings = []
	for parent in g.predecessors(target):
		print ( "PARENT of %s : %s" % ( target, parent  ) )
		for p, sibling in g.out_edges(parent):
			print( " +-- possible sibling : %s" % sibling )
			if sibling != target: siblings.append( sibling )
	siblings = set(siblings)
	print ( "%s has %d siblings" % (target, len(siblings)) )
	for s in siblings: print( " + %s" % s )
	return siblings

def get_parents( g, target ):
	# target = "RANKINE, Jean (33)"
	parents = []
	for p in g.predecessors(target):
		parents.append( p )
	parents = set(parents)
	print ( "%s has %d parents" % (target, len(parents)) )
	for p in parents: print( " + %s" % p )
	return parents
