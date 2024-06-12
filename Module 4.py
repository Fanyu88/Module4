import pandas as pd
import numpy as np

# Part 1: Explore the Data

# Load the dataset
file_path = 'client_dataset.csv'
data = pd.read_csv(file_path)

# View the column names
print("Column Names:", data.columns)

# Use the describe function to gather some basic statistics
print("\nBasic Statistics:\n", data.describe())

# 1. What three item categories had the most entries?
top_categories = data['category'].value_counts().head(3).reset_index()
top_categories.columns = ['Category', 'Count']
print("\nTop 3 Item Categories:\n", top_categories)

# 2. For the category with the most entries, which subcategory had the most entries?
top_category = top_categories['Category'][0]
top_subcategory = data[data['category'] == top_category]['sub_category'].value_counts().idxmax()
print("\nTop Subcategory in the Top Category:", top_subcategory)

# 3. Which five clients had the most entries in the data?
top_clients = data['client_id'].value_counts().head(5).reset_index()
top_clients.columns = ['Client ID', 'Count']
print("\nTop 5 Clients:\n", top_clients)

# Store the client ids of those top 5 clients in a list
top_client_ids = top_clients['Client ID'].tolist()
print("\nTop 5 Client IDs:", top_client_ids)

# 4. How many total units (the qty column) did the client with the most entries order?
top_client_id = top_client_ids[0]
total_units = data[data['client_id'] == top_client_id]['qty'].sum()
print(f"\nTotal Units Ordered by Top Client ({top_client_id}):", total_units)


# Part 2: Transform the Data

# Create a column that calculates the subtotal for each line using the unit_price and the qty
data['subtotal'] = data['unit_price'] * data['qty']

# Create a column for shipping price. Assume shipping price of $7 per pound for orders over 50 pounds and $10 per pound for items 50 pounds or under.
data['shipping_price'] = data['Weight'].apply(lambda w: 7 * w if w > 50 else 10 * w)

# Create a column for the total price using the subtotal and the shipping price along with a sales tax of 9.25%
data['total_price'] = (data['subtotal'] + data['shipping_price']) * 1.0925

# Create a column for the cost of each line using unit cost, qty, and shipping price
data['line_cost'] = data['unit_cost'] * data['qty'] + data['shipping_price']

# Create a column for the profit of each line using line cost and line price
data['profit'] = data['total_price'] - data['line_cost']

# View the transformed data
print("\nTransformed Data:\n", data.head())


# Part 3: Confirm Your Work

# Confirming the total prices for given order IDs
order_ids = [2742071, 2173913, 6128929]
expected_totals = [152811.89, 162388.71, 923441.25]

for order_id, expected_total in zip(order_ids, expected_totals):
    calculated_total = data[data['order_id'] == order_id]['total_price'].sum()
    print(f"\nOrder ID {order_id} - Calculated Total: ${calculated_total:.2f}, Expected Total: ${expected_total:.2f}")


# Part 4: Summarize and Analyze

# Calculate the total revenue from each of the top 5 clients
top_client_revenue = data[data['client_id'].isin(top_client_ids)].groupby('client_id')['total_price'].sum().reset_index()
top_client_revenue.columns = ['Client ID', 'Total Revenue']
print("\nTop 5 Client Revenue:\n", top_client_revenue)

# Create a summary DataFrame for the top 5 clients
summary = data[data['client_id'].isin(top_client_ids)].groupby('client_id').agg(
    total_units=('qty', 'sum'),
    total_shipping_price=('shipping_price', 'sum'),
    total_revenue=('total_price', 'sum'),
    total_profit=('profit', 'sum')
).reset_index()

# Function to change the currency to millions of dollars
to_millions = np.vectorize(lambda x: x / 1_000_000)

# Apply the function and format the DataFrame
summary_millions = summary.copy()  # Avoid modification warnings
summary_millions[['total_units', 'total_shipping_price', 'total_revenue', 'total_profit']] = summary_millions[['total_units', 'total_shipping_price', 'total_revenue', 'total_profit']].apply(to_millions)
summary_millions = summary_millions.round(2)
summary_millions.columns = ['Client ID', 'Total Units (M)', 'Total Shipping Price (M$)', 'Total Revenue (M$)', 'Total Profit (M$)']

# Sort the DataFrame in descending order by total profits
summary_millions = summary_millions.sort_values(by='Total Profit (M$)', ascending=False)
print("\nFormatted Client Summary:\n", summary_millions)

# Write a brief summary of the findings
summary_text = f"""
The analysis revealed that the top 5 clients are significant contributors to the company's revenue and profit. 
The client with the most entries ordered a total of {total_units} units. Overall, these clients generated considerable profits, with the highest total profits being {summary_millions['Total Profit (M$)'].max():.2f} million dollars.
"""
print(summary_text)
