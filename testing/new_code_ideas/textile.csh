#!/bin/csh
#This script generates a latex document script for putting figures side by side, and requires:
#   1) full texlive installation (e.g. sudo yum install texlive*, or, brew cask install texlive-full)
#   2) 'imgaemagick': MAC/Linux package required for running the 'identify' command,
#Coded by Omid Bagherpur
#Update: 5 June 2020 
#===Adjustable Parameters===#
set output = textile
set paperWidth = 1000 #in pixel (might change a bit after processing)
set padding = 5 #padding between figures in pixel
set ncol = $1
#===========================#
#--Remove tmp files if existed--#
touch {dim,Grd,H,ID,index,W,whGrd,Width,WH,rowID,sumWH,tbx,textWidth}.tmp
rm -f {dim,Grd,H,ID,index,W,whGrd,Width,WH,rowID,sumWH,tbx,textWidth}.tmp
touch $output.tex a0header.ps
rm -f $output.tex a0header.ps
#-------------------------------#
clear
printf "'textile' is a LATEX document generator that generates a LATEX script in which a list of figures are put together as tiles when compiled.\n\n"
if ($#argv < 2) then
  printf "  USAGE:  textile <#columns> file1 file2 file3 ...\n\n"
  exit
endif
set nof = `echo $#argv|awk '{print $1-1}'`

printf '  Generating LATEX document ... \r'
#correction scale factor
set factor = `echo $ncol $padding $paperWidth|awk '{printf "%.4f",1-($1*$2/$3)}'`


@ c=1
set dim = ()
while ($c < $#argv)
  @ c++
  set dim = ($dim `identify -format "%wx%h" $argv[$c]`)
end

if ($nof < $ncol) set ncol = $nof
#--find nrow--
set temp1 = `echo "scale=0;$nof / $ncol"|bc`
set temp2 = `echo "scale=1;$nof / $ncol"|bc`
if (`echo "$temp2 > $temp1"|bc` == 1 ) then
  set nrow = `echo "$temp1+1"|bc`
else 
  set nrow = $temp1
endif

@ i = 1
while ($i <= $nrow)
  echo $i >> rowID.tmp
  @ i++
end

#-------------
#Make whGrd.tmp
@ i = 1
while ($i <= $nof)

  set row = `echo "$i $ncol"|awk '{printf "%.2f",($1/$2)+1}'|awk -F"." '{print $1}'`
  if (`echo $i $ncol|awk '{printf "%.2f",$1/$2}'|awk -F"." '{print $2}'` == '00') @ row--
  set col = `echo "$i $row $ncol"|awk '{printf "%d",$1-($2-1)*$3}'`
  set width  = `echo $dim[$i]|awk -F"x" '{print $1}'`  
  set height = `echo $dim[$i]|awk -F"x" '{print $2}'`
  echo $width >> W.tmp
  echo $height >> H.tmp
  set WH = `echo $width $height|awk '{printf "%.4f",$1/$2}'`
  echo $WH >> WH.tmp
  if ($col < $ncol) then
  	printf "%.4f " $WH >> whGrd.tmp
  else
  	printf "%.4f\n" $WH >> whGrd.tmp
  endif
  
  @ i++
end

#-------------
#Measure paperheight
@ i = 1
while ($i <= $nrow)
  set temp = `awk "NR==$i" whGrd.tmp`
  set sum  = `printf "%.4f\n" $temp|awk '{s+= $1} END {printf "%.4f\n",s}'`
  echo $sum >> sumWH.tmp
  @ i++
end

set max  = `sort -nr sumWH.tmp|awk 'NR==1'`
set unit = `echo $paperWidth $max| awk '{printf "%.0f",$1/$2}'`

set paperWidth = `echo $paperWidth $ncol $padding|awk '{printf "%.0f",($2+1.5)*$3+$1}'`
set paperHeight = `echo $unit $nrow $padding|awk '{printf "%.0f",($1*$2)+$3*$2}'`

#make index.tmp
@ i=1
while ($i <= $nrow)
  @ j=1
  while ($j <= $ncol)
    set index = `echo "($i-1)*$ncol+$j"|bc`
    if ($index <= $nof) then
      echo $i $j >> index.tmp
    endif
    @ j++
  end
  @ i++
end


#================#
#Making Latex doc
#================#

printf "c" >> tbx.tmp
@ j=2
while ($j <= $ncol)
  printf " c" >> tbx.tmp
  @ j++
end
printf "\n" >> tbx.tmp

set pt='pt'
cat << END > $output.tex
\documentclass{a0poster}
\usepackage{graphicx,tabularx}
\usepackage[margin= 0pt, tmargin= $padding$pt]{geometry}
END
printf "\\paperheight = %.0fpt\n" $paperHeight >> $output.tex
printf "\\paperwidth = %.0fpt\n" $paperWidth >> $output.tex

cat << END >> $output.tex
\textwidth = \paperwidth
\textheight = 1.5\paperheight
\setlength{\parindent}{0pt}

\begin{document}
\pagenumbering{gobble}
\centering
END

set pt='pt'

cat << END >> $output.tex
\setlength{\tabcolsep}{$padding$pt}
\renewcommand{\arraystretch}{0}
\begin{tabularx}{\textwidth}{`cat tbx.tmp`}
END

@ i=1
while ($i <= $nrow)
  @ j=1
  while ($j <= $ncol)
    set index = `echo "($i-1)*$ncol+$j"|bc`

    if ($index <= $nof) then
      set fn = `echo $index+1|bc`
      set photo = $argv[$fn]
      set size = `echo "$unit*$factor"|bc`

      if ($j == $ncol) then
        printf "\\includegraphics[height=%.0fpt]{%s} \\vspace*{%spt} %s\n" $size $photo $padding '\\' >> $output.tex
      else
        #echo $unit $factor $photo|awk '{printf "\\includegraphics[height=%.0fpt]{%s}  \n",$1*$2,$3}' >> $output.tex
        printf "\\includegraphics[height=%.0fpt]{%s} %s \n" $size $photo '&'>> $output.tex
        
      endif

    endif
    @ j++
  end
  @ i++
end

#add '~'
set temp = `awk "NR==$nof" index.tmp|awk '{print $2}'`
while ($temp < $ncol)
  if (`echo "$temp+1 < $ncol"|bc` == 1) then
    printf "~&" >> $output.tex
  else
    printf "%s\n" ' \\' >> $output.tex
  endif
  @ temp++
end


echo '\\end{tabularx}' >>  $output.tex
echo '\\end{document}' >>  $output.tex


printf '  Generating LATEX document ... Done!\n'

rm -f {dim,Grd,H,ID,index,W,whGrd,Width,WH,rowID,sumWH,tbx,textWidth}.tmp

printf '  Compiling LATEX document ... \r'
pdflatex $output.tex > $output.log
rm -f a0header.ps $output.{aux,log}
printf '  Compiling LATEX document .... Done!\n\n'

rm -f $output.tex

