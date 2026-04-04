# DEX Reporting Guide

## What Is DEX?

DEX (Data Exchange) is the reporting framework operated by the Department of Social Services (DSS) for collecting data about community services delivered with DSS funding. Providers who receive funding through DSS programs — including Home Care, the Commonwealth Home Support Programme (CHSP), and some NDIS-related programs — are required to submit DEX data each reporting period.

DEX data is used by the government to understand the reach and effectiveness of community services across Australia. Non-compliance with DEX reporting obligations can put your DSS funding at risk.

## Who Must Report

You must submit DEX data if your organisation receives funding from DSS programs including:

- Commonwealth Home Support Programme (CHSP)
- Home Care Packages (HCP) — via the My Aged Care system which links to DEX
- Family and community services funded by DSS
- Specialist homelessness services
- Some NDIS programs where DSS co-funding applies

If you are unsure whether your funding agreement requires DEX reporting, check your funding agreement or contact your DSS state office.

## What Data Is Collected

DEX collects three main categories of information:

**Service outlet information**
Your registered service outlets — the locations or programs through which you deliver services — must be registered in DEX before you can submit data for them.

**Session data**
Every funded service session must be recorded. A session is a single instance of service delivery to a client. You record the client identifier (SLK — see below), the date, the service type, and the duration or unit of service.

**Client outcome data (SCORE)**
Outcome measurements for each client at the start and end of each reporting period. See the SCORE Requirements document for full detail.

## Reporting Periods

DEX operates on two reporting periods per year:

| Period | Dates | Submission Due |
|--------|-------|----------------|
| Period 1 | 1 January – 30 June | Mid-July |
| Period 2 | 1 July – 31 December | Mid-January |

Missing a submission deadline will trigger a compliance query from your DSS funding manager and may affect future funding allocations.

## The SLK — Statistical Linkage Key

DEX does not use real client names. Instead, every client is identified by a Statistical Linkage Key (SLK) — a de-identified code derived from the client's personal information.

**How to calculate an SLK:**

The SLK is constructed from:
1. Characters 2 and 3 of the client's given name (first name)
2. Characters 2, 3, and 5 of the client's family name (surname)
3. Date of birth in DDMMYYYY format
4. Gender code (1=Male, 2=Female, 3=Other/Unknown)

**Example:**
- Given name: Margaret → take characters 2 and 3 → AR
- Family name: Thompson → take characters 2, 3, and 5 → HOP
- DOB: 15 March 1952 → 15031952
- Gender: Female → 2
- SLK: **ARHOP150319522**

If a client has a name shorter than required, use 9 (numeric) as a placeholder for missing characters.

The SLK must be calculated correctly and consistently for the same client across all sessions. Incorrect SLKs mean the data cannot be linked and will fail DEX validation.

## Outlet Registration

Before you can submit session data, every service outlet where you deliver the funded service must be registered in the DEX portal. An outlet can be a physical location, a mobile service, or a specific program. Contact DSS if you need to add or update outlets.

## XML Submission Format

DEX data is submitted as an XML file via the DSS Data Exchange portal. The XML must conform to the DSS schema. Errors in the XML structure will cause the entire submission to be rejected.

Providers can prepare DEX submissions manually using the DEX portal's data entry screens (suitable for very small organisations) or by uploading an XML file (required for providers with large volumes of clients and sessions).

## Consequences of Non-Compliance

- DSS compliance query and request for explanation
- Requirement to resubmit corrected data
- Potential withholding of future funding payments
- In serious or repeated cases, funding agreement review or termination

## How SupportIQ Automates DEX Reporting

SupportIQ captures all the data needed for DEX compliance as part of normal service delivery. Session data is collected automatically from shift records. SCORE data is captured by support workers via the mobile app at the start and end of each reporting period. SupportIQ calculates SLKs automatically from client records. At the end of each reporting period, the system generates a validated DEX XML file ready for submission to the DSS portal.