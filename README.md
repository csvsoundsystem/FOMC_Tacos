FOMC_Tacos
==========

A csv soundsystem data gastronomification experiment

The Federal Open Market Committee (FOMC) sets interest rates for the entire economy.

Their statements announcing  interest rate policy is the single most important and highly-anticipated and written-about event each time it happens. Everyone writes about it on page A1 of the newspaper:

http://www.nytimes.com/2014/01/09/business/fed-decided-bond-buying-program-served-purpose-account-says.html?_r=0

Unfortunately, it is written in economic argot that is hard for orginary people to understand, except for reporters and analysts who divine these important statements’ meaning for the lay reader.

Our objective: visualize the FOMC statements by turning them into food - a data gastronomification experiment.

## <a id="sourcedata">Source Data</a>

The scraper downloads all monetary press releases from the Federal Reserve's website, available here:
<http://www.federalreserve.gov/newsevents/press/monetary/2014monetary.htm>

Previous years are available by changing the year in the URL, going back to 1996. The scraper goes back to 1996

## <a id="sourcedata">Running the Scraper</a>

To run the scraper, execute the fomc_all.py python script in the scraper directory.

The scraper will download the press releases into a new directory called frb_releaes.

## <a id="sourcedata">What's in the Data</a>

The data contains all press release content from 1996 onwards, as follows:

| Field	| Datatype | Definition | 
| :------ |:--------| :-------------------------------------------------------------- |
| date | datetime	| The date of the press release | 
| is_fomc | integer	| Indicates whether press release is an FOMC statement: 1 means yes, 0 means no | 
| title | text	| The title of the press release | 
| text | text	| The text of the press release | 
| source_url | text	| The URL for the source of the data | 

## <a id="sourcedata">What are FOMC Statements?</a>

The Federal Open market Committee (FOMC) meets about six times a year to decide interest rates and - more recently - the fate of bond purchase programs. 

The statement outlining their decision is called the FOMC statement. It is the single most important and market-moving statement published by the Fed.




