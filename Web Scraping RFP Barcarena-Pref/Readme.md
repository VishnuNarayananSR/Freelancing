# Readme

## Installation

```bash
pip install -r requirements.txt 
```

## Usage
```bash
python Scrape.py "<name>" "<url>" [--dir "ouput folder name"] [--con no.of concurrent connections]
```

## Example

```bash
python Scrape.py "consultarliqdesporc" "http://www.governotransparente.com.br/transparencia\
/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem\
=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false"
```

### The default output  directory is "Output" if you wish to give a custom name to output directory try this:

```bash
python Scrape.py "consultarliqdesporc" "http://www.governotransparente.com.br/transparencia\
/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem\
=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false" --dir "My folder"
```

### If you wish to send concurrent requests to make things faster try this:

```bash
python Scrape.py "consultarliqdesporc" "http://www.governotransparente.com.br/transparencia\
/4382489/consultarliqdesporc/resultado?ano=8&inicio=01%2F01%2F2021&fim=24%2F01%2F2021&orgao=-1&elem\
=-1&unid=-1&valormax=&valormin=&credor=-1&clean=false" --dir "My folder" --con 100
```

#### NB: By default Cloud Run container instances can receive many requests at the same time (up to a maximum of 250)
