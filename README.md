# Share Market CRM (`stock_crm`) - Custom Frappe App v15

A production-grade, next-generation **Share Market & Unlisted Equity CRM** built for Frappe Framework & ERPNext v15. Replaces manual Excel workbooks (`STOCKS_&_COUNTERPARTIES`, `MANUAL_DEAL_LEDGER`, `EXECUTIVE_MIS_DASHBOARD`, `DEAL_NOTE`) with real-time tax automation, submittable deal ledgers, 3-tier security permissions, and CA audit reports.

---

## 🌟 Key Features

- **100% Dynamic Master Registries**: `Unlisted Stock` (ISIN auto-linking), `Counterparty Profile` (PAN, DP/Client ID, multiple bank accounts), and `Company Receiving Bank`.
- **Submittable Transaction Engine (`Unlisted Deal Ledger`)**:
  - Simultaneous Inward (Seller) and Outward (Buyer) deal tracking.
  - **Live Client/Server Tax Calculators**:
    - **Stamp Duty 0.015%** under Sec 9A.
    - **TCS 0.10%** under Sec 206C(1H).
    - **Net Deal Arbitrage Profit** ($\text{Buyer Gross} - \text{Seller Gross} - \text{Brokerage} - \text{Expenses}$).
  - **3-Tier Permission Matrix**: `Stock Agent` (Draft) $\rightarrow$ `Stock Team Lead` (Submit & Lock) $\rightarrow$ `Stock Admin` (Settlements & CA Audits).
- **1-Click PDF Deal Confirmation Note**: Beautiful Jinja HTML/CSS A4 deal note formatted matching Excel Sheet 4 layout.
- **Executive P&L & CA Audit Reports**:
  - **Executive MIS & CA Audit Dashboard**: Real-time SQL rollup of turnover, net arbitrage, and quarterly **Form 27EQ TCS Return & Sec 9A Stamp Duty remittance**.
  - **Scrip Profitability Report**: Buy vs Sell margin analysis per company share.
  - **Counterparty Settlement Ledger**: Pending payouts, demat credits, and deliveries.
  - **Agent Performance Report**: Deal volume & incentive contribution per agent.

---

## 🚀 Installation Guide

### Option 1: Install on Existing Frappe Bench (Recommended)

```bash
# 1. Clone/Fetch the stock_crm app into your bench
cd ~/frappe-bench
bench get-app https://github.com/YOUR_USERNAME/stock_crm.git
# OR from local directory:
# bench get-app C:\Users\Shubh Vikani\.gemini\antigravity-ide\scratch\stock_crm

# 2. Install app on your site (e.g. stock_market.local)
bench --site stock_market.local install-app stock_crm

# 3. Migrate site to build DocTypes & Reports
bench --site stock_market.local migrate
```

### Option 2: Deploy on Frappe Cloud
1. Push this repository to GitHub.
2. Go to **Frappe Cloud** $\rightarrow$ Apps $\rightarrow$ Install custom app via GitHub URL.
3. Select your site and click **Install**.

---

## 📁 Directory Architecture

```
stock_crm/
├── README.md                           # Documentation & Deploy Guide
├── setup.py                            # Python Package Setup
├── hooks.py                            # App Configuration Hooks
├── modules.txt                         # App Modules
└── stock_crm/
    ├── doctype/                        # Custom DocTypes (Data Models)
    │   ├── unlisted_stock/             # Stock Master Registry
    │   ├── counterparty_profile/       # Client & Broker Directory
    │   ├── counterparty_bank_account/  # Child DocType for Banks
    │   ├── company_receiving_bank/     # Kotak Company Bank Master
    │   └── unlisted_deal_ledger/       # Transaction Engine & JS/Py Calculators
    ├── report/                         # Executive Financial Reports
    │   ├── executive_mis_ca_audit/     # P&L & 27EQ Tax Summary
    │   ├── scrip_profitability/        # Margin Analysis per Stock
    │   ├── counterparty_settlement_ledger/ # Demat & Payout Tracking
    │   └── agent_performance/          # Agent Performance Incentives
    └── print_format/
        └── deal_confirmation_note/     # 1-Click PDF Deal Note Jinja Template
```

---

## 🛡️ License

MIT License - Free for commercial use and customization.
