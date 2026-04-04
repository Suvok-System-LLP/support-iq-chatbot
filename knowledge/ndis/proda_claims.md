# NDIS PRODA Claims

## What Is PRODA?

PRODA (Provider Digital Access) is the Australian Government's identity verification and access management system that gives NDIS registered providers access to the myplace provider portal — the system where payment requests (claims) are submitted to the NDIA.

Every NDIS provider must have an active PRODA account to submit claims. Individual staff members who manage billing must also have their own PRODA accounts linked to the organisation.

## Step-by-Step Claim Submission

**Step 1 — Deliver the service**
Complete the shift, session, or support activity. Record the details: participant, date, start time, end time, support type delivered, worker.

**Step 2 — Create the payment request**
Compile the required information for each claim:
- Participant's NDIS number (7-digit number)
- Your provider registration number
- Support item code from the NDIS Support Catalogue
- Date of service
- Quantity (hours, sessions, or kilometres depending on the item)
- Unit price (must not exceed the price guide limit)
- Total amount

**Step 3 — Submit via PRODA or approved software**
Claims can be submitted directly in the myplace portal or via an approved software integration. SupportIQ submits directly via the NDIS API, which means claims go through without manual data entry in PRODA.

**Step 4 — NDIA processing**
The NDIA processes payment requests within 3 business days. Most straightforward claims are processed faster, often overnight. Claims with errors are rejected and returned with an error code.

**Step 5 — Payment**
Once approved, payment is deposited into the provider's nominated bank account. Providers can view payment status in the myplace portal.

## Required Fields on Every Claim

Missing or incorrect data in any of these fields will cause rejection:

| Field | Notes |
|-------|-------|
| NDIS participant number | Must match exactly — no hyphens, no spaces |
| Provider registration number | Must be current and registered for the support category |
| Support item code | Must be from the current Support Catalogue |
| Service date | Must fall within the participant's plan dates |
| Quantity | Hours for time-based items, correct unit for other items |
| Unit price | Must not exceed current price guide limit |

## Common Error Codes and What They Mean

**E001 — Plan not current for service date**
The participant's plan does not cover the date you are billing for. The plan may have expired, or the service was delivered before the plan start date. Check the participant's plan dates and resubmit for dates within the plan period.

**E002 — Support item not in participant's plan**
The support item code you are billing for is not funded in this participant's plan. Either the participant does not have this support approved, or you are using the wrong support category. Review the participant's plan and confirm the support is funded.

**E003 — Rate exceeds price guide maximum**
Your unit price is above the current price guide limit for this support item. Update the rate to the current maximum and resubmit.

**E004 — Provider not registered for this support category**
Your organisation is not registered to deliver this type of support. Check your NDIS provider registration and the support categories it covers.

**E005 — Duplicate payment request**
A claim for this participant, support item, date, and quantity has already been processed. Check your records before resubmitting.

## Bulk Submissions

Providers with many participants can submit multiple claims in a single batch upload using a CSV template from the myplace portal. Bulk submission is efficient but errors in one row can affect the entire batch — always validate the file before uploading.

## The PACE System

The NDIA is progressively migrating participants to its new PACE system (replacing the previous myplace system). PACE changes some aspects of how plans are structured and how claims are categorised. SupportIQ is PACE-ready — providers do not need to make any cha
