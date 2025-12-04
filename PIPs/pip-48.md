---
pip: 48
title: Native On-Chain Key Delegation (Single-Slot)
author: Johan (@johan256x)
status: Draft
type: Standards Track
category: Core
discussion-no: 271
created: 2025-11-27
---

## Abstract

This PIP introduces a native **On-Chain Key Delegation** mechanism to Pactus.
It allows an account to register a single secondary public
 key—the **Delegated Key**—stored directly in the account's state.

This protocol modifies the Account structure to include a "Delegation Slot".
This slot holds:  

1. The Delegated Public Key.
2. A **Spendable Allowance** (budget).
3. An Expiration Height.

This model functions like a **prepaid debit card**: the mobile wallet holds a
 limited key that draws from the main account's
 balance but is strictly capped by the allowance stored on-chain.
If the key is compromised, the loss is limited to the remaining allowance.

## Motivation

### The "Bank Account vs. Debit Card" Problem

Currently, a Pactus wallet requires the full private key (Seed) to sign
 transactions.
This poses a security risk for mobile or browser wallets: if the device
 is compromised, the entire fund is lost.

We need a separation of concerns similar to traditional banking:

* **The Vault (Primary Account):** Holds the life savings. Access is rare,
 highly generated (Cold Storage/Desktop), and requires maximum security.
* **The Card (Delegated Key):** Used daily for coffee or small transfers.
 Has a spending limit. If lost, the vault remains safe.

Delegated Keys deliberately restrict functionality to **small,
 everyday payments**.
They are not intended for validator operations or account management.

### Solution

This PIP enables this model natively:  

1. **Safety:** The seed phrase never leaves the secure desktop/cold wallet.
2. **Control:** The primary account sets a strict budget (e.g., 500 PAC).
3. **Simplicity:** Mobile apps only need to store the delegated private
 key and the primary address.

## Specification

### 1. State Modification

The Pactus `Account` data structure is modified to include a dedicated
 delegation slot. This prevents state bloat by allowing only **one**
 delegated key per account.

```go  
type Account struct {
    Address  Address
    Balance  int64
    Sequence int32

    // --- New Delegation Slot ---
    DelegateKey       PublicKey // The authorized secondary key (BLS)
    DelegateAllowance int64     // The remaining budget (in NanoPAC)
    DelegateExpiry    int32     // Block height at which delegation expires
}
```

### 2. Management Transaction (SetDelegation)

A new transaction payload type is introduced to manage the delegation slot.
 Only the **Primary Account Key** can sign this transaction.

**Payload:** SetDelegation

* DelegateKey: The new BLS Public Key to authorize.
* Allowance: The amount to authorize (sets the budget).
* Expiry: The block height validity limit (e.g., current + 1 year).

**Behavior:**

* This transaction **overwrites** the existing slot data.
* **To Activate:** Set valid key and positive allowance.
* **To Top-Up (Recharge):** Send a new tx with the same key but a
 refreshed allowance.
* **To Revoke:** Send a tx with a zero allowance or null key.

### 3. Spending Transaction (Delegated Action)

When a transaction is signed by the **Delegated Key**, the protocol validates
 it differently:

1. **Signature Check:** The signature must match Account.DelegateKey.
2. **Expiry Check:** CurrentBlockHeight must be < Account.DelegateExpiry.
3. **Allowance Check:** TransactionAmount + Fee must be <=
 Account.DelegateAllowance.

State Update:
If valid, the transaction is executed, and Account.DelegateAllowance is
 decremented by the total spent amount.
 The Account.Balance is reduced as usual.

Note that `DelegateAllowance` is a hard upper bound, not a guarantee of
 available funds:
 the actual spendable amount is still limited by the account's current
 `Balance`.

### Allowed Operation Types

Delegated Keys are restricted to **Transfer transactions only**.
A Delegated Key **MUST NOT** be permitted to sign or authorize:

* Bond
* Unbond
* Withdraw
* Validator-related actions
* Any other message type

Any non-Transfer transaction signed by the Delegated Key MUST be
 rejected by the protocol.

## Developer Guide & Workflow

This section illustrates how wallet developers can utilize this feature.

### Scenario: "Alice and her Mobile Wallet"

**Step 1:** Setup (Desktop Wallet)  
Alice creates a random keypair on her PC. This will be the delegated key.
She sends a SetDelegation transaction from her Main Account:

* DelegateKey: <Mobile_Public_Key>  
* Allowance: 100 PAC  
* Expiry: Block #500,000

**Step 2:** Transport (QR Code)  
Alice's Desktop Wallet displays a QR Code containing:
{ "secret": "<Mobile_Private_Key>", "address": "<Main_Account_Address>" }

**Step 3:** Mobile Usage  
Alice scans the QR code with her Pactus Mobile App.

* The App **does not** know the Main Seed.  
* The App stores <Mobile_Private_Key>.

**Step 4:** Buying Coffee (The Transaction)  
Alice buys a coffee for 5 PAC.  
The App constructs a standard Transfer transaction:

* **Sender:** <Main_Account_Address>  
* **Signer:** <Mobile_Private_Key>

**Step 5:** On-Chain Validation  
Nodes see the sender is Main Account but the signer is the Mobile Key.

* Nodes check: Is Mobile Key authorized? **Yes.**  
* Nodes check: Is 5 PAC <= 100 PAC Allowance? **Yes.**  
* **Result:** Transfer successful.  
* **New State:** Allowance is now 95 PAC.

## Rationale

### Why Single-Slot?

By limiting each account to one delegate, we eliminate the risk
 of "State Bloat" (spamming the chain with millions of unused allowances).
 It keeps the protocol lightweight and performant.

### Why Stateful Allowance?

A previous draft considered a stateless "Max per Transaction" limit.
 However, this allowed "draining attacks" (e.g., sending 100 transactions
 of 1 PAC rapidly).
 The **Allowance** model (Stateful) provides strict security: the
 delegated key can never spend more than the budget, regardless
 of the number of transactions.

### Why Transfers-Only?

Delegated Keys target mobile use cases where users typically need
 to perform small payments.  
Restricting delegated operations to Transfers only minimizes attack
 surface and ensures that all account-management and validator-related
 actions remain exclusively under the Primary Account Key.

### Comparison

* **XRP Ledger:** Similar to the "Regular Key" concept (single slot
 for key rotation/management).  
* **Ethereum (ERC-20):** Similar to the approve() mechanism, where a
 spender has a specific allowance that decreases over time.

## Backward Compatibility

* **Node Upgrade:** This is a hard-fork change. Old nodes will reject
 transactions signed by keys other than the primary key.  
* **Wallet Compatibility:** Existing wallets continue to work using
 the Primary Key. They simply ignore the delegation slot fields
 until updated.

## Security Considerations

1. **Compromise Scope:** If the Delegated Key is stolen, the attacker
 can only spend the DelegateAllowance. The Main Balance remains untouched.
2. **Revocation & Recovery:** Revocation is instant. The Primary
 Owner simply sends a `SetDelegation` transaction with a
 **newly generated `DelegateKey`** (to rotate keys) or with
 `Allowance = 0` (to disable delegation).
  This overwrites the compromised key immediately, allowing the
  user to restore access without needing to move funds from the Primary Account.
3. **Expiry Safety:** If the mobile device is lost and forgotten,
 the key automatically becomes invalid after the expiry block,
 protecting against future exploits.

## Test Cases

TBD

## Reference Implementation

Pending

## References

* PIP-1: Pactus Improvement Proposal Process
* Cosmos SDK x/authz module (Grant/Allowance concepts)
* XRP Ledger SetRegularKey transaction structure
