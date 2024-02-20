#!/bin/sh

for c1 in "DOC_1" "DOC_2" "DOC_3" "DOC_4" "DOC_5" "DOC_6" "DOC_7" "DOC_8" "DOC_9" "DOC_10" "DOC_11" "DOC_12" "DOC_13" "DOC_14" "DOC_15" "DOC_16" "DOC_17" "DOC_18" "DOC_19" "DOC_20" "DOC_21" "DOC_22" "DOC_23" "DOC_24" "DOC_25" "DOC_26" "DOC_27" "DOC_28" "DOC_29" "DOC_30" "DOC_31" "DOC_32" "DOC_33" "DOC_34" "DOC_35" "DOC_36" "DOC_R1" "DOC_R2" "DOC_37" "DOC_38" "DOC_39" "DOC_44" "documente_1"
do

    for c2 in "DOC_1" "DOC_2" "DOC_3" "DOC_4" "DOC_5" "DOC_6" "DOC_7" "DOC_8" "DOC_9" "DOC_10" "DOC_11" "DOC_12" "DOC_13" "DOC_14" "DOC_15" "DOC_16" "DOC_17" "DOC_18" "DOC_19" "DOC_20" "DOC_21" "DOC_22" "DOC_23" "DOC_24" "DOC_25" "DOC_26" "DOC_27" "DOC_28" "DOC_29" "DOC_30" "DOC_31" "DOC_32" "DOC_33" "DOC_34" "DOC_35" "DOC_36" "DOC_R1" "DOC_R2" "DOC_37" "DOC_38" "DOC_39" "DOC_44" "documente_1"
    do

	if [ "$c1" != "$c2" ]; then 
	    python3 iaa.py --corpus1 ./corpora/$c1 --corpus2 ./corpora/$c2
	fi

    done

done


