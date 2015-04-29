
DIR_CARPETA=`pwd`
OUTPUT_DIR=dPET_simulated


mkdir $OUTPUT_DIR

while read LINE;
	do

   	 frame=$(echo $LINE | cut -d ',' -f 1)
   	 duracion=$(echo $LINE | cut -d ',' -f 2)	

    echo frame $frame trues $trues

INPUT_DIR=OutputN$frame	
FILE_NAME=Frame$frame.v
FILE_NAME_hv=Frame$frame.hv

cd $INPUT_DIR
cp $FILE_NAME ../$OUTPUT_DIR/$FILE_NAME
cp $FILE_NAME_hv ../$OUTPUT_DIR/$FILE_NAME_hv

cd ../

done  < "TrueCounts_list";
