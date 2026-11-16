"""Olist sales performance dashboard.

Run from the project root with:
    python -m streamlit run dashboard.py

Requires data_loader.py and its three SQL files to be in place.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_data

st.set_page_config(
    page_title="Olist | Sales Performance",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(show_spinner="Loading sales data...")
def get_data():
    """Load the underlying SQL results and standardize date columns."""
    monthly, categories, geography = load_data()
    monthly["time_period"] = pd.to_datetime(monthly["time_period"], format="%Y-%m")
    categories["sales_year"] = pd.to_datetime(categories["sales_year"], format="%Y")
    geography["sales_year"] = pd.to_datetime(geography["sales_year"], format="%Y")
    return monthly, categories, geography


def filter_year(df, date_column, year):
    """Return all data or only rows for a selected calendar year."""
    if year == 0:
        return df
    return df.loc[df[date_column].dt.year == year]


def sales_by_group(df, column):
    """Sum item sales at the desired reporting level."""
    return (
        df.groupby(column, as_index=False)["total_sales"]
        .sum()
        .sort_values("total_sales", ascending=False)
    )


def format_reais(value):
    return f"R$ {value:,.2f}"


sales_df, category_df, geo_df = get_data()

st.title("Olist | Sales Performance Dashboard")
st.caption("Delivered-order item sales value (excluding freight) · January 2017 – August 2018")

OPTIONS = {0: "ALL", 2017: "2017", 2018: "2018"}
selected_year = st.sidebar.segmented_control(
    "Filter by year",
    options=list(OPTIONS),
    format_func=lambda value: OPTIONS[value],
    default=0,
    selection_mode="single",
)
# When a user clears a single-select control, default back to the full period.
if selected_year is None:
    selected_year = 0

monthly = filter_year(sales_df, "time_period", selected_year)
category = filter_year(category_df, "sales_year", selected_year)
geography = filter_year(geo_df, "sales_year", selected_year)
period_label = "Jan 2017 – Aug 2018" if selected_year == 0 else str(selected_year)

# --- Executive KPIs ---
st.subheader(f"Performance overview · {period_label}")
total_sales = monthly["total_sales"].sum()
total_orders = int(monthly["total_orders"].sum())
aov = total_sales / total_orders if total_orders else 0.0

sales_col, orders_col, aov_col = st.columns(3)
sales_col.metric("Total item sales value", format_reais(total_sales), border=True)
orders_col.metric("Delivered orders", f"{total_orders:,}", border=True)
aov_col.metric("Average order value", format_reais(aov), border=True)

# --- Monthly performance ---
st.subheader("Monthly sales trend", divider=True)
monthly_fig = px.line(
    monthly,
    x="time_period",
    y="total_sales",
    markers=True,
    labels={"time_period": "Month", "total_sales": "Item sales value (R$)"},
)
monthly_fig.update_layout(hovermode="x unified", margin=dict(t=20, b=25))
monthly_fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f", rangemode="tozero")
st.plotly_chart(monthly_fig, width="stretch")

# --- Category and geographic breakdown ---
category_col, geo_col = st.columns(2, gap="large")

with category_col:
    st.subheader("Top product categories", divider=True)
    category_summary = sales_by_group(category, "category")
    top_categories = category_summary.head(10)
    unknown = category_summary.loc[category_summary["category"] == "Unknown"]
    chart_categories = (
        pd.concat([top_categories, unknown], ignore_index=True)
        .drop_duplicates(subset="category")
        .sort_values("total_sales", ascending=False)
    )
    category_fig = px.bar(
        chart_categories,
        x="total_sales",
        y="category",
        orientation="h",
        labels={"total_sales": "Item sales value (R$)", "category": "Category"},
    )
    category_fig.update_yaxes(autorange="reversed")
    category_fig.update_xaxes(tickprefix="R$ ", tickformat=",.0f")
    category_fig.update_layout(height=490, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(category_fig, width="stretch")

    category_total = category_summary["total_sales"].sum()
    unknown_share = (unknown["total_sales"].sum() / category_total * 100) if category_total else 0.0
    st.caption(f"Unclassified ('Unknown') products: {unknown_share:.2f}% of item sales value.")

with geo_col:
    st.subheader("Top customer states", divider=True)
    geo_summary = sales_by_group(geography, "customer_state")
    top_states = geo_summary.head(10)
    geo_fig = px.bar(
        top_states,
        x="customer_state",
        y="total_sales",
        labels={"customer_state": "Customer state", "total_sales": "Item sales value (R$)"},
    )
    geo_fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f", rangemode="tozero")
    geo_fig.update_layout(height=490, margin=dict(l=10, r=10, t=20, b=20))
    st.plotly_chart(geo_fig, width="stretch")

    top_three = geo_summary.head(3)
    geo_total = geo_summary["total_sales"].sum()
    top_three_share = (top_three["total_sales"].sum() / geo_total * 100) if geo_total else 0.0
    states_text = ", ".join(top_three["customer_state"].astype(str).tolist())
    st.caption(f"Top three states: {states_text} · Combined share: {top_three_share:.2f}%.")

# --- Methodology ---
st.divider()
with st.expander("Methodology & limitations"):
    st.markdown(
        """
        - **Source:** Olist Brazilian E-Commerce public dataset (historical transactions).
        - **Coverage:** Purchase months January 2017 through August 2018. The source may have incomplete coverage near the boundaries.
        - **Sales metric:** Sum of `order_items.price` for orders with status `delivered`; freight is excluded. This is **item sales value**, not Olist's audited revenue or profit.
        - **Order count:** Distinct delivered orders with at least one order-item record.
        - **AOV:** Item sales value divided by distinct orders within the selected period.
        - **Geography:** Based on the customer's state, not the seller's state.
        - **Product categories:** Missing category names are grouped under `Unknown`. The category chart shows the top ten categories plus `Unknown` if needed.
        - **Data quality:** Metrics depend on recorded order statuses and historical source completeness. Monetary figures may differ slightly due to rounding in SQL aggregations.
        """
    )
