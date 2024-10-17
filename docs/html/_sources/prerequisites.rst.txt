=====================================================================
Prerequisites
=====================================================================

Documents must be marked up in the standard format.

----------------------------------------------------------------------
Definitions
----------------------------------------------------------------------

There are a few concepts that will be used when describing what this format is:

.. mermaid::
    :name: concept_map
    
    flowchart LR
        subgraph d1 [Document]
            subgraph sN [Source N]
                A@{ shape: doc, label: "__Header (req)__
                Shortcuts (opt)
                Peopla (opt)
                DataTable (opt)
                DataPoints (opt)
                "}
            end
            subgraph sep[...]
                C:::hidden
            end
            style sep fill:none,stroke:none
            subgraph s1 [Source 1]
                B@{ shape: doc, label: "__Header (req)__
                Shortcuts (opt)
                Peopla (opt)
                DataTable (opt)
                DataPoints (opt)
                " }
            end
        end

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



See a minimal example below:

.. #[RECORD_TYPE]
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
