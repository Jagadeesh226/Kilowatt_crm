# WooCommerce CRM --- Evidence-Based AI Customer Intelligence

## 1. Problem Statement

WooCommerce businesses collect customer and order data, but turning that
data into timely, relevant customer follow-ups often requires manual
work. A basic CRM can display orders; a more useful CRM explains which
customers need attention, why they are relevant now, and what product or
message may fit their actual purchase history.

**Proposed solution:** Build a WooCommerce-integrated CRM that
centralizes customers and orders, calculates transparent customer
segments, and generates evidence-based next-best-action recommendations
using previous purchases, recency, seasonality, and current business
context.

## 2. Objectives

-   Centralize customer profiles, order history, purchase frequency, and
    spending.
-   Track order status and show customer-level purchase context.
-   Identify customer segments using deterministic, explainable rules.
-   Recommend relevant products or campaigns from prior orders and a
    time-aware seasonal calendar---not random LLM guesses.
-   Generate personalized, editable communication drafts for human
    review.
-   Keep the hackathon demo functional with clearly labelled synthetic
    data when a store is unavailable.

## 3. Core Features

  -----------------------------------------------------------------------
  Feature                             What it does
  ----------------------------------- -----------------------------------
  Customer dashboard                  Customer/order totals, eligible
                                      revenue, segment counts and
                                      follow-up queue.

  Customer 360°                       Profile, order history, spending,
                                      purchase recency, repeat purchases
                                      and communications.

  Order tracking                      Order ID, status, amount, date and
                                      line items synchronized from
                                      WooCommerce or demo data.

  Explainable segmentation            Rule-based new, repeat, high-value,
                                      at-risk and inactive groups, with
                                      reasons shown.

  AI next-best action                 Evidence-grounded recommendation,
                                      relevant product category/campaign,
                                      explanation and message draft.

  Seasonal intelligence               Uses a configured festival/season
                                      calendar and lead time, together
                                      with relevant historical purchase
                                      categories.
  -----------------------------------------------------------------------

## 4. Technology Stack

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Frontend                React + Vite            CRM dashboard and
                                                  customer views.

  Backend                 Python + FastAPI        REST APIs, metrics,
                                                  rules and AI
                                                  orchestration.

  Database                PostgreSQL + SQLAlchemy Normalized customer,
                                                  order and communication
                                                  records.

  E-commerce              WooCommerce REST API    Customer/order import
                                                  when credentials and a
                                                  reachable store are
                                                  available.

  AI                      LLM API                 Explains verified facts
                                                  and drafts
                                                  recommendations; does
                                                  not invent metrics.
  -----------------------------------------------------------------------

## 5. System Architecture

React calls FastAPI REST endpoints. FastAPI reads normalized records
from PostgreSQL, calculates authoritative metrics and segments,
retrieves relevant order/category evidence, checks the seasonal
calendar, then calls an LLM to explain the evidence and draft a
suggested action. A demo data provider and a WooCommerce provider share
the same internal data format.

  -----------------------------------------------------------------------
  Component                           Responsibility
  ----------------------------------- -----------------------------------
  React frontend                      Dashboard, customer search,
                                      customer profile, order history and
                                      insight panel.

  FastAPI                             API validation, segmentation,
                                      candidate selection, seasonal
                                      matching and AI orchestration.

  PostgreSQL                          Stores normalized customers,
                                      orders, order items,
                                      campaigns/calendar entries and
                                      communication drafts.

  WooCommerce adapter                 Imports customer/order data; sync
                                      can be manual for the MVP. Webhooks
                                      are a later enhancement.

  Recommendation engine               Builds a factual evidence bundle
                                      from purchase history, recency,
                                      seasonality, inventory and campaign
                                      rules.

  LLM                                 Converts the evidence bundle into a
                                      clear explanation and draft; output
                                      is validated and reviewed by a
                                      human.
  -----------------------------------------------------------------------

