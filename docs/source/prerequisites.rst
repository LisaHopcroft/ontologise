=====================================================================
Prerequisites
=====================================================================

Documents must be marked up in the standard format.

----------------------------------------------------------------------
Definitions
----------------------------------------------------------------------

There are a few concepts that will be used when describing what this format is:

Document
    A single plain text file that contains Ontologise content.
    This can contain more than one source.

Source
    A portion of text that was obtained from a single source.

Header
    A portion of markup, conforming to a specific format, that
    describes the _Source_.

Peopla
    A portion of markup, conforming to a specific format, that
    captures information about a person or a place.
    A _Peopla_ object will have a name and any number of attributes,
    which can be explicity applied or inherited using _Shortcut_
    markers.

Datatable
    A portion of markup, conforming to a specific format, that
    captures tabular information. A datatable will have any number
    of explicit columns, plus any number of _Shortcut_ columns. To
    apply a shortcut to a Datatable, the appropriate marker should
    be included in the Datatable header.

Datapoint
    A single line of tab separated text that represents a single datapoint
    in a _Datatable_. Data will only be parsed for the number of columns
    defined by the _Datatable_.

Shortcut
    Shortcuts are markers that allow transfer of information between
    objects. Currently, there are two kinds of shortcut:
    
    - *inheritance markers* allow objects to inherit the attributes of the _Document_
    - *autogeneration markers* allow objects to inherit other, pre-defined attributes

    Inheritance markers are defined in the _Header_ of a _Document_.
    Autogeneration markers are defined in a settings file (see below).


----------------------------------------------------------------------
Example
----------------------------------------------------------------------

See a minimal example below:

.. code-block:: md

    #[RECORD_TYPE]
    ##AT:	PLACE
    ##ATX:	1800_TEXT_TEXT:00
    ##DATE:	1800-01-01

    ----------------------------------------------------------------------
    ###	^1:
    ###		ENSLAVED*
    ###		!MALE
    ###	^2:
    ###		ENSLAVED*
    ###		!FEMALE
    ###	^3:
    ###		!BLUE
    ----------------------------------------------------------------------

    ###	[M'TURK, Michael]
    ###		PROPRIETOR

    ### @SOMEWHERE
    ###     DESTINATION

    ###\tX\tY\tZ^1^3
    L1
    M1	M2	M3
    N1	N2	N3	N4
    [/]
    ###\tEND

----------------------------------------------------------------------
Markdown formats
----------------------------------------------------------------------

See below for explanation of markdown formats:

*Basic case*

.. code-block::

    ###	[PERS_ID]
    ###		AT
    ###			@[at]


*Together*

.. code-block::

    ###	[PERS_ID]
    ###	w/[PERS_ID]
    ###		MARRIED
    ###			:[val]


*Relations*

.. code-block::

    ###	[PERS_ID]
    ###	w/[PERS_ID]
    ###		MARRIED
    ###			:[val]
    ###	>	*REL*
    ###	>	[PERS_ID]


*Adjunct info*

.. code-block::

    ###	[PERS_ID]
    ###	w/[PERS_ID]
    ###	(	OF
    ###	(		@[val]
    ###		MARRIED
    ###			:[val]


See below for further information about elements used in Ontologise.

.. list-table:: 
   :widths: 25 50
   :header-rows: 1

   * - Context parameters
     - Meaning
   * - ##DATE:	val
     - date (val is of format YYYY-MM-DD)
   * - ##AT:	val
     - place
   * - @00:00
     - time

.. list-table:: 
   :widths: 25 50
   :header-rows: 1

   * - Tag symbol
     - Meaning
   * - @
     - place
   * - :
     - date
   * - \<
     - before
   * - \>
     - after


.. list-table:: 
   :widths: 25 50
   :header-rows: 1

   * - Trailing modifier
     - Meaning
   * - \*
     - use context parameters as defaults
   * - ~
     - possibly

.. list-table:: 
   :widths: 25 50
   :header-rows: 1

   * - Identifiers
     - Meaning
   * - \(n\) 
     - file level identifer
   * - {n} 
     - global identifier


.. list-table:: 
   :widths: 25 50
   :header-rows: 1

   * - Grouping markup
     - Meaning
   * - w/
     - together
   * - vs 
     - actors/reactors (not yet implemented)




