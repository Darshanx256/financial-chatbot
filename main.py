import pandas as pd
import re
from difflib import get_close_matches

# load and sort once
df = pd.read_csv("balance_long.csv")
df = df.sort_values(by=["Company", "Fiscal Year"])

# memory lists for asking folow ups
previous_company = []
previous_year    = []
previous_field   = []

# for user friendly text inputs
FIELD_ALIASES = {
    "cash flow": "Cash Flow",
    "cf": "Cash Flow",
    "cashflow": "Cash Flow",
    "net income": "Net Income",
    "ni": "Net Income",
    "total revenue": "Total Revenue",
    "revenue": "Total Revenue",
    "total assets": "Total Assets",
    "assets": "Total Assets",
    "total liabilities": "Total Liabilities",
    "liabilities": "Total Liabilities",
    "debts": "Total Liabilities",
    "profit": "Net Income",
    "income": "Net Income"
}

# keywords that trigger change-over-time
COMPARISON_KEYWORDS = [
    "gone up", "increased", "decreased", "increase",
    "decrease", "improved", "worsened"
]

def extract_years(query: str):   #to fetch years from query and store it in memory with gibberish guard
    found_years = [int(yr) for yr in re.findall(r'\b(20\d{2})\b', query)]
    if found_years:
        previous_year.clear()
        previous_year.extend(found_years)
        return found_years, True

    return list(previous_year), False

def extract_field(query: str):  #to fetch field from query and store it in memory with gibberish guard
    q_lower = query.lower()
    for keyword, real_col in FIELD_ALIASES.items():
        if keyword in q_lower:
            previous_field.clear()
            previous_field.append(real_col)
            return real_col, True

#fetching close matches in case of typo or shortcut used

    close = get_close_matches(q_lower, FIELD_ALIASES.keys(), n=1, cutoff=0.5)
    if close:
        matched = FIELD_ALIASES[close[0]]
        previous_field.clear()
        previous_field.append(matched)
        return matched, True

    if previous_field:
        return previous_field[0], False

    return None, False

def extract_company_names(query: str):   #to fetch company name from query and store it in memory with gibberish guard
    companies = df['Company'].unique()
    q_lower = query.lower()
    found = []

    for name in companies:
        if name.lower() in q_lower:
            found.append(name)

    if found:
        previous_company.clear()
        previous_company.extend(found)
        return found, True

    words = re.findall(r'\b\w+\b', q_lower)
    fuzzies = []
    for w in words:
        close = get_close_matches(w, [c.lower() for c in companies], n=1, cutoff=0.8)
        if close:
            actual = next((c for c in companies if c.lower() == close[0]), None)
            if actual:
                fuzzies.append(actual)

    fuzzies = list(set(fuzzies))
    if fuzzies:
        previous_company.clear()
        previous_company.extend(fuzzies)
        return fuzzies, True

    return list(previous_company), False

def get_latest_year(company_data: pd.DataFrame):
    return company_data['Fiscal Year'].max()

def get_previous_year(company_data: pd.DataFrame):
    yrs = sorted(company_data['Fiscal Year'].unique())
    return yrs[-2] if len(yrs) >= 2 else None

def compare_years(df: pd.DataFrame, company: str, field: str, y1: int, y2: int):
    data = df[df['Company'].str.lower() == company.lower()]
    if field is None:
        return "Sorry, I couldn't determine the financial metric you're asking about."

    row1 = data[data['Fiscal Year'] == y1]
    row2 = data[data['Fiscal Year'] == y2]
    if row1.empty or row2.empty:
        return f"Data for {company} in {y1} or {y2} not found."

    v1, v2 = row1.iloc[0][field], row2.iloc[0][field]
    diff  = v2 - v1
    pct   = (diff / v1 * 100) if (v1 != 0) else 0
    trend = "increased" if diff > 0 else "decreased"
    return (
        f"{company}'s {field} {trend} by ${abs(diff):,} "
        f"({abs(pct):.2f}%) from {y1} (${v1:,}) to {y2} (${v2:,})."
    )