## 6. Database Design

  ------------------------------------------------------------------------
  Table                   Important fields         Purpose
  ----------------------- ------------------------ -----------------------
  `customers`             `id` PK,                 Customer profile;
                          `wc_customer_id`         supports guest
                          unique/nullable, `name`, checkouts without a
                          `email`, `phone`,        WooCommerce customer
                          `created_at`             ID.

  `orders`                `id` PK, `wc_order_id`   Order history and
                          unique, `customer_id`    recency metrics.
                          FK/nullable, `status`,   
                          `total`, `currency`,     
                          `ordered_at`             

  `order_items`           `id` PK, `order_id` FK,  Evidence for prior
                          `wc_product_id`,         product/category
                          `product_name`,          interest.
                          `category`, `quantity`,  
                          `unit_price`             

  `campaign_calendar`     `id` PK, `name`,         Configured seasonal
                          `start_date`,            events, dates, relevant
                          `end_date`, `lead_days`, categories and
                          `eligible_categories`,   promotion rules.
                          `region`                 

  `communications`        `id` PK, `customer_id`   Draft and communication
                          FK, `order_id` nullable, history.
                          `channel`, `message`,    
                          `status`, `created_at`   
  ------------------------------------------------------------------------

### Data integrity rules

-   Use WooCommerce IDs as external identifiers and enforce uniqueness
    to prevent duplicate imports.
-   Calculate spend and order counts in code from eligible orders;
    handle cancelled, failed and refunded orders consistently.
-   Support guest orders; do not assume every order maps to a registered
    account.
-   Keep API secrets on the backend and outside source control.

## 7. Evidence-Based, Time-Aware Recommendations

**Core rule:** The system must not recommend products merely because an
LLM thinks they sound suitable. Every recommendation must be supported
by customer purchase evidence and a valid current context.

### Recommendation pipeline

1.  **Build customer evidence:** Retrieve recent and repeated purchases,
    product categories, order dates, frequency, spend and any explicit
    preferences the customer has provided.
2.  **Generate eligible candidates:** Select products/categories related
    to previous purchases or configured complementary items. Exclude
    unavailable products and campaigns that are not active.
3.  **Apply time context:** Compare the current date with a maintained
    festival/season calendar and its configured lead time. Use the
    customer's market/region only when known or explicitly configured.
4.  **Rank with transparent rules:** Combine purchase-category match,
    recency/frequency, seasonal relevance, stock/eligibility, and
    campaign timing. Show the reasons and evidence.
5.  **Use AI for explanation:** Send the selected candidates and factual
    evidence to the LLM to draft a natural recommendation. The LLM
    cannot add unsupported purchase facts, discounts or product
    availability.
6.  **Review and log:** Show the reason, evidence, confidence/coverage,
    and editable message. Require human approval before sending.

### Example: Navaratri clothing recommendation

A customer previously bought ethnic wear or festive clothing. Navaratri
is approaching, and the configured seasonal calendar indicates that a
relevant campaign window is open. If the store currently has eligible
festive clothing in stock, the system may recommend that category and
draft a message.

It should explain: "Recommended because the customer previously
purchased ethnic wear and the Navaratri campaign window is active."

If the customer only bought unrelated products, the system should not
infer clothing interest; it should offer a weaker seasonal suggestion
only if a valid campaign and customer eligibility rule support it---or
recommend no outreach.

### Recommendation record should contain

  -----------------------------------------------------------------------
  Field                               Example / meaning
  ----------------------------------- -----------------------------------
  Reason                              Prior ethnic-wear purchase +
                                      upcoming configured Navaratri
                                      campaign.

  Evidence                            Relevant order IDs/categories and
                                      purchase dates; no unnecessary
                                      personal details.

  Timing                              Campaign start/end and lead-time
                                      window from the maintained
                                      calendar.

  Candidate                           Eligible in-stock festive clothing
                                      category or products from the store
                                      catalogue.

  Confidence/coverage                 High when both purchase and
                                      seasonal evidence exist;
                                      low/insufficient when evidence is
                                      missing.

  Action                              Draft message for review; do not
                                      send automatically by default.
  -----------------------------------------------------------------------

### Important safeguards

-   Maintain festival dates and regional relevance in a calendar; do not
    rely on model memory for changing dates.
-   Do not fabricate discounts, stock, product features, or purchase
    history. Use catalogue/inventory data if available.
-   If purchase data is sparse or the context is uncertain, say so and
    avoid a confident personalized recommendation.
-   Respect customer communication consent, opt-outs and applicable
    marketing rules.

