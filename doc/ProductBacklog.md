# Product Backlog

## 1. Introduction

The Product Backlog contains the functional requirements and planned features of Pricey, organized into Epics and User Stories.

The backlog is an evolving document and may be updated throughout the development process as requirements are refined or new needs are identified.

Each User Story describes a feature from the perspective of the user and is accompanied by Acceptance Criteria defining the conditions that must be satisfied for the User Story to be considered complete.

The development process is organized into iterations (Sprints), with User Stories selected from the Product Backlog according to their priority and dependencies.

---

## 2. Epics

| ID  | Epic                 | Description                                                                                                   |
| --- | -------------------- | ------------------------------------------------------------------------------------------------------------- |
| E01 | Product Search       | Allows users to search for products and obtain relevant offers.                                               |
| E02 | Search and Filtering | Allows users to refine product searches according to specific criteria.                                       |
| E03 | Price Monitoring     | Allows users to select products and sites to monitor and periodically track their prices.                     |
| E04 | Notifications        | Allows users to receive notifications when monitored prices decrease according to their configured threshold. |
| E05 | User Management      | Allows users to create and manage their Pricey account.                                                       |

---
<br>

# 3. User Stories

## E01 - Product Search

### US-01 - Search for a Product

**As a** user
**I want** to search for a product by name or model
**so that** I can find where the product is available and compare its prices.

#### Acceptance Criteria

* [ ] The user can enter the name or model of a product.
* [ ] The user can submit the search.
* [ ] Pricey identifies the product corresponding to the search.
* [ ] Pricey searches for the product on the configured websites.
* [ ] Results that do not correspond to the requested product are excluded.

**Priority:** High

---

### US-02 - View Search Results

**As a** user
**I want** to view the products found by Pricey
**so that** I can compare their availability and prices across different websites.

#### Acceptance Criteria

* [ ] The user can view the websites where the product is available.
* [ ] The price associated with each result is displayed.
* [ ] Each result is associated with the corresponding website.
* [ ] Only relevant and available products are displayed.

**Priority:** High

---

## E02 - Search and Filtering

### US-03 - Filter Search Results

**As a** user
**I want** to specify additional product parameters
**so that** I can restrict the search to products matching my requirements.

#### Acceptance Criteria

* [ ] The user can specify additional search parameters.
* [ ] Pricey applies the specified parameters to the search results.
* [ ] Results that do not satisfy the specified parameters are excluded.
* [ ] The user can perform a search without specifying additional parameters.

**Priority:** Medium

---

### US-04 - Set a Maximum Price

**As a** user
**I want** to specify a maximum price
**so that** I can exclude products that exceed my budget.

#### Acceptance Criteria

* [ ] The user can specify a maximum acceptable price.
* [ ] Results exceeding the specified price are excluded.
* [ ] The user can perform a search without specifying a maximum price.
* [ ] The maximum price is applied consistently to the search results.

**Priority:** Medium

---

## E03 - Price Monitoring

### US-05 - Select Sites to Monitor

**As a** user
**I want** to select one or more websites from the search results
**so that** Pricey can monitor the corresponding prices.

#### Acceptance Criteria

* [ ] The user can select one or more websites from the available results.
* [ ] The selected websites are associated with the corresponding product.
* [ ] The user can view which websites are currently being monitored.
* [ ] The user can stop monitoring a previously selected website.

**Priority:** High

---

### US-06 - Monitor Multiple Products

**As a** user
**I want** to monitor multiple products simultaneously
**so that** I can track different products from a single account.

#### Acceptance Criteria

* [ ] The user can add multiple products to their monitored products.
* [ ] Each monitored product is associated with the corresponding user.
* [ ] Each product can have its own monitored websites.
* [ ] The user can view the list of products currently being monitored.
* [ ] The user can stop monitoring a product.

**Priority:** High

---

### US-07 - Periodically Check Prices

**As** a user
**I want** Pricey to periodically check the prices of the products I am monitoring
**so that** I do not have to manually check the websites.

#### Acceptance Criteria

* [ ] Pricey periodically checks the selected websites.
* [ ] The current price of each monitored product is retrieved.
* [ ] Pricey stores or otherwise maintains the information required to compare prices over time.
* [ ] A price change can be identified by comparing the current price with the relevant previous price.

**Priority:** High

---

### US-08 - Configure Monitoring Preferences

**As** a user
**I want** to configure the preferences associated with a monitored product
**so that** I can customize how that product is monitored.

#### Acceptance Criteria