def compare_companies(
    df: pd.DataFrame,
    company1: str, year1: int,
    company2: str, year2: int,
    field: str
):
    if field is None:
        return "Sorry, I couldn't determine the financial metric you're asking about."

    d1 = df[(df['Company'].str.lower() == company1.lower()) & (df['Fiscal Year'] == year1)]
    d2 = df[(df['Company'].str.lower() == company2.lower()) & (df['Fiscal Year'] == year2)]
    if d1.empty or d2.empty:
        return "Some data is missing."

    v1 = d1.iloc[0][field]
    v2 = d2.iloc[0][field]
    if year1 == year2:
        return (f"In {year1}, {company1} had ${v1:,} in {field} and "
                f"{company2} had ${v2:,}.")
    return (f"In {year1}, {company1} had ${v1:,} in {field}, whereas in {year2}, "
            f"{company2} had ${v2:,}.")

def chatbot(user_query: str):
    user_query = user_query.lower()

    # 1) Extract matches and “found this turn” flags
    companies, found_company_this_turn = extract_company_names(user_query)
    years,      found_year_this_turn    = extract_years(user_query)
    field,      found_field_this_turn   = extract_field(user_query)

    # 2) Detect presence of comparison keywords
    has_comparison_kw = any(kw in user_query for kw in COMPARISON_KEYWORDS)

    # 3) Gibberish guard: if NONE of these four is True, bail out
    if not (found_company_this_turn or
            found_year_this_turn or
            found_field_this_turn or
            has_comparison_kw):
        return "Sorry, I couldn’t understand. Try mentioning a company, field, or year."

    # 4) Default field if not specified this turn and no prior memory
    if not found_field_this_turn and not previous_field:
        field = "Total Revenue"

    # 5) Two-company comparison
    if len(companies) == 2:
        if len(years) == 1:
            years = [years[0], years[0]]
        return compare_companies(df,
                                 companies[0], years[0],
                                 companies[1], years[1],
                                 field)

    # 6) Single-company logic
    if len(companies) == 1:
        company_name = companies[0]
        data = df[df['Company'].str.lower() == company_name.lower()]

        # 6a) “last year”
        if "last year" in user_query:
            latest   = get_latest_year(data)
            previous = get_previous_year(data)
            if not previous:
                return f"Not enough data to compare last year for {company_name}."
            return compare_years(df, company_name, field, previous, latest)

        # 6b) Comparison keywords (“increased”, “decreased”, etc.)
        if has_comparison_kw:
            latest   = get_latest_year(data)
            previous = get_previous_year(data)
            if not previous:
                return f"Not enough data to determine change for {company_name}."
            return compare_years(df, company_name, field, previous, latest)

        # 6c) Exactly two years specified
        if len(years) >= 2:
            return compare_years(df, company_name, field, years[0], years[-1])

        # 6d) Exactly one year specified
        if len(years) == 1:
            y   = years[0]
            val = data[data['Fiscal Year'] == y]
            if val.empty:
                previous_year.clear()
                return f"No data for {company_name} in {y}."
            return f"{company_name}'s {field} in {y} was ${val.iloc[0][field]:,}."

        # 6e) No year specified → use latest
        if len(years) == 0:
            latest = get_latest_year(data)
            val    = data[data['Fiscal Year'] == latest]
            if val.empty:
                return f"No data for {company_name} in {latest}."
            return f"{company_name}'s {field} in {latest} was ${val.iloc[0][field]:,}."

    # 7) Fallback
    return "Sorry, I couldn’t understand. Try mentioning a company, field, or year."

def run_chat():
    print("🤖 Welcome to your Financial Chatbot!")
    print("Type 'exit' anytime to quit.\n")

    while True:
        user_input = input("💬 You: ")
        if user_input.strip().lower() == 'exit':
            print("👋 Goodbye!")
            break

        response = chatbot(user_input)
        print("🤖 Bot:", response)

if __name__ == "__main__":
    run_chat()
