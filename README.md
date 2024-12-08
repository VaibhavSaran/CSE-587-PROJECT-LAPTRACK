# LAPTRACK
A major project for the course work at SUNY Buffalo, CSE 587 Data Intensive Computing(Fall 2024) under the guidance of Professor Chen Xu.

## Authors
|Team Member|UB ID|Github|LinkedIN|E-Mail|
|----------------|--------|-----------------------|-------------------|----------|
|Shaurya Mathur|50611201|[ShauryaMathur](https://github.com/ShauryaMathur)            |[shauryamathur27](https://www.linkedin.com/in/shauryamathur27/)            |[smathur4@buffalo.edu](mailto:smathur4@buffalo.edu)|
|Vaibhav Saran|50615031|[VaibhavSaran](https://github.com/VaibhavSaran)|[vaibhav-saran](https://www.linkedin.com/in/vaibhav-saran/)|vsaran@buffalo.edu|
|Yeswanth Chitturi|50591666|[s1th883](https://github.com/s1th883)|[yeswanth-chitturi](https://www.linkedin.com/in/yeswanth-chitturi/)|[ychittur@buffalo.edu](mailto:ychittur@buffalo.edu)|

## Overview
In this project we have tried to build a web app where a user can search for laptops across multiple stores for comparing prices in one place and can get recommendations for similar laptops. In order to do so the project was executed in 3 phases as follows:
- **Phase 1: Data Collection and Analysis**
	 > Here the data was collected by scraping the public websites, namely: amazon.com, flipkart.com and bestbuy.com.
	 
	 > In order to scrape the data **BeautifulSoup** and **Selenium** was used to get the data and is stored in **sqlite database**.

	> The final data has over **4000 products** across the different stores and was analyzed to uncover hidden trends and patterns
- **Phase 2: Model Building**
	> In this part multiple ML models were built based on hypothesis built from Phase 1 data analysis.
	
	> ML models were built to analyze and validate hypothesis and uncover the patterns in the data.
	
	>  A total of **12 Regression models** were built and the **best 3 models** were selected for **hyperparameter tuning**. 

- **Phase 3: Deployment and Web App**
	> In this part a web app is built using **flask** as backend and **ReactJS** as the front end. For the **ETL pipeline**, using the **pySpark framework** the data is stored in **PostgreSQL**.
	
	> A **recommendation system** is built using  **cosine similarity** along with a **price predictor** using **ML models**. The predictor is presented as an **price estimator** for a given specs of a laptop.

## Setup and Executing Project
<br/>
<b>Step 1.</b> Download Docker Desktop: <a href = "https://docs.docker.com/desktop/setup/install/windows-install/">Docker Desktop</a>.
<br/>

> The link contains the steps to install docker on mac, linux and Windows.

<br/>
<b>Step 2.</b> Start Docker Desktop and navigate to the `Phase3/root/app/laptrack` in the docker terminal and run the following command 
<pre>
docker-compose up --build
</pre> 
<br/>
<b>Step 3.</b> It should now directly open up the local hosted application at port 3000. In case it doesn't open up, go to your browser and put the following in the URL bar
<pre>
localhost:3000/
</pre>
<br/>
<b>Step 4.</b> You can use the following sample login credentials to explore the app:
<pre>
user@example.com
user123
</pre>

## Directory Structure

```
📦 
├─ .DS_Store
├─ .gitignore
├─ LICENSE.md
├─ Phase1
│  ├─ Project Laptrack - Phase 1 Data Collection and Cleaning.ipynb
│  ├─ Project Laptrack - Phase 1 Data Collection and Cleaning.pdf
│  ├─ Project Laptrack - Phase 1 Exploratory Data Analysis.ipynb
│  ├─ Project Laptrack - Phase 1 Exploratory Data Analysis.pdf
│  ├─ dataCollection
│  │  ├─ .DS_Store
│  │  ├─ amazon
│  │  │  ├─ .DS_Store
│  │  │  ├─ amazon data
│  │  │  │  ├─ Amazon Data Cleaning.ipynb
│  │  │  │  ├─ Amazon Product Data Collection.ipynb
│  │  │  │  ├─ Amazon URL Scraping.ipynb
│  │  │  │  ├─ consolidated_amazon_laptop_data.csv
│  │  │  │  ├─ final_laptop_data.csv
│  │  │  │  ├─ final_laptop_data_unprocessed_3.csv
│  │  │  │  ├─ final_laptop_data_unprocessed_4.csv
│  │  │  │  ├─ laptop_urls.txt
│  │  │  │  └─ scripts
│  │  │  │     ├─ amazon-URL-scraper.py
│  │  │  │     └─ parseNExportProducts.py
│  │  │  ├─ amazon
│  │  │  │  ├─ Amazon Data Cleaning.ipynb
│  │  │  │  └─ consolidated_amazon_laptop_data.csv
│  │  │  └─ consolidated_amazon_laptop_data.csv
│  │  ├─ bestBuy
│  │  │  ├─ BestBuy Data Collection,Data Cleaning.ipynb
│  │  │  ├─ laptops_data_Best_Buy_22_09_24.csv
│  │  │  ├─ laptops_data_Best_Buy_25_09_24.csv
│  │  │  └─ rawPageBestBuy.csv
│  │  └─ flipkart
│  │     ├─ flipkart_laptop_cleaned.csv
│  │     ├─ flipkart_laptop_data.csv
│  │     ├─ raw.csv
│  │     └─ rawPage.csv
│  └─ images
│     ├─ DatabaseBrowsedData.jpg
│     ├─ DatabaseSummary.jpg
│     └─ pages.jpg
├─ Phase2
│  ├─ Project Laptrack - Phase 2 Model Building.ipynb
│  └─ dataCollection
│     ├─ Data Collection Phase 2 Template.ipynb
│     ├─ LaptrackPhase2.csv
│     ├─ amazon
│     │  ├─ Untitled.ipynb
│     │  ├─ amazon-URL-scraper.py
│     │  ├─ amazonCleaning.ipynb
│     │  ├─ amazon_clean.csv
│     │  ├─ amazon_failed_urls7.txt
│     │  ├─ amazon_laptop_data5.csv
│     │  ├─ amazon_laptop_data6.csv
│     │  ├─ amazon_laptop_data7.csv
│     │  ├─ amazon_laptop_data8.csv
│     │  ├─ amazon_scraped_data_1.csv
│     │  ├─ laptop_urls.txt
│     │  ├─ parseNExportProducts.py
│     │  └─ unscrapedurls.txt
│     ├─ bestbuy
│     │  ├─ bestbuy-cleaning.ipynb
│     │  ├─ bestbuy-scraper.py
│     │  ├─ bestbuy-url-scrapper.py
│     │  ├─ bestbuy_clean.csv
│     │  ├─ bestbuy_failed_urls4.txt
│     │  ├─ bestbuy_laptop_data.csv
│     │  ├─ bestbuy_laptop_data2.csv
│     │  ├─ bestbuy_laptop_data4.csv
│     │  └─ bestbuy_laptop_urls.txt
│     ├─ flipkart
│     │  ├─ flipkart-scraper.py
│     │  ├─ flipkart-url-scrapper.py
│     │  ├─ flipkartCleaning.ipynb
│     │  ├─ flipkart_clean.csv
│     │  ├─ flipkart_failed_urls6.txt
│     │  ├─ flipkart_laptop_data5.csv
│     │  ├─ flipkart_laptop_data6.csv
│     │  └─ flipkart_laptop_urls.txt
│     └─ phase2DataCollection.ipynb
├─ Phase3
│  ├─ report.pdf
│  └─ root
│     ├─ app
│     │  └─ laptrack
│     │     ├─ Dockerfile
│     │     ├─ app
│     │     │  └─ etl
│     │     │     └─ clean_data
│     │     │        ├─ Laptrack_1.csv
│     │     │        ├─ amazon_cleaned_data_1.csv
│     │     │        ├─ bestbuy_cleaned_data_1.csv
│     │     │        └─ flipkart_cleaned_data_1.csv
│     │     ├─ docker-compose.yml
│     │     ├─ etl
│     │     │  ├─ BestBuyCleaner.py
│     │     │  ├─ FlipkartCleaner.py
│     │     │  ├─ amazonCleaner.py
│     │     │  ├─ amazonScraper.py
│     │     │  ├─ combinedCleaner.py
│     │     │  ├─ etl_script.py
│     │     │  ├─ laptopUrls
│     │     │  │  ├─ amazon_laptop_urls.txt
│     │     │  │  ├─ bestbuy_laptop_urls.txt
│     │     │  │  └─ flipkart_laptop_urls.txt
│     │     │  └─ scraped_data
│     │     │     ├─ amazon_scraped_data_1.csv
│     │     │     ├─ bestbuy_scraped_data_1.csv
│     │     │     └─ flipkart_scraped_data_1.csv
│     │     ├─ flask_app
│     │     │  ├─ app.py
│     │     │  ├─ config.py
│     │     │  ├─ ml
│     │     │  │  ├─ GBDT_model.pkl
│     │     │  │  ├─ XGBoost_model.pkl
│     │     │  │  ├─ label_encoders.pkl
│     │     │  │  └─ scaler.pkl
│     │     │  ├─ models
│     │     │  │  ├─ __init__.py
│     │     │  │  └─ laptop.py
│     │     │  ├─ routes
│     │     │  │  ├─ __init__.py
│     │     │  │  ├─ laptop_routes.py
│     │     │  │  └─ recommendation_routes.py
│     │     │  └─ utils
│     │     │     ├─ __init__.py
│     │     │     └─ ml_utils.py
│     │     ├─ laptrack
│     │     │  ├─ .gitignore
│     │     │  ├─ Dockerfile
│     │     │  ├─ README.md
│     │     │  ├─ package-lock.json
│     │     │  ├─ package.json
│     │     │  ├─ public
│     │     │  │  ├─ favicon.ico
│     │     │  │  ├─ index.html
│     │     │  │  ├─ manifest.json
│     │     │  │  └─ robots.txt
│     │     │  └─ src
│     │     │     ├─ App.css
│     │     │     ├─ App.js
│     │     │     ├─ App.test.js
│     │     │     ├─ api.js
│     │     │     ├─ components
│     │     │     │  ├─ BuyingOptions.css
│     │     │     │  ├─ BuyingOptions.js
│     │     │     │  ├─ LaptopCard.css
│     │     │     │  ├─ LaptopCard.js
│     │     │     │  ├─ LaptopDetail.css
│     │     │     │  ├─ LaptopDetail.js
│     │     │     │  ├─ Navbar.css
│     │     │     │  ├─ Navbar.js
│     │     │     │  ├─ PriceStatsTable.js
│     │     │     │  ├─ ProtectedRoutes.js
│     │     │     │  ├─ SimilarProducts.css
│     │     │     │  └─ SimilarProducts.js
│     │     │     ├─ index.css
│     │     │     ├─ index.js
│     │     │     ├─ layout
│     │     │     │  └─ Layout.js
│     │     │     ├─ pages
│     │     │     │  ├─ AboutPage.js
│     │     │     │  ├─ AdminDashboard.js
│     │     │     │  ├─ ContactPage.js
│     │     │     │  ├─ Homepage.css
│     │     │     │  ├─ Homepage.js
│     │     │     │  ├─ LoginPage.css
│     │     │     │  ├─ LoginPage.js
│     │     │     │  ├─ PricePredictor.css
│     │     │     │  └─ PricePredictor.js
│     │     │     ├─ reportWebVitals.js
│     │     │     └─ setupTests.js
│     │     ├─ requirements.txt
│     │     └─ start.sh
│     └─ exp
│        ├─ Phase3-Final ML model.ipynb
│        ├─ Project Laptrack - Phase 2 Model Building.ipynb
│        ├─ Recommendation System.ipynb
│        └─ ml_models
│           ├─ GBDT_model.pkl
│           ├─ XGBoost_model.pkl
│           ├─ label_encoders.pkl
│           └─ scaler.pkl
├─ README.md
├─ data
│  └─ laptrack.csv
├─ database
│  └─ laptrack.db
└─ requirements.txt
```
©generated by [Project Tree Generator](https://woochanleee.github.io/project-tree-generator)

## Project Demo Video
[Video Demo YT](https://youtu.be/WnHhlB1WFgM)

## Project Hypothesis and Questions For Each Member

**Member 1: Shaurya Mathur**

``
How does the amount of RAM in a laptop, along with processor company, storage type, operating system, display size, laptop weight, stock availability, and number of reviews, affect its price?
``

>Location in Model Building Notebook
Question Line Number: Section 4.1,4.2
Analysis Line Number: Section 4.1,4.2

``
How does the choice of processor company, along with operating system, RAM size, laptop weight, stock availability, and number of reviews, influence laptop prices across different price ranges?
``

> Location in Model Building Notebook
Question Line Number: Section 4.3,4.4
Analysis Line Number: Section 4.3,4.4

**Member 2: Vaibhav Saran**

``
How does the similarity in specifications (including RAM, processor company, storage type, operating system, screen size, laptop weight, and number of reviews) affect the prices of laptops across different brands?
``

>Location in Model Building Notebook
Question Line Number: Section 4.5,4.6
Analysis Line Number: Section 4.5,4.6

``
How do different types of storage (e.g., SSD, HDD), along with screen size, processor type, RAM size, laptop weight, operating system, stock availability, and number of reviews, affect laptop prices?
``
> Location in Model Building Notebook
Question Line Number: Section 4.7,4.8
Analysis Line Number: Section 4.7,4.8

**Member 3: Yeswanth Chitturi**

``
How do variations in brand, along with processor type, storage size, display size, RAM size, operating system, laptop weight, and number of reviews, impact the price of laptops?
``

> Location in Model Building Notebook
Question Line Number: Section 4.9,4.10
Analysis Line Number: Section 4.9,4.10

``
How do screen sizes, RAM, processor company, storage type, laptop weight, stock availability, and number of reviews, influence the prices of laptops across different brands?
``

> Location in Model Building Notebook
Question Line Number: Section 4.11,4.12
Analysis Line Number:Section 4.11,4.12
