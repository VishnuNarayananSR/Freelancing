
declare -a StringArray=("http://www.governotransparente.com.br/transparencia/4382489/consultarempenho/resultado?ano=7&inicio=01%2F01%2F2020&fim=25%2F01%2F2020&unid=-1&valormax=&valormin=&credor=-1&clean=false"
 "http://www.governotransparente.com.br/transparencia/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false"
 "http://www.governotransparente.com.br/transparencia/4382489/consultarliqrestpag/resultado?ano=7&inicio=01%2F01%2F2020&fim=25%2F01%2F2020&unid=-1&valormax=&valormin=&credor=-1&clean=false" 
 "http://www.governotransparente.com.br/transparencia/4382489/consultarpagdesporc/resultado?ano=7&inicio=01%2F01%2F2020&fim=25%2F01%2F2020&unid=-1&orgao=-1&elem=-1&valormax=&valormin=&credor=-1&clean=false" 
 "http://www.governotransparente.com.br/transparencia/4382489/consultarpagrestpag/resultado?ano=7&inicio=01%2F01%2F2020&fim=25%2F01%2F2020&unid=-1&valormax=&valormin=&credor=-1&clean=false" 
 )
k=0
p="Scrape.py"
for link in ${StringArray[@]}; do
   eval "python" ${p} ${k} \'${link}\' "--dir" ${k}
   k=`expr $k + 1`
done
