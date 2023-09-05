---
pip: 1
title: PIP Purpose and Guidelines
status: Living
type: Meta
author: Javad Rajabzadeh (ja7ad@live.com)
created: 2023-07-10
---

## What is an PIP?

Pactus Improvement Proposals (PIPs) serve as a comprehensive framework for outlining and defining the standards 
for the Pactus platform's ongoing development and enhancement. These proposals cover various aspects of the platform, 
including core protocol specifications and client application programming interfaces (APIs). By establishing a clear 
and consistent set of guidelines, PIPs ensure seamless interoperability and extensibility across the Pactus ecosystem, 
fostering a robust and efficient environment for developers and users alike.

## PIP Rationale

We intend PIPs to be the primary mechanisms for proposing new features, for collecting community technical input on an issue, and for documenting the design decisions that have gone into Pactus. Because the PIPs are maintained as text files in a versioned repository, their revision history is the historical record of the feature proposal.

For Pactus implementers, PIPs are a convenient way to track the progress of their implementation. Ideally, each implementation maintainer would list the PIPs that they have implemented. This will give end users a convenient way to know the current status of a given implementation or library.

## PIP Types

There are three types of PIP:

Standards Track PIP: Describes any change that affects most or all Pactus implementations, such as—a change to the network protocol, a change in block or transaction validity rules, proposed application standards/conventions, or any change or addition that affects the interoperability of applications using Pactus. Standards Track PIPs consist of three parts—a design document, an implementation, and (if warranted) an update to the formal specification. Furthermore, Standards Track PIPs can be broken down into the following categories:

Core: Improvements requiring a consensus fork, as well as changes that are not necessarily consensus critical but may be relevant to "core dev" discussions.
Networking: Includes improvements around devp2p and Light Pactus Subprotocol, as well as proposed improvements to network protocol specifications of whisper and swarm.
Interface: Includes improvements around client API/RPC specifications and standards. The label "interface" aligns with the interfaces repo, and discussion should primarily occur in that repository before a PIP is submitted to the PIPs repository.
PRC: Application-level standards and conventions, including contract standards such as token standards, name registries, URI schemes, library/package formats, and wallet formats.
Meta PIP: Describes a process surrounding Pactus or proposes a change to (or an event in) a process. Process PIPs are like Standards Track PIPs but apply to areas other than the Pactus protocol itself. They may propose an implementation, but not to Pactus's codebase; they often require community consensus; unlike Informational PIPs, they are more than recommendations, and users are typically not free to ignore them. Examples include procedures, guidelines, changes to the decision-making process, and changes to the tools or environment used in Pactus development. Any meta-PIP is also considered a Process PIP.

Informational PIP: Describes a Pactus design issue, or provides general guidelines or information to the Pactus community, but does not propose a new feature. Informational PIPs do not necessarily represent Pactus community consensus or a recommendation, so users and implementers are free to ignore Informational PIPs or follow their advice.

It is highly recommended that a single PIP contain a single key proposal or new idea. The more focused the PIP, the more successful it tends to be. A change to one client doesn't require a PIP; a change that affects multiple clients, or defines a standard for multiple apps to use, does.

A PIP must meet certain minimum criteria. It must be a clear and complete description of the proposed enhancement. The enhancement must represent a net improvement. The proposed implementation, if applicable, must be solid and must not complicate the protocol unduly.

## PIP Status Terms

We have many status terms to finalize your proposal for implementation in the Pactus blockchain.

```mermaid!
graph TD
  subgraph Idea
    A1[Idea]
    style A1 fill:#FF5733
  end

  subgraph Draft
    B1[Draft]
    style B1 fill:#FACB32
  end

  subgraph Review
    C1[Review]
    style C1 fill:#32A852
  end

  subgraph LastCall
    D1[Last Call]
    style D1 fill:#32A8A2
  end

  subgraph Final
    E1[Final]
    style E1 fill:#32A8D6
  end

  subgraph Stagnant
    F1[Stagnant]
    style F1 fill:#757575
  end

  subgraph Withdrawn
    G1[Withdrawn]
    style G1 fill:#D63232
  end

  subgraph Living
    H1[Living]
    style H1 fill:#32D659
  end

  A1 -->|Idea Proposed| B1
  B1 -->|Draft Created| C1
  C1 -->|Ready for Review| D1
  D1 -->|Approved| E1
  D1 -->|Revert to Review| C1
  C1 -->|Stagnant| F1
  F1 -->|Revived| B1
  B1 -->|Withdrawn| G1
  C1 -->|Withdrawn| G1
  D1 -->|Withdrawn| G1
  E1 -->|Errata or Clarifications| E1
  B1 -->|Ongoing Updates| H1
  E1 -->|Ongoing Updates| H1
  F1 -->|Idea Pursued Later| B1
  F1 -->|Idea Pursued Later| C1
  F1 -->|Idea Pursued Later| D1
  F1 -->|Idea Pursued Later| E1
  F1 -->|Idea Pursued Later| H1
```

1. **Idea:**  
   - Initial idea for an improvement.
   - Not tracked within the PIP Repository.
   - Typically a pre-draft stage.

2. **Draft:**  
   - The first formally tracked stage of a PIP in development.
   - Author creates a draft PIP.
   - It is merged into the PIP repository when properly formatted.

3. **Review:**  
   - Author marks a PIP as ready for peer review.
   - Open for review by peers and experts.
   - Authors gather feedback and make necessary revisions.

4. **Last Call:**  
   - Final review window before moving to FINAL.
   - An editor assigns Last Call status and sets a review end date.
   - Typically, the Last Call period is around 14 days.
   - If significant changes are needed, it can revert to the Review status.

5. **Final:**  
   - Represents the final standard.
   - In a state of finality and should only be updated to correct errors or add non-normative clarifications.
   - Essentially, it's the approved version.

6. **Stagnant:**  
   - PIPs in Draft or Review become stagnant if inactive for 6 months or more.
   - They are moved to this state.
   - Authors or PIP editors can move them back to Draft if they wish to work on them again.

7. **Withdrawn:**  
   - The PIP author(s) decide to withdraw the proposal.
   - It has finality and cannot be resurrected using the same PIP number.
   - If the idea is revisited later, it's considered a new proposal.

8. **Living:**  
   - A special status for PIPs designed to be continually updated.
   - They don't reach a state of finality.
   - Often used for documents that need ongoing maintenance.