* [ ] The user can configure the monitoring preferences for a product.
* [ ] Preferences are associated with the specific user-product relationship.
* [ ] Different monitored products can have different preferences.
* [ ] The configured preferences are used during price monitoring.

**Priority:** Medium

---

## E04 - Notifications

### US-09 - Configure Price Drop Threshold

**As** a user
**I want** to configure the minimum percentage decrease required to trigger a notification
**so that** I only receive notifications for price decreases that are relevant to me.

#### Acceptance Criteria

* [ ] The default price drop threshold is 5%.
* [ ] The user can modify the threshold.
* [ ] The configured threshold is associated with the corresponding monitored product.
* [ ] The configured threshold is used when evaluating price changes.

**Priority:** High

---

### US-10 - Detect a Relevant Price Decrease

**As** a user
**I want** Pricey to detect when the price of a monitored product decreases by at least my configured threshold
**so that** I can be notified when a relevant price change occurs.

#### Acceptance Criteria

* [ ] Pricey compares the current price with the relevant previous price.
* [ ] Pricey calculates whether the price decrease meets the configured threshold.
* [ ] A notification event is generated when the threshold is reached or exceeded.
* [ ] No notification event is generated when the decrease is below the configured threshold.

**Priority:** High

---

### US-11 - Receive a Price Drop Notification

**As a** user
**I want** to receive a notification when a monitored product reaches my configured price drop threshold
**so that** I can take advantage of the price decrease.

#### Acceptance Criteria

* [ ] The user receives a notification when the configured threshold is reached or exceeded.
* [ ] The notification identifies the monitored product.
* [ ] The notification identifies the relevant website.
* [ ] The notification includes the relevant price information.
* [ ] Notifications are only sent for monitored products.

**Priority:** High

---

## E05 - User Management

### US-12 - Create an Account

**As a** user
**I want** to create a Pricey account
**so that** I can save and manage my monitored products and preferences.

#### Acceptance Criteria

* [ ] The user can provide the information required for registration.
* [ ] Pricey validates the registration data.
* [ ] A user account is created when the provided data is valid.
* [ ] The user cannot register using credentials that are already associated with another account.

**Priority:** High

---

### US-13 - Log In

**As a** registered user
**I want** to log in to my Pricey account
**so that** I can access my monitored products and preferences.

#### Acceptance Criteria

* [ ] The user can provide their login credentials.
* [ ] Pricey validates the provided credentials.
* [ ] The user can access their account when the credentials are valid.
* [ ] Access is denied when the credentials are invalid.

**Priority:** High

---
<br>

# 4. MVP Scope

The Minimum Viable Product (MVP) consists of the minimum set of features required to provide the core Pricey functionality.

The initial MVP includes:

* Product search.
* Search result visualization.
* Search filtering.
* Maximum price filtering.
* Selection of websites to monitor.
* Monitoring of multiple products.
* Periodic price checking.
* Configurable price drop threshold.
* Detection of relevant price decreases.
* Price drop notifications.
* User registration and authentication.

The MVP is intended to provide a complete end-to-end workflow:

> Search for a product → view available offers → select offers to monitor → periodically check prices → receive a notification when a relevant price decrease occurs.

The exact implementation of each feature may evolve during development.

---
<br>

# 5. Future Developments

The following features are not currently part of the MVP and may be considered in future iterations:

* Advanced product identification and matching using Machine Learning or Artificial Intelligence.
* Automatic identification of equivalent products across different websites.
* Support for additional e-commerce websites and marketplaces.
* Assessment of website or seller reliability.
* User-defined preferred websites.
* More advanced product and price filters.
* Historical price analysis and visualization.
* Price trend analysis.
* Additional notification channels.
* Personalized recommendations.

These items are considered potential future developments and are not binding requirements for the current development scope.

---
<br>

# 6. Backlog Management

The Product Backlog is managed through GitHub Projects.

User Stories are represented as GitHub Issues and are moved through the following workflow:

```text
Todo → In Progress → Done
```

The Product Backlog defines the functional scope of the project, while GitHub Projects is used to manage the development progress and Sprint planning.

Technical implementation tasks may be created as subtasks within the corresponding User Story Issue.

---
<br>

# 7. Definition of Done

A User Story can be considered **Done** when:

* [ ] All Acceptance Criteria are satisfied.
* [ ] The required functionality has been implemented.
* [ ] Relevant automated tests have been implemented and pass successfully.
* [ ] The implementation does not introduce known regressions.
* [ ] The code has been reviewed or self-reviewed.
* [ ] Relevant documentation has been updated.
* [ ] The changes have been committed to the repository.