## 8. Difference from CSC Business OS

  -----------------------------------------------------------------------
  Area                    CSC Business OS         WooCommerce CRM
  ----------------------- ----------------------- -----------------------
  Purpose                 Manage business         Manage e-commerce
                          services and            customers, orders and
                          operational jobs.       retention.

  Primary records         Documents, job IDs,     Customers, WooCommerce
                          service details and     orders,
                          workflow status.        products/categories,
                                                  purchase metrics and
                                                  communications.

  Triggers                Document intake, OCR    Order changes, purchase
                          extraction, job         history, inactivity and
                          creation and service    seasonal campaign
                          status.                 windows.

  AI role                 OCR/document            Evidence-based customer
                          understanding and       insights and time-aware
                          service workflow        product/campaign
                          assistance where        suggestions.
                          applicable.             

  Success measure         Reliable service        Relevant follow-ups,
                          processing and reduced  faster decisions and
                          manual operations.      potential improvement
                                                  in
                                                  retention/conversion.
  -----------------------------------------------------------------------

### Reusable from CSC Business OS

-   React dashboard patterns, FastAPI service structure,
    PostgreSQL/SQLAlchemy practices and API testing.
-   Workflow/status tracking, audit logs, error handling and message
    preview patterns.

### Do not copy blindly

-   OCR, RTO/insurance and service-job logic are not core requirements
    for this CRM.
-   Do not model WooCommerce orders as generic service jobs; preserve
    e-commerce order semantics.
-   The new differentiator is purchase-evidence + seasonality +
    next-best action, not just CRUD and AI chat.

## 9. Additional Differentiators

-   **Explainable recommendations:** Show "why this customer, why this
    product, why now" with order/category evidence.
-   **Customer 360°:** Profile, order history, spending, segment, and
    communication history in one view.
-   **Suppression rules:** Avoid repeated messages, recent-purchase
    outreach, out-of-stock recommendations, opted-out contacts and
    irrelevant categories.
-   **Campaign timing:** Recommend a suitable outreach window before a
    festival or seasonal event, not after the buying window has passed.
-   **Feedback loop:** Log draft approval, send status,
    clicks/conversions if available; later use results to evaluate which
    recommendations perform well.
-   **Natural-language CRM query (stretch):** Answer questions such as
    "Which repeat customers bought ethnic wear last year and have not
    purchased recently?" using validated database queries.

## 10. Hackathon Scope and 4--6 Hour Plan

  -----------------------------------------------------------------------
  Time                                Deliverable
  ----------------------------------- -----------------------------------
  0:00--0:30                          Bootstrap React, FastAPI and
                                      database.

  0:30--1:15                          Schema, realistic synthetic
                                      customers/orders/categories and
                                      core endpoints.

  1:15--2:30                          Dashboard, customer profile, order
                                      history and search.

  2:30--3:15                          Rule-based metrics/segments and
                                      evidence-based candidate selection.

  3:15--4:00                          Configured sample festival
                                      calendar, AI explanation/message
                                      draft and demo mode.

  4:00--6:00                          Integration if possible, test
                                      fallback paths, polish UI and
                                      rehearse.
  -----------------------------------------------------------------------

## 11. Demo Walkthrough

1.  **Show the problem:** Customer and order data alone do not tell a
    store owner who to contact or what to recommend.
2.  **Show customer evidence:** Open a customer profile and show
    relevant previous orders, product categories, dates and purchase
    metrics.
3.  **Show the timing context:** Open a configured upcoming seasonal
    campaign, such as Navaratri, with its dates and eligible product
    categories.
4.  **Generate a recommendation:** Show the reason---past relevant
    purchase plus active seasonal window---and display eligible
    products/categories if catalogue data is available.
5.  **Show the AI draft:** Present a personalized message, explain its
    evidence, allow editing, and copy it for review. Do not claim the
    message was sent if it was only drafted.

### Suggested pitch

> "Our CRM does more than display WooCommerce orders. It connects a
> customer's actual purchase history with the right time and relevant
> store offerings, then explains why a follow-up makes sense and
> prepares a reviewable message."

## 12. Risks and Limitations

-   This is a hackathon MVP, not a production-ready CRM.
-   When no real store is available, synthetic data must be clearly
    labelled. A live WooCommerce connection requires a reachable store
    and valid API credentials.
-   Seasonal event dates and campaign rules must be maintained and
    verified; do not rely on the LLM to calculate changing festival
    dates.
-   Actual product recommendations require product catalogue and
    preferably inventory/pricing data. Without these, recommend a
    category or campaign, not a specific product.
-   Authentication, role-based access, secure secret handling, webhook
    signature verification, retries, monitoring, privacy controls and
    consent management require further production work.

## References

-   [WooCommerce REST API
    v3](https://developer.woocommerce.com/docs/apis/rest-api/v3/)
-   [WooCommerce Webhooks](https://woocommerce.com/document/webhooks/)
