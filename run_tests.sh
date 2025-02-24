#!/bin/bash

if [ $# -eq 0 ]
    then
        echo "No test name supplied, running full set of tests"
        python -m pytest --cov=./ --cov-report=html --html=test-reports/full_test_run.html
    else

        directory=""
        case "$1" in
            int) directory="tests/integration/test_integration_using-explicit-test-cases.py";;
            def) directory="tests/integration/test_integration_using-default-parameters.py";;
            unit) directory="tests/unit/test_functions.py";;
            *) echo "Unknown test set: $1";;
        esac

        if [ ! -z "$directory" ]
        then
            echo "Running $directory test(s)";
            shift
            echo "- ${#@} specific tests requested"
            if [ ${#@} -gt 0 ]
            then
                echo "  ${@}"
            else
                echo "  Running all tests in file"
            fi

            for I in $@
            do
                OUT=${OUT:+$OUT }$directory::$I
            done

            if [ -z "$OUT" ]
            then
                OUT=$directory
            fi

            echo "[$OUT]"

            pytest $OUT --html=test-reports/specific_test.html
        fi
fi

