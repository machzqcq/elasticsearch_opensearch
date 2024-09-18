# Field Mappings

## category
- **type**: text - This field is analyzed and tokenized.
    - **fields.keyword**: type: keyword - A sub-field for exact matches.

## currency
- **type**: keyword - Used for exact matches.

## customer_birth_date
- **type**: date - Stores date values.

## customer_first_name, customer_full_name, customer_last_name
- **type**: text - Analyzed and tokenized.
    - **fields.keyword**: type: keyword, ignore_above: 256 - Sub-field for exact matches, ignoring values longer than 256 characters.

## customer_gender, customer_id, customer_phone, day_of_week, email, order_id, sku, type, user
- **type**: keyword - Used for exact matches.

## day_of_week_i
- **type**: integer - Stores integer values.

## event
- **properties.dataset**: type: keyword - Nested field for exact matches.

## geoip
- **properties.city_name, properties.continent_name, properties.country_iso_code, properties.region_name**: type: keyword - Nested fields for exact matches.
- **properties.location**: type: geo_point - Stores geographical points.

## manufacturer
- **type**: text - Analyzed and tokenized.
    - **fields.keyword**: type: keyword - Sub-field for exact matches.

## order_date
- **type**: date - Stores date values.

## products
Nested properties for product details:
- **_id**: type: text
    - **fields.keyword**: type: keyword, ignore_above: 256 - Analyzed and tokenized, with a sub-field for exact matches.
- **base_price, base_unit_price, discount_amount, discount_percentage, min_price, price, tax_amount, taxful_price, taxless_price, unit_discount_amount**: type: half_float - Stores floating-point numbers with reduced precision.
- **category, manufacturer, product_name**: type: text
    - **fields.keyword**: type: keyword - Analyzed and tokenized, with sub-fields for exact matches.
- **created_on**: type: date - Stores date values.
- **product_id**: type: long - Stores long integer values.
- **quantity**: type: integer - Stores integer values.
- **sku**: type: keyword - Used for exact matches.
- **taxful_total_price, taxless_total_price**: type: half_float - Stores floating-point numbers with reduced precision.
- **total_quantity, total_unique_products**: type: integer - Stores integer values.

## Summary
This mapping configuration is designed to handle various types of data, including text, dates, numbers, and geographical points. It uses different field types like text for analyzed fields, keyword for exact matches, date for date values, integer and long for integer values, and half_float for floating-point numbers with reduced precision. Nested fields are also used for complex objects like event and products.