# 📊 Financial Chatbot

A lightweight CLI-based financial chatbot built with Python. While it *feels* like it understands natural language, under the hood, it smartly picks up key information from your query and performs precise data extraction from a CSV file containing real financial figures scraped from official 10-K filings.

---

## 1. 🚀 Capabilities

1.1 Responds to direct financial queries for a company
1.2 Year-over-year performance comparisons
1.3 Side-by-side company and multi-year analysis
1.4 **Follows up with context from your previous question** ✨
1.5 Handles common typos and fuzzy word matches

The chatbot uses the `pandas` library to interact with structured financial data and preserves memory between queries during a session.

---

## 2. 📁 Setup Instructions

2.1 Place the CSV file and `main.py` in the same directory.
2.2 The CSV follows a 'long format' making data fetching efficient and intuitive.

**Example structure:**

```
Company,Fiscal Year,Metric,Value
Tesla,2022,Net Income,#####
Tesla,2023,Net Income,#####
Apple,2023,Cash Flow,#####
Apple,2024,Cash Flow,#####
```

2.3 You can add more companies to the CSV. Just ensure each has at least two consecutive years of data for comparisons to work seamlessly.

---

## 3. 📦 Dependencies

* Python 3.7 or above
* pandas

(No external packages beyond `pandas` are needed.)

---

## 4. ▶️ How to Run

1. Open a terminal in the project directory
2. Run the chatbot using:

```
python main.py
```

3. Type your query, and let the bot do the thinking 💬
4. Type `exit` anytime to quit.

---

## 5. 🧠 Extraction Logic

When you type a natural query, the chatbot extracts in this order:

### 5.1 Company Name

* Looks for exact names or fuzzy matches (e.g., “tesl” → Tesla)
* If not found in this prompt, uses the last mentioned one

### 5.2 Year(s)

* Accepts 4-digit years between 2000–2099
* Can understand multiple years like “2022 and 2024”
* Defaults to previous year(s) if unspecified

### 5.3 Metric / Field

Recognized financial metrics include:

* Cash Flow (“cash flow”, “cf”, etc.)
* Net Income (“net income”, “profit”, etc.)
* Total Revenue (“revenue”)
* Total Assets (“assets”)
* Total Liabilities (“liabilities”, “debts”)

If none is found, it defaults to **Total Revenue**, unless a previous field is remembered.

---

## 6. 🔁 Follow-Up Awareness

* If you mention “Compare with last year,” it remembers your previous company and metric.
* Follow-ups like “What about Apple?” or “And in 2022?” use earlier context.
* Context resets only when a new company + new metric are both introduced.

---

## 7. 🚧 Gibberish Guard

If no recognizable data is found in your input, the bot says:

```
Sorry, I couldn’t understand. Try mentioning a company, field, or year.
```

Triggers for a valid response include:

* New company
* New year
* Recognized metric
* Comparison keyword (e.g., “increase”)

---

## 8. 📊 Comparison Logic

### 8.1 Two-Company Comparison

* If two companies are identified:

  * One year → compares both in that year
  * Two years → compares Company1 in Year1 vs Company2 in Year2

### 8.2 Single-Company Logic

If only one company is detected:

* “last year” → compares latest vs previous year
* Keywords like “improved” trigger comparisons
* Two explicit years → direct year comparison
* One year → returns that year's data
* No year → returns the latest available

---

## 9. 📘 Supported Metrics & Aliases

| Metric            | Recognized Aliases                          |
| ----------------- | ------------------------------------------- |
| Cash Flow         | "cash flow", "cf", "cashflow"               |
| Net Income        | "net income", "ni", "income", "profit"      |
| Total Revenue     | "total revenue", "revenue"                  |
| Total Assets      | "total assets", "assets"                    |
| Total Liabilities | "total liabilities", "liabilities", "debts" |

---

## 10. 🏢 Supported Companies

Initial dataset includes:

* Apple
* Microsoft
* Tesla

(You can expand the dataset by adding more rows to the CSV.)

---

## 11. 📈 Comparison Keywords

Trigger words that activate comparison logic:

* “gone up”
* “increased”
* “decreased”
* “improved”
* “worsened”

---

## 12. 🧪 Example Queries & Responses

### 12.1 Single Company, Single Year

```
You: Tesla’s net income in 2023?
Bot: Tesla’s Net Income in 2023 was $#####.
```

### 12.2 Single Company, No Year

```
You: Apple’s cash flow?
Bot: Apple’s Cash Flow in 2024 was $#####.
```

### 12.3 “Last Year” or Trend Keyword

```
You: Has Microsoft’s revenue improved?
Bot: Microsoft’s Total Revenue increased by $##### (X.XX%) from 2023 to 2024.
```

### 12.4 Two-Year Comparison

```
You: Compare Apple’s cash flow in 2022 and 2024.
Bot: Apple’s Cash Flow increased by $##### (X.XX%) between the two years.
```

### 12.5 Two Companies, Same Year

```
You: Compare Tesla and Apple’s net income in 2023.
Bot: In 2023, Tesla had $##### Net Income, and Apple had $#####.
```

### 12.6 Two Companies, Different Years

```
You: Compare Microsoft 2022 revenue with Tesla 2024 revenue.
Bot: Microsoft had $##### in 2022, while Tesla had $##### in 2024.
```

---

## 13. 🚀 Try It Yourself

Ready to give it a try? Just copy paste these commands:

```bash
git clone https://github.com/Darshanx256/financial-chatbot.git
cd financial-chatbot
pip install -r requirements.txt
python main.py
```

🎉 Thanks for reading this far! Try out the bot if possible.

