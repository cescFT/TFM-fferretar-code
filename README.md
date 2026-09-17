# Food environment on Mercadona's supermarket

## Brief resume of the project

The aim of this project is to store all code and stuff necessary for my own TFM on Data Science Master at Universitat Oberta de Catalunya.

The TFM is based on check if [Mercadona](https://www.mercadona.es/) online store helps or not the customers on buying good foods.
For this reason, I have developed software which is able to obtain data using web scraping techniques across mercadona's online supermarket.

Finally, there is also a part of software which will get all the data retrieved from web scraping techniques and will extract conclusions
using data analysis techiques.

## Configuration

TODO: Aqui quan tingui el tema de l'anàlisi de dades, s'ha d'explicar

***NOTE: ALL CONFIGURATIONS ARE CHECKED IN WINDOWS 11 ENVIRONMENT***

In order to configure the project, you have to follow certain steps. For pick up data is necessari follow these steps:

1. Create a **virtual environment**:

```bash
python -m venv tfm-env
```

2. If you use Pycharm, you need to configure the virtual environment:

    * Go to File menu > Settings > Python environment
    * Change interpreter from local and existing
    * Then, select *tfm-env*

3. Activate the **virtual environment**:

```bash
.\tfm-env\Scripts\activate.ps1
```

4. Install requirements:

```bash
pip install -r requirements.txt
```

Finally, if you want to exit virtual environment, you have to use command `deactivate`.

## Folder structure

TODO: Aqui quan tingui el tema de l'anàlisi de dades, s'ha d'explicar

* `csv/`: The idea of this folder is to save final dataset to analyze in the step of data analysis.
* `db/`: In this folder, the project which is abled to retrieve information from online supermarket, save the data in
sqlite database. The structure of this database can be seen in `create_db_table_statement.sql` file. The sqlite
database is `mercadona-scraper-results.db` folder. Also, you can see another file called `queries_debug.sql`. This file
is just to check specific sql's used in other parts of the project.
* `src/`:
  * `db_to_csv/`: This folder has python script called `db_to_csv.py`. This script is responsible for transferring data
  from the database to a CSV file, which will then be processed during the data analysis stage.
  * `mercadona_scraper/`: This folder has all the necessary for retrieve information from mercadona's online supermarket.
    * `constants/constants_variables.py`: This file contains all constants of all project.
    * `driver_creator/creator.py`: Creates Selenium object that it allow navigate into online supermarket.
    * `dto/`: Contains all *Data Transfer Objects* used in different points of collecting data.
      * `gemni_model_data.py`: Contains class `GeminiModelDTO` which has all necessary to check whether gemini
      model is blocked or not.
      * `product_nutritional_data.py`: Contains different classes:
        * `CiqualDTO`: This class represents information from [Ciqual](https://ciqual.anses.fr/). This data is used
        for planet score.
        * `NutrientDTO`: This class is used when products has to be processed in order to get nutriments. 
        * `CertificationDTO`: This class contains all information to create certifications of the products. This 
        certifications then will be used for calculate planet score.
        * `ProductNutritionalDataDTO`: This class constructs all nutritional data of certain product for save nutriments.
        * `NutrimentDataDTO`: The meaning of this class is different in comparison of `NutrientDTO` class. The difference
        is based on if nutriment is saved in database or not. If is not saved, I use `NutrientDTO`, if not, I use `NutrimentDataDTO`.
        This data is used for calculate nutriscore.
        * `ProductNutrimentsDTO`: This class constructs all nutritional data of certain product for calculate nutriscore.
      * `product_scrap_data.py`: Contains `ProductScrapedDTO` class which represents all data scraped from online supermarket.
      * `product_scrap_data_request.py`: Contains `ProductScrapDataRequestDTO` class which is a request for scrape data.
    * `mercadona_api/utils.py`: Permit to make cURL requests to mercadona's API.
    * `mercadona_navigator/initialize_mercadona_grocery.py`: As you can read on the name of this python file, the content 
    of this file is to initialize navigation across online supermarket.
    * `mercadona_navigator/navigate_through_main_page.py`: This file contains code that enables navigate to main page
    and get links to follow with products.
    * `mercadona_navigator/product_scrap_data.py`: Contains code that enables retrieve information from specific product.
    * `utils/utls.py`: Contains stuff such as get path of database. Contain general functions used in all project.
    * `validations/validate_postal_code.py`: As customer of my application, you can introduce a postal code as argument. So,
    it need to be validated if is recognized as valid. This file contains code to check this.
    * `mercadona_scraper_main.py`: Script which scrape data from online supermarket and save data into database.
    * `mercadona_scraper_categories_aggregation_main.py`: Script which retrieve an aggregation data of total products for each category.
  * `nutritional_data/`: This folder contains the second part to enrich data scraped from online supermarket. New
  variables added in scripts contained in this folder are nutritional data such as energy, salt, fat, ... . This data
  is used to calculate nutriscore. Thus, new variables added are nutritrional data and nutriscore.
    * `ciqual/requests.py`: Contains ElasticSearch query to get data from ciqual for then calculate planet score.
    * `ewo/calculate_ultraprocessed_punctuation.py`: Contains the implementation of the algorithm to calculate ultraprocessed qualifications of products.
    * `ewo/parse_mercadona_categories_to_ewo_categories.py`: Parses Mercadona categories to EWO categories.
    * `gemini_integration/connect.py`: Creates gemini client object which ables to make gemini requests.
    * `gemini_integration/model_getter.py`: Retrieve gemini model enabled to make petitions.
    * `gemini_integration/request.py`: Makes petitions to gemini model.
    * `interact_db/get_data_from_db.py`: Contain functions that retireve data from database.
    * `interact_db/update_gemini_model.py`: Update content to database about gemini models.
    * `interact_db/update_products_to_db.py`: Functions resposables of updating product information.
    * `manual_nutritional_processing/nutritional_info.py`: Process products manually for getting nutritional information.
    * `nutriments_processing/process_response.py`: Functions that process informations from gemini and save nutritional
    information into database.
    * `nutriscore/beverages_calculator.py`: Calculator of nutriscore for beverages category.
    * `nutriscore/calculate_nutriscore.py`: Nutriscore calculator using 2023 updated algorithm.
    * `nutriscore/cheese_calculator.py`: Calculator of nutriscore for cheese category.
    * `nutriscore/fats_oils_nuts_seeds_calculator.py`: Calculator of nutriscore for fats, oils, nuts and seeds category.
    * `nutriscore/general_food_calculator.py`: Calculator of nutriscore for general food category.
    * `nutriscore/nutriments_getter.py`: Parse nutritional score of database into requests for calculators of nutriscore.
    * `nutriscore/parse_mercadona_category_to_nutriscore_category.py`: Calculate category of nutriscore using
    mercadona category, subcategory and second subcategory.
    * `nutriscore/red_meat_calculator.py`: Calculator of nutriscore for red meat category.
    * `nutriscore_calculator_handler.py`: Script that calculates nutriscore.
    * `ewo_ultraprocessed_punctuation_handler.py`: Script that calculates ultraprocessed punctuation.
    * `nutritional_data_handler.py`: Script that retrieve nutritional information of product and save it into database.

## How to execute retrieve data from Mercadona supermarket online?

The execution flow of retrieve information from Mercadona supermarket is:

1. **Web scraping**

First of all you need to execute script `src/mercadona_scraper/mercadona_scraper_main.py`. This script retrieve data from
mercadona's supermarket online using techniques of web scraping and save data into database. Also, uses mercadona API
in order to get individual product information.

The technology behind web scraping is made with Selenium and BeautifulSoup.

This script allow the use of different arguments:
* ***-cp***: Postal code of the user. In this case only are allowed two different postal codes (08032 / 43812). If you try
to use another one, you will get an exception.
* ***clear***: With the execution of this argument, all data from existing database will be removed. It's just like hard reset.

1.1. **Web scraping - retrieve aggregated data of total products in each category/subcategory**

To have more context when analyze data, after executing the script above mentioned, you need to execute the script 
`src/mercadona_scraper/mercadona_scraper_categories_aggregation_main.py` which iterates over all categories and subcategories
to collect how many products are available to be sold in each category/subcategory.

This script allows the use of different arguments:
* ***-cp***: Postal code of the user. In this case only are allowed two different postal codes (08032 / 43812). If you try
to use another one, you will get an exception.

2. **Retrieve nutritional data**

With the execution of the first script you will obtain a lot of information of the products. Essentially, you will have
data from product obtained with web scraping and mercadona API. But in this point, products doesn't have nutritional
information. In order to get this data, all you have to do is execute script `src/nutritional_data/nutritional_data_handler.py`.

This script will fill nutritional information into database. It have two modalities: automatic or manual.

Automatic is abled with gemini models, which are stored in `gemini_models` table into database. For the good execution
of this, you need to have an `.env` file with just single variable called `GEMINI_API_KEY` that you can generate using
[Google AI Studio](https://aistudio.google.com/). Please, check out information on how to generate api keys for this
searching on internet. So, with the use of gemini models, substitutes OCR script, and works very well.

On the other hand, the manual modality the only difference in comparion in automatic once is that you have to retrieve
nutritional data from images copying and pasting prompt and images manually in gemini or another AI that allow you to
retrieve information from images.

Nevertheless, the other parts of the script works in same way even if you use it automatic or manual.

The arguments that allow this script are:

* ***manual***: Enables manual execution described above.
* ***limit***: Limit items to get nutritional data if product hasn't have nutritional data in one exection.

3. **Calculate nutriscore**

This script calculates nutriscore for all products that do not have nutriscore data calculated.

The arguments that allow this script are:

* ***limit***: Limit of products per execution which do not have nutriscore.

4. **Calculate ewo ultraprocessed qualification mark**

This scripts implements the ewo algorithm to calculate ultraprocessed qualifications of products.

The arguments that allow this scripts are:

* ***limit***: Limit of products per execution which do not have ultraprocessed qualification mark.

5. **Database content as CSV**

The last script of lifecycle about retrieve information of Mercadona online supermarket is the script called
`db_to_csv.py`. This script executes an SQL which retrieve all data from database and transforms this data to CSV format.

Also, it generates a CSV file with aggregated data of total products in each category/subcategory.
